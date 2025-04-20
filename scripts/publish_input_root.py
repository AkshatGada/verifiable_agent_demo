#!/usr/bin/env python3
import os
import json
import hashlib
import argparse
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

from github_agent.identity import AGENT_DID, AGENT_KEY_PATH
from github_agent.utils.github_readme import fetch_and_hash

# Directory to store proofs
PROOFS_DIR = Path("proofs")
PROOFS_DIR.mkdir(exist_ok=True)


def issue_vc_cli(cred_json: str, key_path: str) -> str:
    """
    Issues a Verifiable Credential using the didkit CLI (vc-issue-credential).
    Reads the credential JSON from stdin and outputs the signed credential JSON.
    """
    cmd = ["didkit", "vc-issue-credential", "-k", key_path]
    try:
        result = subprocess.run(
            cmd,
            input=cred_json,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error issuing VC (exit {e.returncode}):", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)


def main():
    # Load environment variables and parse arguments
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Commit GitHub README inputRoot on-chain"
    )
    parser.add_argument(
        "repos", nargs="+", help="List of GitHub repo URLs"
    )
    args = parser.parse_args()

    RPC_URL = os.getenv("RPC_URL")
    OWNER_KEY = os.getenv("OWNER_KEY")
    REGISTRY_ADDR = os.getenv("REGISTRY_ADDR")
    if not (RPC_URL and OWNER_KEY and REGISTRY_ADDR):
        print("Error: set RPC_URL, OWNER_KEY, REGISTRY_ADDR in .env", file=sys.stderr)
        sys.exit(1)

    # Fetch and hash each README
    digests = []
    for url in args.repos:
        repo, _, digest = fetch_and_hash(url)
        print(f"  • {repo}: {digest}")
        digests.append(digest)

    # Compute the inputRoot (SHA-256 of sorted digests)
    input_root = hashlib.sha256("".join(sorted(digests)).encode()).hexdigest()
    print("Computed inputRoot:", input_root)

    # Build Verifiable Credential payload
    issuance_date = f"{__import__('datetime').datetime.utcnow().isoformat()}Z"
    cred = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "id": f"urn:inputroot:{input_root}",
        "type": ["VerifiableCredential", "InputRoot"],
        "issuer": AGENT_DID,
        "issuanceDate": issuance_date,
        "credentialSubject": {"inputRoot": input_root}
    }
    cred_json = json.dumps(cred)

    # Issue (sign) the credential
    print("Issuing Verifiable Credential via didkit CLI...")
    proof_json = issue_vc_cli(cred_json, AGENT_KEY_PATH)
    proof_path = PROOFS_DIR / f"inputRoot-{input_root}.json"
    proof_path.write_text(proof_json)
    print("Signed VC saved to", proof_path)

    # Publish inputRoot on-chain
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    acct = w3.eth.account.from_key(OWNER_KEY)
    owner = acct.address

    # Load the registry ABI
    abi_path = Path("artifacts/contracts/IdentityRegistry.sol/IdentityRegistry.json")
    if not abi_path.exists():
        print(f"Error: ABI not found at {abi_path}", file=sys.stderr)
        sys.exit(1)
    abi = json.load(abi_path.open())["abi"]
    registry = w3.eth.contract(address=REGISTRY_ADDR, abi=abi)

    # Prepare and send the transaction
    claim_id = w3.keccak(text=AGENT_DID)
    topic = w3.keccak(text="inputRoot")
    data_bytes = Web3.to_bytes(hexstr=input_root)

    nonce = w3.eth.get_transaction_count(owner)
    tx = registry.functions.claim(
        claim_id, topic, data_bytes
    ).build_transaction({
        "from": owner,
        "nonce": nonce
    })

    signed_tx = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print("InputRoot attestation tx:", tx_hash.hex())

if __name__ == "__main__":
    main()

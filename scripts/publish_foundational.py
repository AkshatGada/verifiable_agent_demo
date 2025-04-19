#!/usr/bin/env python3
import os
import json
import hashlib
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

from github_agent.identity import AGENT_DID, model_hash

def main():
    # Load environment variables from .env
    load_dotenv()
    RPC_URL        = os.getenv("RPC_URL")
    OWNER_KEY      = os.getenv("OWNER_KEY")
    REGISTRY_ADDR  = os.getenv("REGISTRY_ADDR")

    # Validate required env vars
    if not RPC_URL or not OWNER_KEY or not REGISTRY_ADDR:
        print("Error: RPC_URL, OWNER_KEY, and REGISTRY_ADDR must be set in .env")
        return

    # Connect to chain
    w3    = Web3(Web3.HTTPProvider(RPC_URL))
    acct  = w3.eth.account.from_key(OWNER_KEY)
    owner = acct.address

    # Load the registry ABI
    abi_path = Path("artifacts/contracts/IdentityRegistry.sol/IdentityRegistry.json")
    if not abi_path.exists():
        print(f"Error: ABI file not found at {abi_path}")
        return

    with abi_path.open() as f:
        abi = json.load(f)["abi"]

    # Instantiate the contract
    registry = w3.eth.contract(address=REGISTRY_ADDR, abi=abi)

    # Prepare the foundational claim
    claim_id   = Web3.keccak(text=AGENT_DID)         # keccak256(DID) as bytes32
    topic      = Web3.keccak(text="foundational")   # keccak256("foundational")
    data_bytes = Web3.to_bytes(hexstr=model_hash()) # sha256(agent code)

    # Build transaction
    nonce = w3.eth.get_transaction_count(owner)
    tx = registry.functions.claim(
        claim_id,
        topic,
        data_bytes
    ).build_transaction({
        "from":  owner,
        "nonce": nonce,
    })

    # Sign & send
    signed_tx = acct.sign_transaction(tx)
    tx_hash   = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    print("Foundational attestation submitted. Tx hash:", tx_hash.hex())

if __name__ == "__main__":
    main()
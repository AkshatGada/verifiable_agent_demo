#!/usr/bin/env python3
import os, json, hashlib
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

from github_agent.identity import AGENT_DID, model_hash

def main():
    load_dotenv()
    RPC_URL       = os.getenv("RPC_URL")
    REGISTRY_ADDR = os.getenv("REGISTRY_ADDR")

    # sanity checks
    if not RPC_URL or not REGISTRY_ADDR:
        print("❌ .env must define RPC_URL and REGISTRY_ADDR")
        return

    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    # load ABI
    abi_path = Path("artifacts/contracts/IdentityRegistry.sol/IdentityRegistry.json")
    abi = json.load(abi_path.open())["abi"]

    registry = w3.eth.contract(address=REGISTRY_ADDR, abi=abi)

    # compute the same keys you used when publishing
    claim_id = w3.keccak(text=AGENT_DID)
    expected_topic = w3.keccak(text="foundational")
    expected_data  = bytes.fromhex(model_hash())

    # fetch on‑chain
    claim = registry.functions.claims(claim_id).call()
    actual_topic, actual_data, issuer, timestamp = claim

    print(f"• On‑chain topic:  0x{actual_topic.hex()}")
    print(f"• Expect topic:    0x{expected_topic.hex()}")
    print(f"• On‑chain data:   0x{actual_data.hex()}")
    print(f"• Expect data:     0x{expected_data.hex()}")
    print(f"• Issuer address:  {issuer}")
    print(f"• Timestamp:       {timestamp}")

    # validations
    ok_topic = actual_topic == expected_topic
    ok_data  = actual_data  == expected_data

    if ok_topic and ok_data:
        print("✅ Foundational attestation is valid")
    else:
        print("❌ Foundational attestation does NOT match expected values")

if __name__ == "__main__":
    main()
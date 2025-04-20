#!/usr/bin/env python3
import os, json
from pathlib import Path
from web3 import Web3
from dotenv import load_dotenv
from github_agent.identity import AGENT_DID

load_dotenv()
RPC_URL       = os.getenv("RPC_URL")
OWNER_KEY     = os.getenv("OWNER_KEY")
REGISTRY_ADDR = os.getenv("REGISTRY_ADDR")

if not (RPC_URL and OWNER_KEY and REGISTRY_ADDR):
    raise RuntimeError(".env needs RPC_URL, OWNER_KEY, REGISTRY_ADDR")

# Read back the root from the proof file name
fname = next(Path("proofs").glob("inputRoot-*.json"))
root = fname.name.split("-")[1].rsplit(".",1)[0]  # the hex

w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(OWNER_KEY)
owner_addr = acct.address

# Load ABI from Hardhat artifacts
abi_path = Path("artifacts/contracts/IdentityRegistry.sol/IdentityRegistry.json")
abi = json.load(abi_path.open())["abi"]
reg = w3.eth.contract(address=REGISTRY_ADDR, abi=abi)

# Build & send the claim
claim_id   = w3.keccak(text=AGENT_DID)
topic      = w3.keccak(text="inputRoot")
data_bytes = w3.to_bytes(hexstr=root)

nonce = w3.eth.get_transaction_count(owner_addr)
tx = reg.functions.claim(claim_id, topic, data_bytes).build_transaction({
    "from":  owner_addr,
    "nonce": nonce,
})
signed = acct.sign_transaction(tx)
txh    = w3.eth.send_raw_transaction(signed.rawTransaction)
print("Published inputRoot, tx hash:", txh.hex())
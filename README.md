# Verifiable AI Agent Framework

## Why We Built This Framework

As AI agents become integral parts of decentralized applications, ensuring their actions and data inputs are transparent, tamper‑proof, and auditable is critical. This framework provides a step‑by‑step pipeline that:

1. **Identifies** AI agents with cryptographically verifiable DIDs.
2. **Anchors** agent identities and reputation on a blockchain-based registry.
3. **Validates** and commits input data (e.g., GitHub README files) via off‑chain hashing, verifiable credentials, and on‑chain anchoring.

By integrating these components, we create a bullet‑proof provenance trail—from raw data ingestion through signed credentials to immutable blockchain records.

## What We've Achieved

- **GitHub Agent**: A custom AI agent that fetches and summarizes README files from arbitrary GitHub repositories.
- **Identity Registry**: A Solidity smart contract (`IdentityRegistry`) that records agent DIDs and associated claims on‑chain.
- **Input Validation**: Deterministic hashing of input data into an `inputRoot`, issuance of a W3C Verifiable Credential, and anchoring of that root on‑chain.

Together, these pieces form a fully decentralized, end‑to‑end verifiable protocol for AI agents on blockchain.

---

## 1. GitHub Agent

The **GitHub Agent** is built on top of the Sentient Agent Framework and performs the following tasks:

1. **Fetch**: Uses the GitHub API to retrieve the raw README.md from one or more repository URLs.
2. **Vectorize** (optional extension): Builds a vector store from README content for retrieval‑augmented summarization.
3. **Summarize**: Produces a concise summary of each repository.

### Setup & Usage

```bash
# 1. Clone the repo
git clone https://github.com/your-org/verifiable_agent_demo.git
cd verifiable_agent_demo

# 2. Create & activate venv
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the agent server
python app.py

# 5. Query the agent
curl -N http://localhost:8000/assist \
  -H "Content-Type: application/json" \
  -d '{"session":{…},"query":{"id":"","prompt":"https://github.com/user/repo"}}'
```

Logs will show each README fetched and the generated summary.

---

## 2. Identity Registry

The **Identity Registry** is a smart contract that maintains a mapping from `keccak256(agentDID)` to a list of claims (topics and data).

### Contract: `IdentityRegistry.sol`

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract IdentityRegistry {
    struct Claim { bytes32 topic; bytes data; uint256 timestamp; }
    mapping(bytes32 => Claim[]) public claims;

    function claim(bytes32 id, bytes32 topic, bytes calldata data) external {
        claims[id].push(Claim(topic, data, block.timestamp));
    }
}
```

### Deployment

1. **Install Hardhat**
   ```bash
   npm init -y
   npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers dotenv
   npx hardhat  # select "Create an empty hardhat.config.js"
   ```
2. **Configure** your `hardhat.config.js` with your RPC and private key in `.env`.
3. **Compile & Deploy**
   ```bash
   npx hardhat compile
   npx hardhat run scripts/deploy_registry.js --network 
   ```
4. **Save** the deployed address to `.env → REGISTRY_ADDR`.

---

## 3. Input Validation & Commitment

This module creates an **inputRoot** from your agent's raw inputs, issues a Verifiable Credential, and anchors the root on‑chain.

### A. Compute the Input‑Root

```bash
# Generate the unsigned credential payload
python scripts/make_input_root_cred.py \
  https://github.com/ethereum/go-ethereum \
  https://github.com/langchain-ai/langchain \
> proofs/cred.json
```

This script:
- Fetches each README
- SHA‑256 hashes each text
- Sorts the digests and hashes the concatenation into `inputRoot`
- Outputs a pure JSON VC payload to `proofs/cred.json`

### B. Issue the Verifiable Credential

Using DIDKit (Dockerized):

```bash
# Remove any stale proofs
rm -f proofs/inputRoot-*.json

# Issue & sign the VC
docker run --rm -i \
  -v "$(pwd)":/data -w /data \
  ghcr.io/spruceid/didkit-cli:latest \
  credential issue --key-path .agent_key.jwk \
   proofs/inputRoot-.json
```

Verify the credential:
```bash
didkit credential verify proofs/inputRoot-.json
# Should report {"checks":["proof"],"warnings":[],"errors":[]}
```

### C. Anchor On‑Chain

```bash
python scripts/publish_input_root_tx.py
```

This script:
- Reads the `` from the filename
- Builds a transaction calling `registry.claim( keccak256(agentDID), keccak256("inputRoot"), bytes(root) )`
- Signs & sends it with `OWNER_KEY`
- Prints the transaction hash

Verify on‑chain:
```bash
python scripts/verify_onchain.py
# Confirms topic == keccak256("inputRoot") and data == root
```

---

## What's Next

- **Execution Tracing**: Record and Merkle‑tree hash the agent's runtime logs, then verify with zk‑proofs.
- **Reputation Signals**: Build social and behavioral attestations on top of this identity foundation.

> By following these steps, you have a fully decentralized, transparent, and verifiable pipeline for your AI agent—from data ingestion to on‑chain proof.

---
Answer from Perplexity: pplx.ai/share

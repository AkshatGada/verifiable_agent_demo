# Verifiable AI Agent Framework : Version 0 

# Why We Built This Framework

As AI agents become integral parts of decentralized applications, ensuring their actions and data inputs are transparent, tamper‑proof, and auditable is critical. This framework provides a step‑by‑step pipeline that:

1. **Identifies** AI agents with cryptographically verifiable DIDs.
2. **Anchors** agent identities and reputation on a blockchain-based registry.
3. **Validates** and commits input data (e.g., GitHub README files) via off‑chain hashing, verifiable credentials, and on‑chain anchoring.

By integrating these components, we create a bullet‑proof provenance trail—from raw data ingestion through signed credentials to immutable blockchain records.

## The Critical Need for Verifiable AI

### Trust Without Transparency Isn't Trust

Today's AI systems operate as black boxes, making decisions with little visibility into their data sources, reasoning processes, or execution pathways. This lack of transparency creates significant risks:

- **Data integrity cannot be guaranteed** without verifiable proof of what information an AI agent consumed
- **Accountability becomes impossible** when there's no cryptographic trail of an agent's actions
- **Attribution is challenging** without verifiable agent identities tied to responsible entities

## Verifiability as the Foundation of Trusted AI

Verifiability serves as the missing piece in the AI ecosystem, enabling agents to operate with unprecedented levels of trust:

- **Transparent Decision Trails**: Our framework enables users to backtrace exactly how an AI agent arrived at its conclusions, creating accountability for every action

- **Provable Authenticity**: Through cryptographic proofs, we demonstrate that agent actions are genuinely autonomous and not manipulated by hidden human operators—essential for establishing trusted agentic systems

- **Immutable Reputation**: By anchoring agent identities and attestations on-chain, we create an indelible record of agent behavior that builds cumulative trust over time

---

# 🎯 What We've Achieved (Start to Finish)


<img width="1319" alt="image" src="https://github.com/user-attachments/assets/38ba2704-394b-4405-82b6-e65ecc99c993" />

1. **GitHub Agent Initialization**
   - Built a custom AI agent on the Sentient Agent Framework that fetches and summarizes README files from arbitrary GitHub repositories.

2. **Cryptographic Agent Identity**
   - Generated a did:key:… DID for the agent and securely stored its JWK keypair.

3. **Foundational On‑Chain Attestation**
   - Anchored the agent's DID on‑chain via a claim in the IdentityRegistry smart contract, binding agent identity to your Ethereum address.

4. **Deterministic Input‑Root Computation**
   - Fetched each README, SHA‑256‑hashed its contents, sorted the hashes, and produced a single inputRoot digest.

5. **Input‑Root Verifiable Credential**
   - Wrapped the inputRoot in a W3C‑compliant Verifiable Credential and signed it with the agent's DID using DIDKit.

6. **Input‑Root On‑Chain Anchoring**
   - Published the same inputRoot hash under keccak256(agentDID) in the IdentityRegistry contract for immutable public proof.

7. **Execution‑Level Logging**
   - Instrumented every agent step—prompts, tool calls, LLM inputs/outputs—with timestamped, hashed log entries.

8. **Merkle‑Tree Construction**
   - Built a Merkle tree over all execution‑log hashes to compute a single executionRoot that commits to the entire session.

9. **Decentralized Trace Storage**
   - Published the full execution trace and Merkle‑tree data to IPFS, yielding immutable CIDs for auditor retrieval.

10. **Execution‑Root Verifiable Credential**
    - Packaged the executionRoot in a W3C‑Verifiable Credential and signed it with the agent's DID.

11. **Execution‑Root On‑Chain Anchoring**
    - Recorded the executionRoot hash on‑chain in the IdentityRegistry, extending your proof ledger to cover runtime behavior.

12. **Zero‑Knowledge Verification**
    - Generated a zk‑SNARK proof that the Merkle tree was constructed correctly, and deployed a Solidity verifier to confirm the proof both off‑chain and on‑chain.

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

## Results in terminal 
 <img width="1511" alt="Screenshot 2025-04-19 at 5 58 10 AM" src="https://github.com/user-attachments/assets/15a82fd6-189d-45b7-a6a6-572536f4d36c" />
 &nbsp;
<img width="1511" alt="Screenshot 2025-04-19 at 5 59 22 AM" src="https://github.com/user-attachments/assets/d0f9e505-9b90-4f80-b876-cba148db08e6" />
&nbsp;
<img width="1511" alt="Screenshot 2025-04-19 at 6 00 09 AM" src="https://github.com/user-attachments/assets/6c81a7c2-1155-436f-a4d2-2ad547ab3fa7" />
&nbsp;
<img width="1026" alt="Screenshot 2025-04-19 at 5 57 20 AM" src="https://github.com/user-attachments/assets/54c588cb-75ee-48ad-8d9f-759b3876e57c" />
&nbsp;

#!/usr/bin/env python3
import json
import argparse
from datetime import datetime
from github_agent.identity import AGENT_DID
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--out", "-o", default="proofs/execution_cred.json")
args = parser.parse_args()

# Read the root from the Merkle tree file
tree = json.load(open("proofs/execution_tree.json"))
root = tree["root"]

cred = {
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "id":           f"urn:executionroot:{root}",
  "type":         ["VerifiableCredential","ExecutionRoot"],
  "issuer":       AGENT_DID,
  "issuanceDate": f"{datetime.utcnow().isoformat()}Z",
  "credentialSubject": {"executionRoot": root}
}

Path(args.out).write_text(json.dumps(cred, indent=2))
print("Wrote unsigned execution VC to", args.out)
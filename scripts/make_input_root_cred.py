#!/usr/bin/env python3
import json, hashlib, argparse
from datetime import datetime

from github_agent.identity import AGENT_DID
from github_agent.utils.github_readme import fetch_and_hash

parser = argparse.ArgumentParser()
parser.add_argument("repos", nargs="+")
parser.add_argument("--out", "-o", default="proofs/cred.json")
args = parser.parse_args()

digests = []
for url in args.repos:
    _, _, d = fetch_and_hash(url)
    digests.append(d)

root = hashlib.sha256("".join(sorted(digests)).encode()).hexdigest()

cred = {
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "id":           f"urn:inputroot:{root}",
  "type":         ["VerifiableCredential", "InputRoot"],
  "issuer":       AGENT_DID,
  "issuanceDate": f"{datetime.utcnow().isoformat()}Z",
  "credentialSubject": {"inputRoot": root}
}

# write *only* JSON
with open(args.out, "w") as f:
    json.dump(cred, f, indent=2)
print(f"Wrote pure JSON credential to {args.out}")
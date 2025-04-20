import json, hashlib
from datetime import datetime
from merkletools import MerkleTools
import ipfshttpclient

class ExecutionLogger:
    def __init__(self, agent_did: str):
        self.agent_did = agent_did
        self.entries = []

    def _record(self, event_type: str, payload):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type":      event_type,
            "payload":   payload
        }
        # digest of the canonical JSON
        data = json.dumps(entry, sort_keys=True).encode()
        entry["hash"] = hashlib.sha256(data).hexdigest()
        self.entries.append(entry)

    # hook these into the response handler
    def log_text(self, label: str, text: str):
        self._record("TEXT", {"label": label, "text": text})

    def log_json(self, label: str, obj):
        self._record("JSON", {"label": label, "json": obj})

    def log_error(self, label: str, err):
        self._record("ERROR", {"label": label, "error": err})

    def finalize(self):
        # Build a Merkle tree over the entry hashes
        mt = MerkleTools(hash_type="sha256")
        for e in self.entries:
            mt.add_leaf(e["hash"], do_hash=False)
        mt.make_tree()
        root = mt.get_merkle_root()

        # write out full trace + tree
        with open("proofs/execution_trace.json", "w") as f:
            json.dump(self.entries, f, indent=2)
        with open("proofs/execution_tree.json", "w") as f:
            json.dump({
                "root": root,
                "layers": mt.get_layers()
            }, f, indent=2)

        # publish to IPFS
        client = ipfshttpclient.connect()  
        res = client.add(["proofs/execution_trace.json", "proofs/execution_tree.json"])
        # res is a list of dicts with 'Hash' fields
        cids = { Path(x["Name"]).name: x["Hash"] for x in res }
        with open("proofs/execution_cids.json", "w") as f:
            json.dump(cids, f, indent=2)

        return root, cids
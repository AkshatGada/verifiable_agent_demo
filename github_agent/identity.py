import os
import pathlib
import didkit
import hashlib

# Path to the agent's JWK key file
KEY_PATH = pathlib.Path(".agent_key.jwk")

# Generate or load the agent key & DID

def load_or_create_key():
    if KEY_PATH.exists():
        key_jwk = KEY_PATH.read_text()
    else:
        # Create a new Ed25519 key
        key_jwk = didkit.generate_ed25519_key()
        KEY_PATH.write_text(key_jwk)
    # Derive a did:key from the JWK
    did = didkit.key_to_did("key", key_jwk)
    return did, key_jwk

AGENT_DID, AGENT_KEY = load_or_create_key()
# Expose the path for CLI-based operations
AGENT_KEY_PATH = str(KEY_PATH)


def model_hash() -> str:
    """
    Computes the SHA-256 hash of this identity module's source code.
    """
    code = pathlib.Path(__file__).read_bytes()
    return hashlib.sha256(code).hexdigest()

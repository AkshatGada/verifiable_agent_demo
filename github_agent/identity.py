import os, json, hashlib, pathlib

import didkit                # comes from didkit-py 0.5.0+

KEY_PATH = pathlib.Path(".agent_key.jwk")

def load_or_create_key():
    """
    Returns (did, jwk_json_str)
    """
    if KEY_PATH.exists():
        key_jwk = KEY_PATH.read_text()
    else:
        key_jwk = didkit.generate_ed25519_key()        # ← NEW API
        KEY_PATH.write_text(key_jwk)

    did = didkit.key_to_did("key", key_jwk)            # NEW API
    return did, key_jwk

AGENT_DID, AGENT_KEY = load_or_create_key()

def model_hash() -> str:
    code = pathlib.Path(__file__).with_suffix(".py").read_bytes()
    return hashlib.sha256(code).hexdigest()
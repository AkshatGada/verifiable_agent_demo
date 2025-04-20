#!/usr/bin/env bash
set -euo pipefail

CIRCUIT=circuits/merkleTree.circom
PTAU=powersOfTau28_hez_final_12.ptau
BUILD=build
TREE=proofs/execution_tree.json

echo "[1] Compile circuit"
circom $CIRCUIT \
  --r1cs --wasm --sym \
  -o $BUILD

echo "[2] Setup zkey"
snarkjs groth16 setup \
  $BUILD/merkleTree.r1cs \
  $PTAU \
  $BUILD/merkle_0000.zkey

echo "[3] Contribute randomness"
snarkjs zkey contribute \
  $BUILD/merkle_0000.zkey \
  $BUILD/merkle_final.zkey \
  --name="First contribution" -v

echo "[4] Export verification key"
snarkjs zkey export verificationkey \
  $BUILD/merkle_final.zkey \
  $BUILD/verification_key.json

echo "[5] Generate witness"
# Convert execution_tree.json -> input.json for the WASM
jq '{ leaf: [.leaves[]] }' $TREE > $BUILD/input.json
node $BUILD/merkleTree_js/generate_witness.js \
  $BUILD/merkleTree_js/merkleTree.wasm \
  $BUILD/input.json \
  $BUILD/witness.wtns

echo "[6] Create proof + public signals"
snarkjs groth16 prove \
  $BUILD/merkle_final.zkey \
  $BUILD/witness.wtns \
  $BUILD/proof.json \
  $BUILD/public.json

echo "[7] Verify proof locally"
snarkjs groth16 verify \
  $BUILD/verification_key.json \
  $BUILD/public.json \
  $BUILD/proof.json

echo "✅ All steps completed. Merkle‑root proof is valid!"
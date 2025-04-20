pragma circom 2.2.2;

include "circomlib/circuits/poseidon.circom";

template Merkle4() {
    signal input leaf[4];
    // level 1
    component h0 = Poseidon(2);
    component h1 = Poseidon(2);
    h0.inputs[0] <== leaf[0];  h0.inputs[1] <== leaf[1];
    h1.inputs[0] <== leaf[2];  h1.inputs[1] <== leaf[3];
    // level 2
    component h2 = Poseidon(2);
    h2.inputs[0] <== h0.out;   // Changed from h0.output to h0.out
    h2.inputs[1] <== h1.out;   // Changed from h1.output to h1.out
    signal output root;
    root <== h2.out;           // Changed from h2.output to h2.out
}

component main = Merkle4();

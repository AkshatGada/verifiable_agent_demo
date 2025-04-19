// SPDX‑License‑Identifier: MIT
pragma solidity ^0.8.19;

contract IdentityRegistry {
    struct Claim {
        bytes32 topic;   // e.g. keccak256("foundational")
        bytes   data;    // payload (e.g. model hash)
        address issuer;  // msg.sender
        uint64  ts;
    }

    mapping(bytes32 id => Claim) public claims; // id = keccak256(DID)

    event Claimed(bytes32 indexed id, bytes32 topic, address issuer);

    function claim(bytes32 id, bytes32 topic, bytes calldata data) external {
        claims[id] = Claim(topic, data, msg.sender, uint64(block.timestamp));
        emit Claimed(id, topic, msg.sender);
    }
}
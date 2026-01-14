// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract KERIAnchor {
    // Store: AID -> Sequence -> Hash
    mapping(string => mapping(uint256 => string)) public anchors;
    
    // Store latest sequence per drone
    mapping(string => uint256) public latestSequence;
    
    // Event emitted when anchor is registered
    event AnchorRegistered(string aid, uint256 sequence, string hash);
    
    // Store a new anchor
    function registerAnchor(string memory aid, uint256 sequence, string memory hash) public {
        require(sequence > latestSequence[aid], "Sequence must increase");
        
        anchors[aid][sequence] = hash;
        latestSequence[aid] = sequence;
        
        emit AnchorRegistered(aid, sequence, hash);
    }
    
    // Get stored hash
    function getAnchor(string memory aid, uint256 sequence) public view returns (string memory) {
        return anchors[aid][sequence];
    }
}
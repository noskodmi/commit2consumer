// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Commit2Consumer {
    struct Bounty {
        uint256 id;
        string issueUrl;
        address funder;
        uint256 amount;
        bool resolved;
        address resolver;
    }

    uint256 public bountyCount;
    mapping(uint256 => Bounty) public bounties;

    address public authorizedResolver;

    event BountyCreated(uint256 indexed bountyId, string issueUrl, address indexed funder, uint256 amount);
    event BountyResolved(uint256 indexed bountyId, address indexed developer, uint256 amount);

    constructor(address _resolver) {
        authorizedResolver = _resolver;
    }

    modifier onlyResolver() {
        require(msg.sender == authorizedResolver, "Not authorized");
        _;
    }

    function createBounty(string memory issueUrl) external payable {
        require(msg.value > 0, "Bounty must have funds");

        bountyCount++;
        bounties[bountyCount] = Bounty({
            id: bountyCount,
            issueUrl: issueUrl,
            funder: msg.sender,
            amount: msg.value,
            resolved: false,
            resolver: address(0)
        });

        emit BountyCreated(bountyCount, issueUrl, msg.sender, msg.value);
    }

    function resolveBounty(uint256 bountyId, address developer) external onlyResolver {
        Bounty storage b = bounties[bountyId];
        require(!b.resolved, "Already resolved");
        require(b.amount > 0, "No funds");

        b.resolved = true;
        b.resolver = developer;

        payable(developer).transfer(b.amount);

        emit BountyResolved(bountyId, developer, b.amount);
    }
}
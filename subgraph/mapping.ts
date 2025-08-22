import { BountyCreated, BountyResolved } from "../generated/Commit2Consumer/Commit2Consumer"
import { Bounty } from "../generated/schema"

export function handleBountyCreated(event: BountyCreated): void {
  let bounty = new Bounty(event.params.bountyId.toString())
  bounty.issueUrl = event.params.issueUrl
  bounty.funder = event.params.funder
  bounty.amount = event.params.amount
  bounty.resolved = false
  bounty.save()
}

export function handleBountyResolved(event: BountyResolved): void {
  let bounty = Bounty.load(event.params.bountyId.toString())
  if (bounty) {
    bounty.resolved = true
    bounty.resolver = event.params.developer
    bounty.save()
  }
}
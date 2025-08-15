def is_pr_merged(payload: dict) -> bool:
    return payload.get("action") == "closed" and payload.get("pull_request", {}).get("merged", False)

def extract_contributor(payload: dict):
    pr = payload.get("pull_request", {})
    contributor = pr.get("user", {}).get("login")
    repo_name = payload.get("repository", {}).get("full_name")
    # For MVP, assume contributor's wallet address is in PR body
    body = pr.get("body", "")
    wallet = body.strip() if body.startswith("0x") else None
    return wallet, repo_name
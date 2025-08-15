import hmac
import hashlib
import os

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False
    sha_name, signature = signature_header.split("=")
    if sha_name != "sha256":
        return False
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

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
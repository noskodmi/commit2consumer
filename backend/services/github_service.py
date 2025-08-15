import hmac
import hashlib
import os
import logging
from config import settings

logger = logging.getLogger(__name__)

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature"""
    if not WEBHOOK_SECRET:
        logger.warning("GITHUB_WEBHOOK_SECRET not configured")
        return False
        
    if not signature_header:
        logger.warning("No signature header provided")
        return False
        
    try:
        sha_name, signature = signature_header.split("=")
        if sha_name != "sha256":
            logger.warning(f"Unsupported signature algorithm: {sha_name}")
            return False
            
        mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
        return hmac.compare_digest(mac.hexdigest(), signature)
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False

def is_pr_merged(payload: dict) -> bool:
    """Check if the webhook payload is for a merged PR"""
    is_merged = (
        payload.get("action") == "closed" and 
        payload.get("pull_request", {}).get("merged", False)
    )
    
    if is_merged:
        pr_number = payload.get("pull_request", {}).get("number")
        repo = payload.get("repository", {}).get("full_name")
        logger.info(f"Detected merged PR #{pr_number} in {repo}")
    
    return is_merged

def extract_contributor(payload: dict):
    """Extract contributor information from webhook payload"""
    pr = payload.get("pull_request", {})
    contributor = pr.get("user", {}).get("login")
    repo_name = payload.get("repository", {}).get("full_name")
    
    # For MVP, look for wallet address in PR body
    body = pr.get("body", "")
    
    # Simple regex-like search for Ethereum address
    wallet = None
    if body:
        lines = body.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("0x") and len(line) >= 40:
                wallet = line.split()[0]  # Take first word if there are multiple
                break
    
    logger.info(f"Extracted contributor: {contributor}, wallet: {wallet}, repo: {repo_name}")
    return wallet, repo_name
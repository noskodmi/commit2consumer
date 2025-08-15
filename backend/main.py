from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services import repo_processor, llm_service, reward_service, github_service
from models import AddRepoRequest, ChatRequest, ChatResponse, FAQResponse, DocsResponse
import logging
from typing import List
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
            
app = FastAPI(title="Commit2Consumer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory repo store for MVP
repos = {}

# Top Mantle repos to preload
TOP_MANTLE_REPOS = [
    "https://github.com/mantlenetworkio/mantle",
    "https://github.com/mantlenetworkio/mantle-contracts",
    "https://github.com/mantlenetworkio/mantle-tutorial",
    "https://github.com/mantlenetworkio/mantle-sdk",
    "https://github.com/mantlenetworkio/mantle-docs"
]

@app.on_event("startup")
async def preload_repos():
    logger.info("Preloading Top Mantle repos...")
    for url in TOP_MANTLE_REPOS:
        try:
            repo_id, meta = await repo_processor.process_repo(url)
            repos[repo_id] = meta
            logger.info(f"Preloaded repo {url} with ID {repo_id}")
        except Exception as e:
            logger.error(f"Failed to preload {url}: {str(e)}")

@app.get("/health")
def health():
    return {"status": "ok", "environment": "production" if settings.PRODUCTION else "development"}

@app.get("/repos")
def list_repos():
    logger.info(f"Listing {len(repos)} repositories")
    return list(repos.values())

@app.post("/repos")
async def add_repo(req: AddRepoRequest):
    logger.info(f"Adding new repo: {req.url}")
    try:
        repo_id, meta = await repo_processor.process_repo(req.url)
        repos[repo_id] = meta
        logger.info(f"Successfully added repo {req.url} with ID {repo_id}")
        return {"id": repo_id, "meta": meta}
    except Exception as e:
        logger.error(f"Failed to add repo {req.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process repository: {str(e)}")

@app.get("/repos/{repo_id}/docs", response_model=DocsResponse)
def get_docs(repo_id: str):
    if repo_id not in repos:
        logger.warning(f"Repo not found: {repo_id}")
        raise HTTPException(404, "Repository not found")
    
    logger.info(f"Generating docs for repo {repo_id}")
    try:
        return llm_service.get_docs(repo_id)
    except Exception as e:
        logger.error(f"Error generating docs for {repo_id}: {str(e)}")
        raise HTTPException(500, f"Error generating documentation: {str(e)}")

@app.get("/repos/{repo_id}/faq", response_model=FAQResponse)
def get_faq(repo_id: str):
    if repo_id not in repos:
        logger.warning(f"Repo not found: {repo_id}")
        raise HTTPException(404, "Repository not found")
    
    logger.info(f"Generating FAQ for repo {repo_id}")
    try:
        return llm_service.get_faq(repo_id)
    except Exception as e:
        logger.error(f"Error generating FAQ for {repo_id}: {str(e)}")
        raise HTTPException(500, f"Error generating FAQ: {str(e)}")

@app.post("/repos/{repo_id}/chat", response_model=ChatResponse)
def chat_repo(repo_id: str, req: ChatRequest):
    if repo_id not in repos:
        logger.warning(f"Repo not found: {repo_id}")
        raise HTTPException(404, "Repository not found")
    
    logger.info(f"Chat request for repo {repo_id}: {req.question}")
    try:
        return llm_service.chat(repo_id, req.question)
    except Exception as e:
        logger.error(f"Error in chat for {repo_id}: {str(e)}")
        raise HTTPException(500, f"Error processing chat request: {str(e)}")

@app.post("/webhook/github")
async def github_webhook(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    body = await request.body()

    # Verify webhook signature
    if not github_service.verify_signature(body, signature):
        logger.warning("Invalid webhook signature received")
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = await request.json()
        
        # Check if this is a merged PR
        if github_service.is_pr_merged(payload):
            contributor_wallet, repo_name = github_service.extract_contributor(payload)
            
            if not contributor_wallet:
                logger.warning(f"No wallet address found for contributor in PR from {repo_name}")
                return {"status": "no_wallet_found"}
            
            # Send reward
            tx_hash = reward_service.send_reward(contributor_wallet)
            
            if tx_hash == "invalid_wallet":
                logger.warning(f"Invalid wallet address: {contributor_wallet}")
                return {"status": "invalid_wallet_address"}
                
            logger.info(f"Reward sent to {contributor_wallet} for PR in {repo_name}, tx: {tx_hash}")
            return {"status": "reward_sent", "tx_hash": tx_hash, "wallet": contributor_wallet}
        
        logger.info("Webhook received but not a merged PR")
        return {"status": "ignored", "reason": "not_a_merged_pr"}
    
    except Exception as e:
        logger.error(f"Error processing GitHub webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")
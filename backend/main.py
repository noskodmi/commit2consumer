from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from services import repo_processor, llm_service, reward_service, github_service
from models import AddRepoRequest, ChatRequest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
            
app = FastAPI(title="Commit2Consumer API")

# In-memory repo store for MVP
repos = {}

TOP_MANTLE_REPOS = [
    "https://github.com/mantlenetworkio/mantle",
    "https://github.com/mantlenetworkio/mantle-contracts",
    ...
]

@app.on_event("startup")
async def preload_repos():
    logging.info("Preloading Top Mantle repos...")
    for url in TOP_MANTLE_REPOS:
        try:
            repo_id, meta = await repo_processor.process_repo(url)
            repos[repo_id] = meta
            logging.info(f"Preloaded repo {url} with ID {repo_id}")
        except Exception as e:
            logging.error(f"Failed to preload {url}: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/repos")
def list_repos():
    return list(repos.values())

@app.post("/repos")
async def add_repo(req: AddRepoRequest):
    repo_id, meta = await repo_processor.process_repo(req.url)
    repos[repo_id] = meta
    return {"id": repo_id, "meta": meta}

@app.get("/repos/{repo_id}/docs")
def get_docs(repo_id: str):
    if repo_id not in repos:
        raise HTTPException(404, "Repo not found")
    return llm_service.get_docs(repo_id)

@app.get("/repos/{repo_id}/faq")
def get_faq(repo_id: str):
    if repo_id not in repos:
        raise HTTPException(404, "Repo not found")
    return llm_service.get_faq(repo_id)

@app.post("/repos/{repo_id}/chat")
def chat_repo(repo_id: str, req: ChatRequest):
    if repo_id not in repos:
        raise HTTPException(404, "Repo not found")
    return llm_service.chat(repo_id, req.question)

@app.post("/webhook/github")
async def github_webhook(request: Request):
    payload = await request.json()
    if github_service.is_pr_merged(payload):
        contributor, repo_name = github_service.extract_contributor(payload)
        tx_hash = reward_service.send_reward(contributor)
        return {"status": "reward_sent", "tx_hash": tx_hash}
    return {"status": "ignored"}
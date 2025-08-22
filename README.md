Commit2Consumer


Commit2Consumer is my submission for Cook 04.
It’s a MVP for Mantle users that makes open source more rewarding: anyone can fund a GitHub issue with MNT, and when a PR closes it, the developer gets paid automatically. We use The Graph for indexing and transparency, and added a Repo2Chat demo so contributors can quickly understand a repo with auto‑docs, FAQs, and chat.


- 🌐 App: [Link](https://commit2consumer.vercel.app)
- 🎥 Demo: [Link](https://commit2consumer.vercel.app/demo)
- 📜 Smart Contract (Mantle Sepolia): [0x39898600f965fa785B64893411C61030C316314e](https://sepolia.mantlescan.xyz/address/0x39898600f965fa785B64893411C61030C316314e)
- 📊 Subgraph: [Mantle Subgraphs](https://subgraph-api.mantle.xyz/api/public/query_deployment?subgraph_id=QmV37dVDGrrUWNLMdx6ANZZNKowLpFhcp5bZS64Ln3f6go)

---

Tech Stack

- Smart Contract: Solidity (Mantle Sepolia), code is in subgraph folder
- Indexing: The Graph (Mantle subgraphs), code is in subgraph folder
- Frontend: React + Tailwind, wagmi + viem for wallet connect
- Backend: Flask (demo) / FastAPI (planned)
- Repo2Chat: mocked with GPT‑5‑nano (full pipeline with different models and local inference for privacy planned)

---

Run Locally

Prerequisites

- Node.js 18+
- Python 3.11+
- Docker (optional)

Frontend

	cd frontend
	npm install
	npm run dev

App runs on http://localhost:3000

Backend (Flask demo)

	cd backend
	pip install -r requirements.txt
	python app.py

Backend runs on http://localhost:5000


---

Run with Docker

	docker-compose up --build

This will spin up both frontend and backend containers.


---

Notes
- This is work in progress. Both Commit2Consumer and Repo2Chat are subjects of change, deployed version is on branch called "latest"
- Contract + subgraph are live on Mantle Sepolia.
- Repo2Chat is mocked for demo but will be extended with full ingestion + embeddings.
- Next steps: smarter Repo2Chat, benchmarks, and expanding beyond auto-rewarding closed PRs to contests, hackathons, etc.
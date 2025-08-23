#!/bin/bash

# Create directories
mkdir -p backend
mkdir -p frontend/public
mkdir -p frontend/src/components
mkdir -p frontend/src/hooks
mkdir -p frontend/src/utils
mkdir -p contracts

# Create backend files
touch backend/app.py
touch backend/requirements.txt
touch backend/railway.json
touch backend/Procfile
touch backend/.env.example

# Create frontend files
touch frontend/public/index.html
touch frontend/public/favicon.ico

touch frontend/src/components/Navigation.jsx
touch frontend/src/components/HomePage.jsx
touch frontend/src/components/AddBountyPage.jsx
touch frontend/src/components/Repo2ChatPage.jsx
touch frontend/src/components/RewardsPage.jsx
touch frontend/src/components/ProfilePage.jsx

touch frontend/src/hooks/useWeb3.js
touch frontend/src/hooks/useAPI.js

touch frontend/src/utils/constants.js
touch frontend/src/utils/helpers.js

touch frontend/src/App.jsx
touch frontend/src/main.jsx
touch frontend/src/index.css

touch frontend/package.json
touch frontend/vite.config.js
touch frontend/tailwind.config.js
touch frontend/postcss.config.js
touch frontend/vercel.json

# Create contracts
touch contracts/Commit2Consumer.sol

# Root-level files
touch .gitignore
touch README.md
touch deploy.md

echo "✅ Project structure created successfully in current folder!"
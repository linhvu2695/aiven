# Project Overview

This project consists of a **frontend** (React + Vite) and a **backend** (Flask API) designed for seamless local development using Docker and Makefile commands.

---

## Prerequisites

- [Node.js](https://nodejs.org/) (for frontend)
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) (for backend)
- [Make](https://www.gnu.org/software/make/) (for running provided commands)
- [Python 3.8+](https://www.python.org/) (if you wish to run backend outside Docker)

---

### 1. Start Backend Services

#### a. Start Docker Containers

From the project root, run:

```sh
make docker
```

This will start all required backend services (e.g., databases, caches) using Docker Compose.

#### b. Start the Flask API

**Option 1: Using Docker (Recommended)**  
No further action needed if your backend is containerized.

**Option 2: Running Locally (with Virtual Environment)**

```sh
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
make run
```

The Flask API will be available at [http://localhost:8000](http://localhost:8000).

---

### 2. Start the Frontend

```sh
cd frontend
npm install
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000).

---

## Environment Variables

- **Backend:** Configure environment variables in `backend/.env`.
- **Frontend:** Edit `frontend/.env.development` or `frontend/.env.production` as needed.

---

## Useful Commands

- **Start Docker containers:** `make docker` (from project root)
- **Run backend API:** `make run` (from `backend/` directory)
- **Run backend tests:** `make test` (from `backend/` directory)
- **Start frontend:** `npm run dev` (from `frontend/` directory)

---

## Notes

- Ensure Docker containers are running before starting the backend API.
- The frontend expects the backend API at `http://localhost:8000` by default.
- For production, update environment files accordingly.

---

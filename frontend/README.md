# Quickstart

This project consists of a **backend** (FastAPI, Python) and a **frontend** (React, Vite).

---

## Backend (FastAPI)

1. **Create and activate the virtual environment** (if not already created):

   ```sh
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   - Copy or edit `.env` in the `backend/` directory with your API keys and secrets.

4. **Run the backend server:**

   ```sh
   make run
   ```
   The FastAPI server will start at [http://localhost:8000](http://localhost:8000).

---

## Frontend (React + Vite)

1. **Install dependencies:**

   ```sh
   cd frontend
   npm install
   ```

2. **Set up environment variables:**

   - Edit `.env.development` if you need to change the API base URL (default is `http://localhost:8000`).

3. **Run the frontend dev server:**

   ```sh
   npm run dev
   ```
   The app will be available at [http://localhost:3000](http://localhost:3000).

---

## Notes

- The frontend expects the backend to be running at `http://localhost:8000` by default.
- Make sure to activate the Python virtual environment each time you work on the backend.
- For production, update `.env.production` in the frontend and deploy the backend accordingly.

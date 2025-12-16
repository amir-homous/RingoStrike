# RingoStrike

A habit & challenge tracking app built with:
- Flask backend
- Vue (Vite) frontend
- Notion as database
- Telegram login

## Current Status
🚧 MVP in progress

## Features (MVP)
- Telegram authentication
- Join public challenges
- Daily check-in
- Streak tracking
- User dashboard

## Tech Stack
- Backend: Flask, JWT
- Frontend: Vue 3 + Vite + Pinia
- Database: Notion
- Automation: n8n

## Run Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python app.py
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

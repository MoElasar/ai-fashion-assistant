# AI Fashion Assistant

An AI-powered outfit recommendation app that analyzes your wardrobe and suggests combinations using clothing detection, color theory, and Google Gemini. Built as a cross-platform Flutter app backed by a FastAPI service.

> Graduation capstone — Management Information Systems, Işık University.

## Features

- **Wardrobe management** — add clothing items from photos; the app detects and categorizes them.
- **AI outfit recommendations** — suggests combinations based on color theory and matching rules.
- **Gemini-powered analysis** — uses Google Gemini for clothing and image understanding.
- **Color extraction & matching** — pulls dominant colors from items and pairs them intelligently.
- **Weather-aware suggestions** — factors in current conditions.
- **Chat assistant** — conversational interface for style help.
- **Scheduling** — plan outfits ahead.
- **Analytics** — insights into wardrobe usage.
- **Authentication** — JWT-based user accounts.

## Tech Stack

**Frontend (Flutter)**
- Dart, Flutter (Android, iOS, web, desktop)
- Provider for state management

**Backend (FastAPI)**
- Python, FastAPI, SQLAlchemy
- Google Gemini API for image analysis
- OpenCV / image processing for color extraction
- JWT authentication

## Architecture
Flutter app  ──►  FastAPI backend  ──►  Google Gemini API

(lib/)            (ai-fashion-backend/)

├── routers/    # API endpoints

├── services/   # Gemini, color matching, recommendations

├── models/     # database models

└── schemas/    # request/response schemas
## Getting Started

### Backend

1. Create and activate a virtual environment:
```bash
   cd ai-fashion-backend
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
```
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Set up environment variables — copy the example and fill in your own values:
```bash
   cp .env.example .env
```
   You'll need a Google Gemini API key and a JWT secret.
4. Run the server:
```bash
   uvicorn main:app --reload
```

### Frontend

1. Install Flutter dependencies:
```bash
   flutter pub get
```
2. Run the app:
```bash
   flutter run
```

## Note

API keys and secrets are loaded from a `.env` file, which is git-ignored. Use `.env.example` as a template — never commit real credentials.

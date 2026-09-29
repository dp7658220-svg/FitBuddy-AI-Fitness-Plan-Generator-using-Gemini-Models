
# FitBuddy — AI Fitness Plan Generator (Gemini + FastAPI)

FitBuddy generates a personalized 7-day workout plan and a nutrition tip
from a short form (age, weight, fitness goal, intensity), using Google's
**Gemini 1.5 Pro** (workout generation + feedback-based revisions) and
**Gemini Flash** (fast nutrition tips). Data is persisted in SQLite via
SQLAlchemy, and there's a simple admin view to see every user's plan.

## Project structure

```
fitbuddy/
├── app/
│   ├── main.py                    # FastAPI app entrypoint
│   ├── routes.py                  # All route handlers
│   ├── database.py                # SQLAlchemy models + DB helpers
│   ├── schemas.py                 # Pydantic request schemas
│   ├── gemini_generator.py        # Gemini 1.5 Pro: workout + feedback update
│   └── gemini_flash_generator.py  # Gemini Flash: nutrition tips
├── templates/
│   ├── index.html                 # Input form
│   ├── result.html                # Plan, tip, feedback form
│   └── all_users.html             # Admin panel
├── static/css/style.css
├── requirements.txt
├── .env.example
└── .gitignore
```

## 1. Local setup

```bash
python -m venv fitbuddy-env
source fitbuddy-env/bin/activate      # Windows: fitbuddy-env\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# then edit .env and paste your real Gemini API key
```

Get a free Gemini API key at https://aistudio.google.com/app/apikey.

## 2. Run it

```bash
uvicorn app.main:app --reload
```

Visit **http://127.0.0.1:8000** for the app, and
**http://127.0.0.1:8000/docs** for the interactive API docs.

Routes:
| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Home page / input form |
| `/generate-workout` | POST | Generate workout plan + nutrition tip |
| `/submit-feedback` | POST | Revise plan based on feedback |
| `/view-all-users` | GET | Admin view of all users & plans |

## 3. Push to GitHub

```bash
cd fitbuddy
git init
git add .
git commit -m "FitBuddy: AI fitness plan generator (FastAPI + Gemini)"
git branch -M main
git remote add origin https://github.com/<your-username>/fitbuddy.git
git push -u origin main
```

(Create the empty repo on GitHub first — github.com → New repository —
then use the URL it gives you in place of the one above.)

## 4. Record a demo video

A simple, effective flow to record (screen recording, 2–4 minutes):

1. Start the server (`uvicorn app.main:app --reload`) and open `http://127.0.0.1:8000`.
2. Fill in the home page form (name, user ID, age, weight, goal, intensity) → **Generate Plan**.
3. Show the resulting **7-day workout plan** and **nutrition tip** on the result page.
4. Enter feedback (e.g. "Add more cardio") → **Update Plan** → show the revised plan.
5. Go to **/view-all-users** and show the admin table with original + updated plans.
6. (Optional) Briefly show `/docs` to demonstrate the API.

Free screen recorders: **OBS Studio** (Windows/Mac/Linux, free), the
built-in **Screenshot toolbar → Screen Recording** on macOS
(Cmd+Shift+5), or **Xbox Game Bar** (Win+G) on Windows. Export as MP4
and upload to YouTube (unlisted) or Google Drive, then include that
link alongside your GitHub link in your submission.

## Notes

- If `GOOGLE_API_KEY` isn't set, the AI functions return a friendly
  error message in-place rather than crashing the app.
- SQLite database file (`fitbuddy.db`) is created automatically on
  first run and is git-ignored.

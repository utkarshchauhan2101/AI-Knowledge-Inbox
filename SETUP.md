# notes-rag — Setup Instructions

Complete setup for a **fresh machine**, Mac or Windows. Follow top to bottom.
Where commands differ by OS, both are shown.

The app has two parts that run at the same time in **two terminals**:
- **backend** — Python API (port 8000)
- **frontend** — React UI (port 5173)

---

## 0. Prerequisites (install these first)

### Python 3.11

**Use Python 3.11 specifically — not 3.12/3.13/3.14.** Newer versions may not
have prebuilt packages (numpy in particular) and will try to compile from
source, which fails on many machines. 3.11 has ready-made installers for every
OS.

- **Mac / Windows:** download the installer from
  https://www.python.org/downloads/release/python-3119/
  - Mac: "macOS 64-bit universal2 installer" (`.pkg`)
  - Windows: "Windows installer (64-bit)" (`.exe`) — during install, tick
    **"Add python.exe to PATH"**.
- Verify:
  - Mac/Linux: `python3.11 --version` → should print `Python 3.11.9`
  - Windows: `py -3.11 --version` → should print `Python 3.11.9`

### Node.js 18+ (for the frontend)

- Download the **LTS** installer from https://nodejs.org
- Verify: `node --version` (must be 18 or higher) and `npm --version`

### Git (only if cloning; skip if you have the project as a zip)

- https://git-scm.com/downloads

---

## 1. Get a Gemini API key

1. Go to https://aistudio.google.com
2. Sign in with a Google account.
3. Click **Get API key → Create API key**. No credit card required.
4. Copy the key.

**Note on key format:** as of 2026, Google issues **Auth keys that start with
`AQ.`** (not the older `AIza` format). That is expected and correct. This app
uses Google's native SDK, which supports `AQ.` keys. Keep the key private — it
goes in a file that is never committed to git.

---

## 2. Get the project

Either unzip the provided `notes-rag.zip`, or clone the repo:

```bash
git clone <your-repo-url>
cd notes-rag        # or whatever the project folder is named
```

The project has two folders: `backend/` and `frontend/`.

---

## 3. Backend setup (terminal 1)

### 3a. Create and activate a virtual environment

**Mac / Linux:**
```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
cd backend
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
```

After activating, your prompt shows `(.venv)`. Confirm the version:
```bash
python --version        # must say 3.11.x
```

### 3b. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

On Python 3.11 these install as prebuilt wheels (no compiling). If you see a
long compile that ends in an error, you are almost certainly on the wrong
Python version — go back to step 0 and use 3.11.

### 3c. Add your API key

Create a file named `.env` inside `backend/` containing your key.

**Mac / Linux:**
```bash
printf 'GEMINI_API_KEY=%s\n' 'PASTE_YOUR_AQ_KEY_HERE' > .env
```

**Windows (PowerShell):**
```powershell
'GEMINI_API_KEY=PASTE_YOUR_AQ_KEY_HERE' | Out-File -Encoding ascii .env
```

Or just create `backend/.env` in any editor with one line:
```
GEMINI_API_KEY=AQ.Ab...your-full-key...
```
No quotes, no spaces around `=`, the whole key on one line.

### 3d. Confirm the model names

Open `backend/app/config.py` and check these two lines. Current working values:
```python
embed_model: str = "gemini-embedding-001"
chat_model: str = "gemini-3.6-flash"
```
Google retires model names over time. If a request later fails with
"model not found", run this to list what your key can use, then update the two
lines above (venv active, inside `backend/`):
```bash
python -c "
from app.config import settings
from google import genai
c = genai.Client(api_key=settings.gemini_api_key)
for m in c.models.list(): print(m.name)
"
```

### 3e. Start the backend

```bash
uvicorn app.main:app --reload
```

You should see `vector index loaded: 0 chunks` and `startup complete`.
Leave this terminal running.

Quick check in a browser:
- http://localhost:8000/health → `{"status":"ok"}`
- http://localhost:8000/docs → interactive API docs

---

## 4. Frontend setup (terminal 2)

Open a **second** terminal (leave the backend running in the first).

```bash
cd frontend
npm install
npm run dev
```

Open the URL it prints: http://localhost:5173

---

## 5. Test it works (in order)

1. **Add a note.** Keep "note" selected, type e.g.
   *"My cat's name is Mochi and she is three years old."* → Save. It appears in
   the saved-items list.
2. **Ask an answerable question.** Type *"What is my cat's name?"* → you get an
   answer mentioning Mochi, with a source snippet and score.
3. **Ask an unanswerable question.** Type *"What is the capital of France?"* →
   it should say it doesn't know. This proves answers are grounded in your saved
   content, not the model's general knowledge.
4. **Add a URL.** Switch to "url", paste a plain article URL (a blog post,
   documentation page, or news article works well) → Save → then ask about it.

If all four behave, the app works.

---

## Troubleshooting

**`pip install` starts compiling numpy and fails** (errors mentioning `meson`,
`ninja`, or `_knot_mask32`)
You are on Python 3.12+ where no prebuilt wheel exists yet. Delete the venv,
install **Python 3.11**, and recreate the venv with it (step 3a).

**Backend: `gemini_api_key Field required`**
`backend/.env` is missing or in the wrong place. It must be at `backend/.env`
and contain `GEMINI_API_KEY=...`. Restart uvicorn after creating it (a running
server does not pick up a new `.env` automatically).

**Backend: `Invalid Auth key` / `API_KEY_INVALID`**
The key is wrong, truncated, or stale. Confirm `.env` has the full `AQ.` key on
one line. Restart uvicorn. (This app uses Google's native SDK, which accepts
`AQ.` keys; the older OpenAI-compatible endpoint does not.)

**Ask fails: `model ... is no longer available`**
Google retired that chat model. Use the model name from the error (or the
`models.list()` command in 3d) and update `chat_model` in `app/config.py`.
Restart uvicorn.

**URL fails: `403 Forbidden`**
The site blocks automated requests. The app sends a browser User-Agent to get
past most sites, but some (with stronger bot protection, paywalls, or
login walls) will still refuse. Try a different, simpler URL.

**URL fails: `no readable content extracted`**
The page has no extractable article text (often a JavaScript-heavy single-page
app). Try a plain server-rendered page instead.

**Frontend: PostCSS / "Cannot find native binding" on `npm run dev`**
Remove and reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json    # Windows: rmdir /s node_modules & del package-lock.json
npm install
npm run dev
```

**Frontend loads but has no styling**
Tailwind isn't generating classes. Confirm `frontend/tailwind.config.js` has
`content: ["./index.html", "./src/**/*.{js,jsx}"]`, that
`frontend/src/main.jsx` imports `./index.css`, then fully restart
`npm run dev` and hard-reload the browser (Cmd/Ctrl+Shift+R).

**Frontend actions all error**
The backend isn't running or is on another port. Confirm terminal 1 shows
uvicorn on port 8000 and that http://localhost:8000/health responds.

**Reset all saved data**
Stop the backend and delete the database:
```bash
rm backend/notes.db        # Windows: del backend\notes.db
```

---

## What NOT to do

- Don't commit `backend/.env` (your key). It is gitignored — keep it that way.
- Don't run backend and frontend in the same terminal; both must stay running.
- Don't use Python 3.12+ for this project unless you want to debug wheels.

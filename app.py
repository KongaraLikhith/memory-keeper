import requests, json, os, asyncio, time
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List
import uvicorn

TRANSCRIBE_URL = "https://likhith0715--memory-keeper-transcribe-audio.modal.run"
PHOTO_URL = "https://likhith0715--memory-keeper-describe-photo.modal.run"
BOOK_URL = "https://likhith0715--memory-keeper-build-memory-book.modal.run"

# Storage directory — persists on HF Spaces if mounted, otherwise local to container
STORAGE_DIR = "./data/memories"
os.makedirs(STORAGE_DIR, exist_ok=True)

def profile_path(name: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name).strip().lower()
    return f"{STORAGE_DIR}/{safe}.json"

def load_profile(name: str) -> dict:
    path = profile_path(name)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"name": name, "transcripts": [], "photo_descriptions": [], "sessions": 0, "history": []}

def save_profile(profile: dict):
    with open(profile_path(profile["name"]), "w") as f:
        json.dump(profile, f, indent=2)

def list_profiles() -> list:
    profiles = []
    for fname in os.listdir(STORAGE_DIR):
        if fname.endswith(".json"):
            with open(f"{STORAGE_DIR}/{fname}") as f:
                try:
                    p = json.load(f)
                    profiles.append({
                        "name": p["name"],
                        "sessions": p.get("sessions", 0),
                        "memories": len(p.get("transcripts", [])),
                        "photos": len(p.get("photo_descriptions", []))
                    })
                except: pass
import gradio as gr

fast_app = gr.Server()

async def cleanup_old_memories():
    """Background task to delete profile JSONs older than 48 hours."""
    while True:
        now = time.time()
        for fname in os.listdir(STORAGE_DIR):
            if fname.endswith(".json"):
                path = os.path.join(STORAGE_DIR, fname)
                try:
                    if now - os.path.getmtime(path) > 48 * 3600:
                        os.remove(path)
                except Exception:
                    pass
        await asyncio.sleep(3600)  # Check every hour

@fast_app.on_event("startup")
async def startup_event():
    asyncio.create_task(cleanup_old_memories())

@fast_app.get("/", response_class=HTMLResponse)
def index():
    return open("index.html").read()

@fast_app.get("/profiles")
def get_profiles():
    return JSONResponse(list_profiles())

@fast_app.get("/profile/{name}")
def get_profile(name: str):
    return JSONResponse(load_profile(name))

@fast_app.delete("/profile/{name}")
def delete_profile(name: str):
    path = profile_path(name)
    if os.path.exists(path):
        os.remove(path)
    return JSONResponse({"ok": True})

@fast_app.post("/run")
async def run(
    name: str = Form(...),
    text: str = Form(""),
    audios: List[UploadFile] = File(default=[]),
    photos: List[UploadFile] = File(default=[])
):
    # Load existing profile
    profile = load_profile(name)
    new_transcripts = []
    new_photos = []

    if text.strip():
        new_transcripts.append(text)

    for audio in audios:
        if audio and audio.filename:
            audio_bytes = await audio.read()
            if audio_bytes:
                resp = requests.post(
                    TRANSCRIBE_URL, data=audio_bytes,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=300
                )
                if resp.status_code == 200:
                    new_transcripts.append(f"[Voice]: {resp.json()}")

    for photo in photos:
        if photo and photo.filename:
            photo_bytes = await photo.read()
            if photo_bytes:
                resp = requests.post(
                    PHOTO_URL, data=photo_bytes,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=300
                )
                if resp.status_code == 200:
                    new_photos.append(resp.json())

    if not new_transcripts and not new_photos:
        return JSONResponse({"error": "No memories provided"}, status_code=400)

    # Accumulate into profile
    profile["transcripts"].extend(new_transcripts)
    profile["photo_descriptions"].extend(new_photos)
    profile["sessions"] = profile.get("sessions", 0) + 1
    save_profile(profile)

    # Build book from ALL accumulated memories
    if not profile["transcripts"]:
        profile["transcripts"].append(f"Photos were shared of {name}.")

    resp = requests.post(BOOK_URL, json={
        "name": name,
        "transcripts": profile["transcripts"],
        "photo_descriptions": profile["photo_descriptions"]
    }, timeout=600)

    result = resp.json()

    # Append to history and save again
    history_entry = {
        "session": profile["sessions"],
        "timestamp": datetime.now().strftime("%b %d, %Y - %H:%M"),
        "timeline": result.get("timeline", ""),
        "chapter": result.get("chapter", ""),
        "letter": result.get("letter", ""),
        "people": result.get("people", "")
    }
    profile.setdefault("history", []).append(history_entry)
    save_profile(profile)

    result["sessions"] = profile["sessions"]
    result["total_memories"] = len(profile["transcripts"])
    result["total_photos"] = len(profile["photo_descriptions"])
    result["history"] = profile["history"]
    return JSONResponse(result)

if __name__ == "__main__":
    fast_app.launch(server_name="0.0.0.0", server_port=7860)

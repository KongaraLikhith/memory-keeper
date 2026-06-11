# Memory Keeper

A lightweight, serverless AI pipeline that acts as a personal digital archive. Built during the Hugging Face Build Small Hackathon, Memory Keeper takes disparate personal media inputs—like raw audio voice notes and images—and processes them through specialized serverless models to generate structured, contextual "memory books."

Instead of maintaining heavy, always-on backend infrastructure, the core pipeline is broken into independent, on-demand serverless tasks managed completely via Modal.

## Architecture Overview

The system is designed with a decoupled frontend-backend architecture:
- **Frontend / API Layer** (`app.py`, `index.html`): A clean, professional user interface to manage profiles, upload media files, and display consolidated timelines. Built with FastAPI and vanilla HTML/JS, running in a Docker container on Hugging Face Spaces.
- **Compute Engine** (`modal_inference.py`): An orchestrated serverless application running on Modal that triggers specialized tasks (using A10G GPUs) only when needed, keeping memory overhead minimal and performance high.

### Project Structure
- `app.py` - FastAPI server routing requests and managing state.
- `index.html` - Professional frontend UI.
- `modal_inference.py` - Core Modal serverless orchestration for AI models.
- `Dockerfile` - Deployment configuration for Hugging Face Spaces.
- `requirements.txt` - Project dependencies.

## Core Engine Functions

Under the main memory-keeper container app, tasks are isolated into discrete, scalable serverless functions on Modal:

- `describe_photo`: Processes uploaded images using `Salesforce/blip-image-captioning-base` to extract semantic context and visual elements.
- `transcribe_audio`: Spins up transient GPU workers to transcribe spoken audio clips using `openai/whisper`.
- `build_memory_book`: The orchestrator LLM function (using `Qwen2.5-7B`) that compiles the structural logs, updates profiles, and outputs the final historical narrative, timelines, and letters.

## Deployment Instructions

### 1. Backend (Modal)
You need a Modal account to run the inference tasks. Install the Modal CLI locally and authenticate your environment:
```bash
pip install modal
python -m modal setup
```
To deploy the backend endpoints permanently so they can process traffic from the UI:
```bash
modal deploy modal_inference.py
```

### 2. Frontend (Hugging Face Spaces)
The frontend is designed to be hosted seamlessly on Hugging Face Spaces as a Docker Space.

1. Create a new Space on Hugging Face.
2. Choose **Docker** -> **Blank** as the SDK.
3. Connect this GitHub repository directly to your Hugging Face Space.
   *(Note: The included `.dockerignore` file strictly prevents `modal_inference.py` and local testing data from being copied into the final Hugging Face Docker image, keeping your frontend deployment incredibly lightweight and secure).*
4. The Space will automatically build the Dockerfile and run `app.py` on port 7860.

## Local Development
To run the frontend locally for testing:
```bash
pip install -r requirements.txt
uvicorn app:fast_app --host 0.0.0.0 --port 7860
```
Open your local browser to `http://localhost:7860` to interact with the frontend.

# Memory Keeper 🌲 *(Track: Thousand Token Wood)*

🚀 **[Live App (Hugging Face Space)](https://huggingface.co/spaces/build-small-hackathon/memory-keeper)** | 🎥 **[Watch the Demo Video](https://drive.google.com/file/d/1MCXUOhq1C8chFCno9T7GjPm8BOkAZX_X/view?usp=sharing)** | 📝 **[LinkedIn Post](https://www.linkedin.com/posts/likhith-kongara-049b87212_github-kongaralikhithmemory-keeper-memory-activity-7470707614285410304-tbUS)**

A lightweight, serverless AI pipeline that acts as a personal digital archive. Built during the Hugging Face Build Small Hackathon, Memory Keeper takes disparate personal media inputs—like raw audio voice notes and images—and processes them through specialized serverless models to generate structured, contextual "memory books."

Instead of maintaining heavy, always-on backend infrastructure, the core pipeline is broken into independent, on-demand serverless tasks managed completely via Modal.

🔌 **Off the Grid Badge:** This application uses **zero proprietary cloud APIs** (no OpenAI, Anthropic, Gemini, etc.). Every single AI operation is performed using open-weight models (`Qwen2.5-7B`, `Whisper-base`, `BLIP-base`) hosted on independent Modal serverless endpoints.

## Architecture Overview

The system is designed with a decoupled frontend-backend architecture:
- **Frontend / API Layer** (`app.py`, `index.html`): A clean, professional user interface to manage profiles, upload media files, and display consolidated timelines. Built using `gradio.Server` to leverage Custom UI functionality, running in a Docker container on Hugging Face Spaces.
- **Compute Engine**: An orchestrated serverless application running on Modal that triggers specialized tasks (using A10G GPUs) only when needed, keeping memory overhead minimal and performance high. The AI endpoints are external and pre-deployed.

### Project Structure
- `app.py` - Gradio Server routing requests and managing state.
- `index.html` - Professional custom frontend UI.
- `Dockerfile` - Deployment configuration for Hugging Face Spaces.
- `requirements.txt` - Project dependencies.

## Core Engine Functions

Under the main memory-keeper container app, tasks are isolated into discrete, scalable serverless functions on Modal:

- `describe_photo`: Processes uploaded images using `Salesforce/blip-image-captioning-base` to extract semantic context and visual elements.
- `transcribe_audio`: Spins up transient GPU workers to transcribe spoken audio clips using `openai/whisper`.
- `build_memory_book`: The orchestrator LLM function (using `Qwen2.5-7B`) that compiles the structural logs, updates profiles, and outputs the final historical narrative, timelines, and letters.

## Deployment Instructions

### Hugging Face Spaces (Frontend)
The frontend is designed to be hosted seamlessly on Hugging Face Spaces as a Docker Space.

1. Create a new Space on Hugging Face.
2. Choose **Docker** -> **Blank** as the SDK.
3. Connect this GitHub repository directly to your Hugging Face Space.
4. The Space will automatically build the Dockerfile and launch the Gradio custom server on port 7860.

## Local Development
To run the frontend locally for testing:
```bash
pip install -r requirements.txt
python app.py
```
Open your local browser to `http://127.0.0.1:7860` to interact with the frontend.

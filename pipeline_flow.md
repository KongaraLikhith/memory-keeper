# Agent Trace: Memory Keeper Pipeline Flow

This document outlines the end-to-end data flow and architectural pipeline for the Memory Keeper application.

## 📡 Pipeline Architecture

The system operates strictly "Off the Grid" using entirely open-weight models hosted via serverless functions. **No proprietary cloud LLM APIs (like OpenAI, Anthropic, or Gemini) are used.**

### Step 1: User Input (Hugging Face Spaces)
1. The user interacts with the completely custom `gradio.Server` interface running in a Docker container on Hugging Face Spaces.
2. The user uploads a photo, records an audio voice note, or types a text memory.
3. The FastAPI backend running on HF Spaces receives the multipart form data.

### Step 2: Parallel Perception (Modal Serverless)
The backend securely offloads the heavy perception tasks to transient Modal endpoints powered by A10G GPUs.
- **Audio Pipeline:** The audio file is sent to the `transcribe_audio` Modal endpoint. A serverless worker spins up, runs `openai/whisper-base` entirely locally, and returns the transcribed text.
- **Visual Pipeline:** The photo is sent to the `describe_photo` Modal endpoint. A worker runs `Salesforce/blip-image-captioning-base` to extract rich visual context and returns the semantic description.

### Step 3: Synthesis & Generation (Modal Serverless)
The extracted text transcripts, visual descriptions, and the user's historical profile data are gathered by the HF Spaces backend and sent to the core orchestrator.
- **LLM Pipeline:** The `build_memory_book` Modal endpoint spins up with `Qwen/Qwen2.5-7B-Instruct`.
- The LLM processes the raw contexts and generates structured JSON containing a chronological "Timeline", a narrative "Story", and a personalized "Letter".

### Step 4: Storage & Delivery
1. The HF Space backend receives the structured JSON from Qwen2.5.
2. The data is saved locally to the container's ephemeral storage (managed by an asynchronous 48-hour cleanup task).
3. The generated "Memory Book" is rendered beautifully in the custom HTML/CSS UI for the user to view and download.

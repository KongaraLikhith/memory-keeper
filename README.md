# memory-keeper

A lightweight, serverless AI pipeline that acts as a personal digital archive. Built during the Hugging Face Build Small Hackathon, memory-keeper takes disparate personal media inputs—like raw audio voice notes and images—and processes them through specialized serverless models to generate structured, contextual "memory books."

Instead of maintaining heavy, always-on backend infrastructure, the core pipeline is broken into independent, on-demand serverless tasks managed completely via Modal.

## Architecture Overview

The system is designed with a decoupled frontend-backend architecture:
- Frontend (app.py, index.html): A clean user interface to manage profile chips, upload media files, and display consolidated timelines.
- Compute Engine (modal_inference.py): An orchestrated serverless application running on Modal that triggers specialized tasks only when needed, keeping memory overhead minimal and performance high.

Project Structure:
- app.py -> Main UI or application router
- index.html -> Profile management and media upload UI
- modal_inference.py -> Core Modal serverless orchestration & tool execution
- requirements.txt -> Project dependencies

## Core Engine Functions

Under the main memory-keeper container app, tasks are isolated into discrete, scalable serverless functions:

- describe_photo: Processes uploaded images using efficient vision-language models to extract semantic context, visual elements, and environmental details.
- transcribe_audio: Spins up transient GPU workers to transcribe spoken audio clips and voice memos (e.g., using Whisper architectures) into clean text.
- generate: An LLM-driven synthesis step that ingests raw texts, transcriptions, and image metadata to combine them into an ordered narrative.
- build_memory_book: The orchestrator function that compiles the structural logs, updates profiles, and outputs the final historical log.

## Local Development & Deployment

### Prerequisites

You need a Modal account to run the inference tasks. Install the Modal CLI locally and authenticate your environment:

pip install modal
python3 -m modal setup

### Running the App Ephemerally

To spin up a live interactive development session where containers log directly to your terminal and auto-terminate when you stop the command, run:

modal run modal_inference.py

### Deploying the Production Build

To register the application permanently in the cloud so that the endpoints stay alive and ready to process traffic from your interface, deploy the app:

modal deploy modal_inference.py

## UI Setup

The interface tracks separate user profiles using dynamic HTML chips. Run the application layer to host the frontend:

python3 app.py

Open your local browser to interact with the frontend, upload assets, and start generating memory volumes.

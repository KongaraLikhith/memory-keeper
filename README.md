# Memory Keeper 🌲 *(Track: Thousand Token Wood)*

💻 **[GitHub Repository](https://github.com/KongaraLikhith/memory-keeper)** | 🎥 **[Watch the Demo Video](https://drive.google.com/file/d/1MCXUOhq1C8chFCno9T7GjPm8BOkAZX_X/view?usp=sharing)** | 📝 **[LinkedIn Post](https://www.linkedin.com/posts/likhith-kongara-049b87212_github-kongaralikhithmemory-keeper-memory-activity-7470707614285410304-tbUS)**

## 📖 The Story: Why I Built Memory Keeper

We all have those little moments—a beautiful sunset, a fleeting thought we record as a voice note, or a random photo that captures a specific feeling. But more often than not, these memories get lost in the endless scroll of our camera rolls or the unorganized abyss of our voice memos. 

I built **Memory Keeper** for the Hugging Face "Build Small" Hackathon because I wanted a whimsical, personal digital archive that actually *understands* these fragments. I wanted a tool that could take my raw audio notes and spontaneous photos, and weave them together into beautifully structured storybooks and letters to my future self. 

I chose the **Thousand Token Wood** track because this project isn't just about utility; it’s about creating something deeply personal, experimental, and delightful.

---

## ✨ The Magic: How It Works

Memory Keeper is a multi-modal AI pipeline that acts as your personal archivist:
1. **Upload:** You upload a photo, record a voice note, or simply type a thought into the custom glassmorphic UI.
2. **Perception:** The backend immediately spins up specialized "small models" to perceive the inputs. It transcribes the audio and generates rich semantic descriptions of the photos.
3. **Synthesis:** A central orchestrator LLM takes all these pieces, looks at your history, and writes a narrative timeline, a structured story, and a personal letter summarizing the memory. 

---

## 🏆 Hackathon Bonuses

### 🔌 Off the Grid Badge
This application uses **zero proprietary cloud APIs** (no OpenAI, Anthropic, Gemini, etc.). Every single AI operation is performed using open-weight models hosted on independent, transient serverless endpoints:
- **Language:** `Qwen/Qwen2.5-7B-Instruct`
- **Audio:** `openai/whisper-base`
- **Vision:** `Salesforce/blip-image-captioning-base`

### 📡 Sharing is Caring Badge
Curious how the data flows? Check out the [`pipeline_flow.md`](./pipeline_flow.md) document in this repository for a complete architectural breakdown of the agentic pipeline.

---

## 🏗️ Architecture & Deployment

To keep the application incredibly lightweight while maintaining a premium feel, the system uses a decoupled frontend-backend architecture:

- **Frontend (Hugging Face Spaces):** A completely custom HTML/CSS UI built on top of `gradio.Server`. This bypasses the standard Gradio blocks to deliver a stunning visual experience while strictly adhering to the hackathon's Gradio requirement. 
- **Compute Engine (Modal):** Heavy AI perception tasks are offloaded to A10G GPUs via Modal. These endpoints are entirely serverless, meaning they scale to zero when not in use, keeping the memory footprint minimal.

### Local Development
To run the frontend locally for testing:
```bash
pip install -r requirements.txt
python app.py
```
Open your local browser to `http://127.0.0.1:7860` to interact with the frontend.

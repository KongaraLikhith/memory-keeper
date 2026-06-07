
import modal
from fastapi import Request

app = modal.App("memory-keeper")

image = (
    modal.Image.from_registry("nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04", add_python="3.11")
    .apt_install("ffmpeg")  # ← this was missing
    .pip_install("torch", "torchvision", extra_index_url="https://download.pytorch.org/whl/cu121")
    .pip_install(
        "transformers>=4.40.0",
        "accelerate>=0.27.0",
        "huggingface_hub",
        "openai-whisper",
        "Pillow",
        "numpy",
        "fastapi[standard]"
    )
)

volume = modal.Volume.from_name("qwen-7b-hf-vol", create_if_missing=True)
MODEL_DIR = "/models/qwen-7b"

@app.function(image=image, gpu="A10G", volumes={"/models": volume}, timeout=600)
@modal.fastapi_endpoint(method="POST")
def generate(item: dict) -> str:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    prompt = item["prompt"]
    max_tokens = item.get("max_tokens", 512)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR, torch_dtype=torch.float16, device_map="cuda"
    )
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt").to("cuda")
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_tokens,
            temperature=0.7, do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    output_ids = outputs[0][len(inputs.input_ids[0]):]
    return tokenizer.decode(output_ids, skip_special_tokens=True)

@app.function(image=image, gpu="A10G", timeout=300)
@modal.fastapi_endpoint(method="POST")
async def transcribe_audio(request: Request) -> str:
    import whisper, tempfile, os
    audio_data = await request.body()
    model = whisper.load_model("base")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_data)
        tmp_path = f.name
    result = model.transcribe(tmp_path)
    os.unlink(tmp_path)
    return result["text"]

@app.function(image=image, gpu="A10G", timeout=300)
@modal.fastapi_endpoint(method="POST")
async def describe_photo(request: Request) -> str:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    from PIL import Image
    import torch, io
    image_data = await request.body()
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base", torch_dtype=torch.float16
    ).to("cuda")
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    inputs = processor(image, return_tensors="pt").to("cuda", torch.float16)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=100)
    return processor.decode(out[0], skip_special_tokens=True)

@app.function(image=image, gpu="A10G", volumes={"/models": volume}, timeout=600)
@modal.fastapi_endpoint(method="POST")
def build_memory_book(item: dict) -> dict:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    name = item["name"]
    transcripts = item["transcripts"]
    photo_descriptions = item["photo_descriptions"]
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR, torch_dtype=torch.float16, device_map="cuda"
    )
    def ask(prompt):
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer([text], return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = model.generate(
                **inputs, max_new_tokens=512,
                temperature=0.7, do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        output_ids = outputs[0][len(inputs.input_ids[0]):]
        return tokenizer.decode(output_ids, skip_special_tokens=True)
    context = f"""
Person: {name}
Memories: {chr(10).join(transcripts)}
Photos: {chr(10).join(photo_descriptions)}
"""
    return {
        "timeline": ask(f"{context}\nWrite a timeline of key life events. Format: [Period] - Event"),
        "chapter": ask(f"{context}\nWrite a warm 3-paragraph narrative about {name}'s life."),
        "letter": ask(f"{context}\nWrite a heartfelt letter from {name} to future generations."),
        "people": ask(f"{context}\nList and describe the important people in {name}'s memories.")
    }

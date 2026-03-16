"""
FastAPI service for LLM inference using HuggingFace Transformers + PyTorch.
Cross-platform compatible (Mac, Linux, Windows).
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import logging
from transformers import pipeline
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Rowan LLM Service")

# Model info - Qwen1.5-0.5B: 500M params, ~300MB download, ultra-light
MODEL = "Qwen/Qwen1.5-0.5B-Chat"
DEVICE = 0 if torch.cuda.is_available() else -1  # Use GPU if available, else CPU

# Global pipe (loaded once on startup)
pipe = None


@app.on_event("startup")
async def load_model():
    """Load Phi-2 model on startup"""
    global pipe
    try:
        logger.info(f"Loading {MODEL} on device {DEVICE}...")
        pipe = pipeline(
            "text-generation",
            model=MODEL,
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device=DEVICE,
            trust_remote_code=True,
        )
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


class GenerateRequest(BaseModel):
    """Request model for generation"""
    prompt: str
    max_length: int = 256


class GenerateResponse(BaseModel):
    """Response model for generation"""
    response: str


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    """Generate text using Qwen model"""
    if pipe is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        logger.info(f"[LLM API] 🔵 STEP 1: Received generation request")
        logger.info(f"[LLM API] Prompt length: {len(request.prompt)} chars")
        logger.info(f"[LLM API] Prompt: {request.prompt}")
        logger.info(f"[LLM API] Max tokens: {request.max_length}")

        # Determine if this is a JSON task
        is_json_task = "JSON" in request.prompt or "json" in request.prompt
        logger.info(f"[LLM API] JSON task detected: {is_json_task}")

        logger.info(f"[LLM API] 🔵 STEP 2: Calling model pipeline...")
        # Generate text with better defaults for JSON tasks
        outputs = pipe(
            request.prompt,
            max_new_tokens=128,  # Reduced for JSON tasks
            num_return_sequences=1,
            do_sample=True,  # Use sampling for better generation
            temperature=0.7,
            top_p=0.9,
        )

        logger.info(f"[LLM API] 🔵 STEP 3: Model returned output")
        logger.info(f"[LLM API] Full output length: {len(outputs[0]['generated_text'])} chars")

        # Extract generated text (skip the prompt part)
        full_text = outputs[0]["generated_text"]
        logger.info(f"[LLM API] Full text: '{full_text}'")

        response_text = full_text[len(request.prompt):].strip()
        logger.info(f"[LLM API] Extracted response (after prompt): '{response_text}'")
        logger.info(f"[LLM API] Response length: {len(response_text)} chars")

        logger.info(f"[LLM API] ✅ STEP 4: Returning response")
        return GenerateResponse(response=response_text)
    except Exception as e:
        logger.error(f"[LLM API] ❌ Generation failed: {e}")
        import traceback
        logger.error(f"[LLM API] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "model": MODEL, "device": "GPU" if torch.cuda.is_available() else "CPU"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

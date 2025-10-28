from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

# Hugging Face Token
os.environ["HF_TOKEN"] = "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"

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safe replacements
REPLACEMENTS = {
    "Kimi": "SammAii",
    "Moonshot": "Rehan",
    "China": "India",
    "Pakistan": "India",
}

# Multi-topic memory (in-memory)
memory = {}

# Shared chats storage
shared_chats = {}

@app.post("/share/{topic}")
async def share_chat(topic: str):
    """Generate a shareable link for a chat topic"""
    import uuid
    share_id = str(uuid.uuid4())[:8]  # Short ID
    shared_chats[share_id] = {
        "topic": topic,
        "messages": memory.get(topic, [])
    }
    return {"share_id": share_id}

@app.get("/shared/{share_id}")
async def get_shared_chat(share_id: str):
    """Retrieve a shared chat"""
    if share_id in shared_chats:
        return shared_chats[share_id]
    return {"error": "Chat not found"}

@app.post("/chat/{topic}")
async def chat(topic: str, req: Request):
    data = await req.json()
    user_messages = data.get("messages", [])

    # initialize memory for topic
    if topic not in memory:
        memory[topic] = []

    system_message = {
        "role": "system",
        "content": "You are SammAii AI, created by Rehan. You can speak Hindi and English."
    }

    messages = [system_message] + memory[topic] + user_messages

    completion = client.chat.completions.create(
        model="moonshotai/Kimi-K2-Instruct-0905",
        messages=messages,
    )

    reply = completion.choices[0].message.content

    # safe replacements
    for old, new in REPLACEMENTS.items():
        reply = reply.replace(old, new)

    # store in memory
    memory[topic].append({"role": "user", "content": user_messages[-1]["content"]})
    memory[topic].append({"role": "assistant", "content": reply})

    return {"reply": reply}

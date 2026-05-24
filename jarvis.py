"""
JARVIS — Personal Voice AI Agent
Stack: Whisper (STT) · Claude Haiku (LLM) · ElevenLabs (TTS)
OS: macOS
"""

import os
import json
import time
import threading
import tempfile
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import anthropic

from skills.web_search import web_search
from skills.open_app import open_app
from skills.reminders import set_reminder, get_time
from memory.store import load_memory, save_memory

WAKE_WORDS = ["hey jarvis", "jarvis", "hey j"]
SAMPLE_RATE = 16000
RECORD_SECONDS = 6
SILENCE_THRESHOLD = 0.01

print("⚡ Loading Whisper model (first run takes ~30s)...")
stt_model = whisper.load_model("base")
print("✅ Whisper ready.\n")

anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "ErXwobaYiN019PkySvjV")  # Antoni — deep, calm

SYSTEM_PROMPT = f"""You are JARVIS, a highly intelligent, calm, and efficient personal AI assistant — inspired by the AI from Iron Man. You run locally on your user's MacBook.

Your personality:
- Concise and precise. Never verbose. One or two sentences unless detail is truly needed.
- Slightly witty but never sarcastic. Professional but warm.
- Address the user as "sir" occasionally, but don't overdo it.
- You are aware of the current date and time.

Your capabilities:
- Answer general knowledge questions
- Search the web for current information
- Open apps and files on the Mac
- Tell the time, set reminders
- Remember context from this conversation

Current date/time: {{datetime}}

Rules:
- Never say "As an AI..." or "I cannot..." — just do it or offer an alternative.
- Keep responses short enough to be spoken aloud naturally (under 40 words unless asked for detail).
- When using a tool, don't narrate it — just respond with the result.
"""

TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for current information, news, facts, or anything that may have changed recently.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "open_app",
        "description": "Open an application or file on the Mac.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "App name (e.g. 'Spotify', 'Safari', 'Terminal') or file path"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "get_time",
        "description": "Get the current time and date.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "set_reminder",
        "description": "Set a reminder for a specific time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "What to remind about"},
                "minutes": {"type": "integer", "description": "How many minutes from now"}
            },
            "required": ["message", "minutes"]
        }
    }
]

def record_audio():
    """Record audio from microphone."""
    print("🎙️  Listening...")
    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()
    return audio.flatten()

def transcribe(audio_array):
    """Convert audio to text via Whisper."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav.write(f.name, SAMPLE_RATE, (audio_array * 32767).astype(np.int16))
        result = stt_model.transcribe(f.name, language="en", fp16=False)
    return result["text"].strip().lower()

def speak_elevenlabs(text):
    """Convert text to speech via ElevenLabs and play it."""
    import requests
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{elevenlabs_voice_id}"
    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.6, "similarity_boost": 0.85}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(response.content)
            subprocess.run(["afplay", f.name], check=True)
    else:
        print(f"[TTS error] {response.status_code}: {response.text}")
        speak_fallback(text)

def speak_fallback(text):
    """macOS built-in TTS as fallback."""
    subprocess.run(["say", "-v", "Alex", text])

def speak(text):
    print(f"🤖 JARVIS: {text}")
    if elevenlabs_api_key:
        speak_elevenlabs(text)
    else:
        speak_fallback(text)

def execute_tool(tool_name, tool_input):
    """Route tool calls to skill functions."""
    if tool_name == "web_search":
        return web_search(tool_input["query"])
    elif tool_name == "open_app":
        return open_app(tool_input["name"])
    elif tool_name == "get_time":
        return get_time()
    elif tool_name == "set_reminder":
        return set_reminder(tool_input["message"], tool_input["minutes"])
    return "Tool not found."

def ask_jarvis(user_input, conversation_history):
    """Send message to Claude Haiku with tool support."""
    conversation_history.append({"role": "user", "content": user_input})

    system = SYSTEM_PROMPT.replace("{datetime}", datetime.now().strftime("%A, %B %d %Y, %I:%M %p"))

    while True:
        response = anthropic_client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            system=system,
            tools=TOOLS,
            messages=conversation_history
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            assistant_content = response.content

            for block in response.content:
                if block.type == "tool_use":
                    print(f"🔧 Using tool: {block.name}({block.input})")
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            conversation_history.append({"role": "assistant", "content": assistant_content})
            conversation_history.append({"role": "user", "content": tool_results})

        else:
            reply = ""
            for block in response.content:
                if hasattr(block, "text"):
                    reply += block.text
            conversation_history.append({"role": "assistant", "content": reply})
            return reply.strip(), conversation_history

def contains_wake_word(text):
    return any(w in text for w in WAKE_WORDS)

def main():
    print("=" * 50)
    print("  J.A.R.V.I.S. — Online")
    print(f"  {datetime.now().strftime('%A, %B %d %Y')}")
    print("=" * 50)
    speak("JARVIS online. Ready when you are, sir.")

    conversation_history = load_memory()
    wake_mode = False
    wake_timeout = 0

    while True:
        try:
            audio = record_audio()

            if np.max(np.abs(audio)) < SILENCE_THRESHOLD:
                continue

            text = transcribe(audio)
            if not text or len(text) < 3:
                continue

            print(f"👂 Heard: {text}")

            if contains_wake_word(text):
                wake_mode = True
                wake_timeout = time.time() + 30
                query = text
                for w in WAKE_WORDS:
                    query = query.replace(w, "").strip()
                if not query:
                    speak("Yes, sir?")
                    continue
            elif not wake_mode or time.time() > wake_timeout:
                continue
            else:
                query = text
                wake_timeout = time.time() + 30

            if any(w in query for w in ["goodbye", "exit", "shut down", "shutdown", "go offline"]):
                speak("Shutting down. Goodbye, sir.")
                save_memory(conversation_history)
                break

            reply, conversation_history = ask_jarvis(query, conversation_history)
            speak(reply)
            save_memory(conversation_history)

        except KeyboardInterrupt:
            speak("Shutting down. Goodbye.")
            save_memory(conversation_history)
            break
        except Exception as e:
            print(f"[Error] {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()

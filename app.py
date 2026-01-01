"""Dr. Carlos Cortes Voice-Cloned Chatbot with Lip-Sync Avatar

A Gradio app that lets users converse with Dr. Carlos E. Cortes,
historian and multicultural education pioneer.

Architecture:
- LLM: Gemini via OpenRouter (with bibliography context)
- Voice: ElevenLabs voice clone
- Avatar: Sync Labs lip-sync API
"""

import gradio as gr
import requests
import os
import tempfile
import time
import base64
from pathlib import Path

# Configuration - set via environment variables or Hugging Face Secrets
# REQUIRED: Set these in HF Spaces secrets or .env file
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("VOICE_ID", "")  # Dr. Cortes voice clone ID
SYNC_API_KEY = os.environ.get("SYNC_API_KEY", "")

# Avatar image URL (publicly accessible for Sync Labs)
AVATAR_URL = os.environ.get("AVATAR_URL", "https://raw.githubusercontent.com/charlesmartinedd/dr-cortes-chatbot/main/dr_cortes.jpg")

# Load knowledge base
KNOWLEDGE_BASE_PATH = Path(__file__).parent / "knowledge_base.txt"
if KNOWLEDGE_BASE_PATH.exists():
    KNOWLEDGE_BASE = KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8")
else:
    KNOWLEDGE_BASE = "No knowledge base loaded."

# System prompt - Dr. Cortes persona
SYSTEM_PROMPT = f"""You are Dr. Carlos E. Cortes, a distinguished historian, author, and pioneer in multicultural education. You speak in first person as yourself.

Your background:
- Professor Emeritus of History at the University of California, Riverside
- Author of numerous books and articles on multicultural education, media literacy, and diversity
- Renowned speaker and consultant on issues of diversity and education
- Known for your warm, engaging, and thoughtful communication style

When answering questions:
1. Draw from your published works and experiences documented below
2. Speak as yourself in first person ("In my work...", "I've found that...", "As I wrote in...")
3. Be thoughtful, nuanced, and educational in your responses
4. If asked about topics outside your expertise, acknowledge that gracefully
5. Keep responses conversational but substantive (2-3 sentences for voice - keep it brief for lip-sync)

YOUR PUBLISHED WORKS AND BIBLIOGRAPHY:
{KNOWLEDGE_BASE}

Remember: You ARE Dr. Carlos Cortes. Respond as he would, with his wisdom, experience, and perspective.
IMPORTANT: Keep responses under 100 words for efficient voice/video generation.
"""


def query_llm(message: str, history: list) -> str:
    """Query Gemini via OpenRouter."""

    if not OPENROUTER_API_KEY:
        return "[Error: OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable.]"

    # Build conversation history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for h in history:
        if h[0]:
            messages.append({"role": "user", "content": h[0]})
        if h[1]:
            messages.append({"role": "assistant", "content": h[1]})

    messages.append({"role": "user", "content": message})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.5-pro-preview",
                "messages": messages,
                "max_tokens": 256,  # Keep short for voice
                "temperature": 0.7
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error querying LLM: {str(e)}]"


def generate_voice(text: str) -> tuple[str | None, str | None]:
    """Generate speech using ElevenLabs voice clone.
    Returns (local_path, public_url) - public_url for Sync Labs
    """

    if not ELEVENLABS_API_KEY or not VOICE_ID:
        return None, None

    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            },
            timeout=60
        )

        if response.status_code == 200:
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                f.write(response.content)
                local_path = f.name

            # Upload to tmpfiles.org for public URL (free, temporary hosting)
            try:
                files = {"file": open(local_path, "rb")}
                upload_resp = requests.post("https://tmpfiles.org/api/v1/upload", files=files, timeout=30)
                if upload_resp.status_code == 200:
                    # tmpfiles returns {"data": {"url": "https://tmpfiles.org/123/file.mp3"}}
                    # We need to convert to direct link: https://tmpfiles.org/dl/123/file.mp3
                    url = upload_resp.json().get("data", {}).get("url", "")
                    if url:
                        public_url = url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                        return local_path, public_url
            except Exception as e:
                print(f"Audio upload error: {e}")

            return local_path, None
        else:
            print(f"ElevenLabs error: {response.status_code} - {response.text}")
            return None, None

    except Exception as e:
        print(f"Voice generation error: {e}")
        return None, None


def generate_lipsync_video(audio_url: str, avatar_url: str) -> str | None:
    """Generate lip-sync video using Sync Labs API."""

    if not SYNC_API_KEY or not audio_url or not avatar_url:
        return None

    try:
        # Create generation request
        response = requests.post(
            "https://api.sync.so/v2/generate",
            headers={
                "x-api-key": SYNC_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "model": "lipsync-2",
                "input": [
                    {"type": "video", "url": avatar_url},
                    {"type": "audio", "url": audio_url}
                ]
            },
            timeout=30
        )

        if response.status_code not in [200, 201]:
            print(f"Sync Labs error: {response.status_code} - {response.text}")
            return None

        gen_id = response.json().get("id")
        if not gen_id:
            return None

        # Poll for completion (max 2 minutes)
        for _ in range(24):
            time.sleep(5)
            status_resp = requests.get(
                f"https://api.sync.so/v2/generate/{gen_id}",
                headers={"x-api-key": SYNC_API_KEY},
                timeout=30
            )

            if status_resp.status_code == 200:
                data = status_resp.json()
                status = data.get("status")

                if status == "COMPLETED":
                    return data.get("outputUrl")
                elif status == "FAILED":
                    print(f"Sync Labs failed: {data.get('error')}")
                    return None

        return None  # Timeout

    except Exception as e:
        print(f"Lip-sync error: {e}")
        return None


def chat(message: str, history: list):
    """Main chat function - returns text, audio, and optional video."""

    # Get LLM response
    response_text = query_llm(message, history)

    # Generate voice
    audio_path, audio_url = generate_voice(response_text)

    # Generate lip-sync video if we have audio URL and avatar URL
    video_url = None
    if audio_url and AVATAR_URL:
        video_url = generate_lipsync_video(audio_url, AVATAR_URL)

    return response_text, audio_path, video_url


# Build Gradio interface
with gr.Blocks(title="Dr. Carlos Cortes - Interactive Dialogue", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # Dr. Carlos E. Cortes
    ### Interactive Dialogue with a Pioneer in Multicultural Education

    Ask Dr. Cortes about his work on multicultural education, media literacy,
    diversity in education, and his experiences as a historian and author.
    """)

    with gr.Row():
        with gr.Column(scale=1):
            avatar_img = gr.Image(
                value="dr_cortes.jpg" if Path("dr_cortes.jpg").exists() else None,
                label="Dr. Carlos E. Cortes",
                show_label=False,
                width=300,
                height=300
            )
            gr.Markdown("""
            **Dr. Carlos E. Cortes**
            Professor Emeritus of History
            University of California, Riverside
            """)

        with gr.Column(scale=2):
            video_output = gr.Video(
                label="Dr. Cortes Speaking",
                autoplay=True,
                visible=True
            )

    chatbot = gr.Chatbot(
        label="Conversation",
        height=300,
        show_copy_button=True
    )

    with gr.Row():
        msg = gr.Textbox(
            label="Your message",
            placeholder="Ask Dr. Cortes a question about multicultural education...",
            scale=4
        )
        submit = gr.Button("Send", variant="primary", scale=1)

    audio_output = gr.Audio(
        label="Voice Response (Audio Only)",
        type="filepath",
        autoplay=False,
        visible=True
    )

    status_text = gr.Markdown("")

    clear = gr.Button("Clear Conversation")

    # Example questions
    gr.Examples(
        examples=[
            "Dr. Cortes, how did you become interested in multicultural education?",
            "What role does media play in shaping our understanding of different cultures?",
            "What advice would you give to educators today about teaching diversity?",
        ],
        inputs=msg
    )

    def respond(message, chat_history):
        # Show processing status
        yield "", chat_history, None, None, "*Thinking...*"

        response_text, audio_path, video_url = chat(message, chat_history)
        chat_history.append((message, response_text))

        status = ""
        if video_url:
            status = "[Lip-sync video generated]"
        elif audio_path:
            status = "[Voice response generated - no video (set AVATAR_URL for lip-sync)]"
        else:
            status = "[Text only - check API keys]"

        yield "", chat_history, audio_path, video_url, status

    submit.click(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, audio_output, video_output, status_text]
    )

    msg.submit(
        respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot, audio_output, video_output, status_text]
    )

    clear.click(lambda: ([], None, None, ""), outputs=[chatbot, audio_output, video_output, status_text])

    gr.Markdown("""
    ---
    **Technical Details:**
    - Voice: ElevenLabs clone of Dr. Cortes
    - Avatar: Sync Labs lip-sync (sync.so)
    - LLM: Gemini via OpenRouter

    Built with Gradio | Hosted on Hugging Face Spaces
    """)


if __name__ == "__main__":
    demo.launch()

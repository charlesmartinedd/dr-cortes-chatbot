# Dr. Carlos Cortes Voice-Cloned Chatbot

Interactive dialogue with Dr. Carlos E. Cortes, historian and multicultural education pioneer.

## Features

- **AI Persona**: Gemini LLM trained on Dr. Cortes's bibliography
- **Voice Clone**: ElevenLabs voice clone from original recordings
- **Lip-Sync Avatar**: Sync Labs API for talking head video
- **Free Hosting**: Hugging Face Spaces (Gradio)

## Setup

### 1. Environment Variables

Set these in Hugging Face Spaces secrets:

```
OPENROUTER_API_KEY=your_openrouter_key
ELEVENLABS_API_KEY=your_elevenlabs_key
VOICE_ID=BEvFJk5aH8C3iqnJa1Mk
SYNC_API_KEY=your_sync_labs_key
```

### 2. Knowledge Base

Edit `knowledge_base.txt` with Dr. Cortes's annotated bibliography.

### 3. Deploy

```bash
# Push to Hugging Face
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/dr-cortes-chatbot
git push hf main
```

## Architecture

```
User Question
    ↓
[Gemini LLM + Bibliography Context]
    ↓
Text Response
    ↓
[ElevenLabs TTS → Voice Clone]
    ↓
Audio MP3
    ↓
[Sync Labs → Lip-Sync Video]
    ↓
Talking Avatar Video
```

## API Costs

| Service | Free Tier |
|---------|-----------|
| Hugging Face Spaces | Unlimited |
| OpenRouter (Gemini) | ~$0 |
| ElevenLabs | 10K chars/month |
| Sync Labs | 5 free minutes |

## Files

- `app.py` - Gradio app
- `knowledge_base.txt` - Dr. Cortes bibliography
- `dr_cortes.jpg` - Avatar image
- `requirements.txt` - Python dependencies

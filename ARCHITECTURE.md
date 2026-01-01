# Dr. Carlos Cortes Avatar Chatbot - Architecture

## Overview
Voice-cloned chatbot with lip-sync talking head, hosted FREE.

## Flow

```
User Question (text)
         ↓
[Gradio App on Hugging Face Spaces]
         ↓
[OpenRouter → Gemini Pro]
(57-work bibliography in system prompt)
         ↓
Response Text
         ↓
[ElevenLabs TTS → Dr. Cortes Voice Clone]
         ↓
Audio MP3
         ↓
[Sync Labs API → Lip-Sync Video]
         ↓
Video displayed to user
```

## Components

### 1. Frontend + Backend (Hugging Face Spaces - FREE)
- Gradio app with chat interface
- Accepts text input
- Displays video responses

### 2. LLM (OpenRouter - ~$0)
- Gemini Pro
- System prompt contains full 57-work bibliography
- Responds as Dr. Cortes in first person

### 3. Voice Clone (ElevenLabs - FREE tier)
- Cloned from MP4 video
- Generates audio for each response

### 4. Lip-Sync Video (Sync Labs - 5 free minutes)
- API-based lip-sync generation
- Takes: Avatar photo + ElevenLabs audio
- Returns: Lip-synced video

## Environment Variables

| Variable | Description |
|----------|-------------|
| ELEVENLABS_API_KEY | ElevenLabs API key |
| OPENROUTER_API_KEY | OpenRouter API key |
| SYNC_API_KEY | Sync Labs API key |
| VOICE_ID | ElevenLabs voice clone ID |

## Cost Summary

| Service | Cost |
|---------|------|
| Hugging Face Spaces | FREE |
| OpenRouter (Gemini) | ~$0 |
| ElevenLabs | FREE (10K chars/mo) |
| Sync Labs | 5 free minutes |
| **Total** | **$0/month (on free tiers)** |

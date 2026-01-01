# Easy-Wav2Lip on Google Colab - Free Lip-Sync Setup

Generate talking avatar videos of Dr. Cortes using the free T4 GPU on Google Colab.

## Quick Start

### Option 1: Use the Official Easy-Wav2Lip Colab
1. Go to: https://colab.research.google.com/github/anothermartz/Easy-Wav2Lip/blob/v8.4/Easy_Wav2Lip_v8.4.ipynb
2. Click "Copy to Drive" to save your own copy
3. Run all cells in order

### Option 2: Create Your Own Notebook

Create a new Colab notebook and paste these cells:

#### Cell 1: Install Dependencies
```python
!git clone https://github.com/anothermartz/Easy-Wav2Lip.git
%cd Easy-Wav2Lip
!pip install -r requirements.txt
!pip install gdown
```

#### Cell 2: Download Models
```python
!gdown --id 1dwHpJghv-PvnR2QnbH4qTJAz2WevaAv9 -O checkpoints/wav2lip.pth
!gdown --id 1k4jiug-rDqwNvSaU9uVJhqvv91xtjqtu -O checkpoints/wav2lip_gan.pth
```

#### Cell 3: Upload Your Files
```python
from google.colab import files

print("Upload dr_cortes.jpg (avatar photo)")
uploaded = files.upload()
avatar_file = list(uploaded.keys())[0]

print("Upload audio file (MP3 from ElevenLabs)")
uploaded = files.upload()
audio_file = list(uploaded.keys())[0]
```

#### Cell 4: Generate Lip-Sync Video
```python
!python inference.py \
    --checkpoint_path checkpoints/wav2lip_gan.pth \
    --face {avatar_file} \
    --audio {audio_file} \
    --outfile output_video.mp4

# Download the result
files.download('output_video.mp4')
```

## Files You Need

1. **Avatar Photo**: `dr_cortes.jpg` (extracted from video, ~87KB)
2. **Audio**: MP3 file from ElevenLabs TTS response

## Workflow

```
User Question
    |
    v
[Gradio App] --> [Gemini LLM] --> Text Response
    |
    v
[ElevenLabs TTS] --> Audio MP3
    |
    v
[Easy-Wav2Lip Colab] --> Lip-Sync Video MP4
    |
    v
[Display to User]
```

## Tips

- **GPU**: Use free T4 GPU (Runtime > Change runtime type > T4 GPU)
- **Quality**: wav2lip_gan.pth produces higher quality than wav2lip.pth
- **Processing Time**: ~30-60 seconds for a 30-second response
- **Image Format**: JPG or PNG, face should be clearly visible
- **Audio Format**: MP3 or WAV, clear speech

## Automation (Future)

For fully automated lip-sync, you could:
1. Host Easy-Wav2Lip on a GPU server (e.g., RunPod, Lambda Labs)
2. Create an API endpoint that accepts audio + image
3. Return the generated video

This would add ~$0.30-0.50/hour for GPU time when in use.

## Resources

- Easy-Wav2Lip GitHub: https://github.com/anothermartz/Easy-Wav2Lip
- ElevenLabs API: https://docs.elevenlabs.io/
- Gradio Docs: https://gradio.app/docs/

from fastapi import APIRouter, UploadFile, File, HTTPException
import speech_recognition as sr
import io
from pydub import AudioSegment
import os

router = APIRouter()

# Check if ffmpeg is available (needed for pydub non-wav support)
# If not, we hope the browser sends WAV or we warn user.

@router.post("/api/stt")
async def speech_to_text(file: UploadFile = File(...)):
    print(f"Received audio file for STT: {file.filename}, Content-Type: {file.content_type}")
    
    try:
        # Read audio file
        audio_bytes = await file.read()
        
        # Pre-process: Convert to WAV if possible (SpeechRecognition prefers WAV)
        wav_io = io.BytesIO()
        
        try:
            # Try converting using pydub (requires ffmpeg)
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio = audio.set_channels(1).set_frame_rate(16000) # Standardize
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
        except Exception as e:
            print(f"Warning: pydub conversion failed (FFmpeg missing?): {e}")
            # Fallback: Treat as raw WAV if possible, or try direct recognition
            wav_io = io.BytesIO(audio_bytes)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            # Record the audio data
            audio_data = recognizer.record(source)
            
            # Use Google Web Speech API (Free tier, good enough for personal use)
            print("Listening to audio data...")
            text = recognizer.recognize_google(audio_data)
            print(f"Transcribed: {text}")
            return {"text": text}
            
    except sr.UnknownValueError:
        print("STT: Could not understand audio")
        return {"text": ""}
    except sr.RequestError as e:
        print(f"STT API Error: {e}")
        raise HTTPException(status_code=503, detail=f"Speech API Connection Error: {e}")
    except Exception as e:
        print(f"STT General Error: {e}")
        # Return empty if failed so frontend doesn't crash
        return {"text": "", "error": str(e)}

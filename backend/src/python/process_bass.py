import sys
import yt_dlp
import librosa
import numpy as np
import soundfile as sf

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info['ext']

def extract_bass(filename):
    # Aquí iría spleeter u otro método de separación
    # Por ahora usamos el mismo archivo como placeholder
    y, sr = librosa.load(filename, sr=44100)
    return y, sr

def detect_notes(y, sr):
    # Placeholder: solo genera notas tocables de ejemplo
    return ["E1", "G1", "A1", "B1", "C2", "D2"]

if __name__ == "__main__":
    url = sys.stdin.readline().strip()
    ext = download_audio(url)
    y, sr = extract_bass(f"song.{ext}")
    notas = detect_notes(y, sr)
    print(",".join(notas))

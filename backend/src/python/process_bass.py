import sys
import os
import yt_dlp
import librosa
import numpy as np
import subprocess
import warnings

warnings.filterwarnings("ignore")


# -------------------------
# 1) Obtener URL
# -------------------------
if len(sys.argv) < 2:
    sys.exit(1)

url = sys.argv[1]


# -------------------------
# 2) Descargar audio
# -------------------------
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class NoLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': f'{DOWNLOAD_DIR}/song.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'logger': NoLogger(),
    'progress_hooks': [],
}


with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])



audio_file = None
for f in os.listdir(DOWNLOAD_DIR):
    if f.startswith("song") and f.endswith((".mp3", ".webm", ".m4a", ".wav")):
        audio_file = os.path.join(DOWNLOAD_DIR, f)
        break

if not audio_file:
    sys.exit(1)


# -------------------------
# 3) Separar bajo con DEMUCS
# -------------------------
demucs_path = os.path.join(os.path.dirname(sys.executable), "demucs.exe")

subprocess.run(
    [demucs_path, "--two-stems=bass", audio_file],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)


bass_file = None
for root, dirs, files in os.walk("separated"):
    for f in files:
        if f == "bass.wav":
            bass_file = os.path.join(root, f)
            break

if not bass_file:
    sys.exit(1)


# -------------------------
# 4) Cargar audio del bajo
# -------------------------
y, sr = librosa.load(bass_file, sr=44100)


# -------------------------
# 5) Detectar pitch (YIN)
# -------------------------
def hz_to_note(freq):
    if freq <= 0:
        return None
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F',
             'F#', 'G', 'G#', 'A', 'A#', 'B']
    A4 = 440
    n = int(round(12 * np.log2(freq / A4)))
    octave = 4 + (n + 9) // 12
    note = notes[(n + 9) % 12]
    return f"{note}{octave}"

f0 = librosa.yin(y, fmin=43, fmax=350, sr=sr)

notas_detectadas = []
for freq in f0:
    if 43 < freq < 350:
        nota = hz_to_note(freq)
        if nota:
            notas_detectadas.append(nota)


# -------------------------
# 6) Estabilizar notas
# -------------------------
def stabilize_notes(notes):
    cleaned = []
    last = None
    counter = 0
    
    for n in notes:
        if n == last:
            counter += 1
        else:
            if last and counter > 5:
                cleaned.append(last)
            last = n
            counter = 1

    if last and counter > 5:
        cleaned.append(last)

    return cleaned

notas_estables = stabilize_notes(notas_detectadas)


# -------------------------
# 7) Mapa cuerda/traste
# -------------------------
bass_strings = {
    4: ['E1','F1','F#1','G1','G#1','A1','A#1','B1','C2','C#2','D2','D#2','E2','F2','F#2','G2','G#2','A2','A#2','B2','C3'],
    3: ['A1','A#1','B1','C2','C#2','D2','D#2','E2','F2','F#2','G2','G#2','A2','A#2','B2','C3','C#3','D3','D#3','E3'],
    2: ['D2','D#2','E2','F2','F#2','G2','G#2','A2','A#2','B2','C3','C#3','D3','D#3','E3','F3','F#3','G3'],
    1: ['G2','G#2','A2','A#2','B2','C3','C#3','D3','D#3','E3','F3','F#3','G3','G#3','A3']
}

def note_to_position(note):
    for string, notes in bass_strings.items():
        if note in notes:
            fret = notes.index(note)
            return string, fret
    return None


# -------------------------
# 8) Optimizar digitación
# -------------------------
optimized = []
prev_string = None
prev_fret = None

for nota in notas_estables:
    pos = note_to_position(nota)
    if not pos:
        continue

    string, fret = pos
    prev_string, prev_fret = string, fret

    optimized.append(f"{nota} (Cuerda {string}, Traste {fret})")


# -------------------------
# 9) SALIDA LIMPIA
# -------------------------
print("\n".join(optimized))

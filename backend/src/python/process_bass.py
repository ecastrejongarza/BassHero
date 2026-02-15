import sys
import os
import yt_dlp
import librosa
import numpy as np

print("=== PROCESS_BASS OPTIMIZADO GRAVE ===")

# -------------------------
# 1) Obtener URL
# -------------------------
if len(sys.argv) < 2:
    print("No URL provided")
    sys.exit(1)

url = sys.argv[1]

# -------------------------
# 2) Descargar audio
# -------------------------
audio_file = "song.mp3"
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'song.%(ext)s',
    'quiet': True
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

# detectar extensión real
for f in os.listdir():
    if f.startswith("song."):
        audio_file = f
        break

print(f"Audio descargado: {audio_file}")

# -------------------------
# 3) Cargar audio
# -------------------------
y, sr = librosa.load(audio_file, sr=44100)
print("Audio cargado correctamente")

# -------------------------
# 4) Configuración de notas y cuerdas
# -------------------------
notes = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

# Afinación estándar de bajo 4 cuerdas (MIDI numbers)
strings = {
    4: 40,  # E1
    3: 45,  # A1
    2: 50,  # D2
    1: 55   # G2
}

def hz_to_note(freq):
    if freq <= 0:
        return None
    A4 = 440
    n = int(round(12 * np.log2(freq / A4)))
    octave = 4 + (n + 9) // 12
    note = notes[(n + 9) % 12]
    return f"{note}{octave}"

def note_to_positions(note_name):
    """Devuelve todas las posiciones posibles (cuerda, traste) para una nota"""
    note, octave = note_name[:-1], int(note_name[-1])
    note_index = {n:i for i,n in enumerate(notes)}
    midi_number = (octave+1)*12 + note_index[note]
    positions = []
    for string_num, open_midi in strings.items():
        fret = midi_number - open_midi
        if 0 <= fret <= 24:  # rango típico
            positions.append((string_num, fret))
    return positions

# -------------------------
# 5) Detectar notas graves
# -------------------------
pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
detected_notes = []

for t in range(pitches.shape[1]):
    index = magnitudes[:, t].argmax()
    freq = pitches[index, t]
    if 40 < freq < 350:  # rango del bajo
        nota = hz_to_note(freq)
        if nota:
            positions = note_to_positions(nota)
            if positions:
                detected_notes.append((nota, positions))

# -------------------------
# 6) Optimizar digitación respetando cuerda grave
# -------------------------
optimized_notes = []
prev_string = None
prev_fret = None

for nota, positions in detected_notes:
    # Priorizar la cuerda más grave disponible
    min_string = min(pos[0] for pos in positions)
    grave_positions = [pos for pos in positions if pos[0] == min_string]
    
    # Elegir la posición más cómoda
    if prev_string is None:
        chosen = min(grave_positions, key=lambda x: x[1])
    else:
        # Mantener movimiento mínimo, preferir misma cuerda si posible
        same_string_positions = [p for p in grave_positions if p[0] == prev_string]
        if same_string_positions:
            chosen = min(same_string_positions, key=lambda x: abs(x[1]-prev_fret))
        else:
            chosen = min(grave_positions, key=lambda x: abs(x[1]-prev_fret) + abs(x[0]-prev_string))
    
    prev_string, prev_fret = chosen
    optimized_notes.append(f"{nota} (Cuerda {prev_string}, Traste {prev_fret})")

# -------------------------
# 7) Limpiar repetidas consecutivas
# -------------------------
final_notes = []
if optimized_notes:
    final_notes.append(optimized_notes[0])
for n in optimized_notes[1:]:
    if n != final_notes[-1]:
        final_notes.append(n)

# -------------------------
# 8) Imprimir resultado limpio para React
# -------------------------
print(",".join(final_notes))

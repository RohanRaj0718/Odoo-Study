import os
import subprocess
import shutil

# Find the ffmpeg from imageio-ffmpeg and put it on PATH
import imageio_ffmpeg
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
print(f"ffmpeg found at: {ffmpeg_path}")

# Copy ffmpeg to a location named "ffmpeg.exe" so whisper can find it
ffmpeg_dir = os.path.dirname(ffmpeg_path)
target_ffmpeg = os.path.join(ffmpeg_dir, "ffmpeg.exe")
if not os.path.exists(target_ffmpeg):
    shutil.copy2(ffmpeg_path, target_ffmpeg)
    print(f"Copied ffmpeg to: {target_ffmpeg}")

os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
print(f"Added {ffmpeg_dir} to PATH")

input_file = r"C:\Odoo Study\WhatsApp Ptt 2026-02-26 at 10.22.38 AM.ogg"

import whisper
print('\nLoading whisper model (small - better for multilingual)...')
model = whisper.load_model('small')

print('Transcribing in Malayalam...')
result_ml = model.transcribe(input_file, language='ml')
print('\n=== MALAYALAM TRANSCRIPTION ===')
print(result_ml['text'])

print('\n=== SEGMENTS (Malayalam) ===')
for seg in result_ml['segments']:
    print(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")

print('\n\n=== ENGLISH TRANSLATION ===')
result_en = model.transcribe(input_file, task='translate')
print(result_en['text'])

print('\n=== TRANSLATION SEGMENTS ===')
for seg in result_en['segments']:
    print(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")

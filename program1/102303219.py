import sys
import os
from yt_dlp import YoutubeDL
from pydub import AudioSegment

import shutil

def reset_dirs():
    for d in ["audios", "clips"]:
        if os.path.exists(d):
            shutil.rmtree(d)

def validate_args():
    if len(sys.argv) != 5:
        print("Usage: python <program.py> <SingerName> <NumVideos> <DurationSec> <OutputFile>")
        sys.exit(1)

    singer = sys.argv[1]

    try:
        n = int(sys.argv[2])
        dur = int(sys.argv[3])
    except:
        print("NumVideos and DurationSec must be integers")
        sys.exit(1)

    if n <= 10:
        print("NumVideos must be greater than 10")
        sys.exit(1)

    if dur <= 20:
        print("Duration must be greater than 20 seconds")
        sys.exit(1)

    output = sys.argv[4]

    return singer, n, dur, output

def download_videos(singer, n):
    os.makedirs("audios", exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audios/%(id)s.%(ext)s',
        'quiet': False,
        'ignoreerrors': True,   # ← important fix
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    query = f"ytsearch{n}:{singer} songs"

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([query])

def trim_audios(duration):
    files = os.listdir("audios")
    if len(files) == 0:
        print("No audio files downloaded — exiting")
        sys.exit(1)

    os.makedirs("clips", exist_ok=True)

    for file in os.listdir("audios"):
        audio = AudioSegment.from_file(os.path.join("audios", file))
        clip = audio[:duration * 1000]
        clip.export(os.path.join("clips", file), format="mp3")

def merge_clips(output_name):
    combined = AudioSegment.empty()

    for file in sorted(os.listdir("clips")):
        sound = AudioSegment.from_file(os.path.join("clips", file))
        combined += sound

    combined.export(output_name, format="mp3")

def main():
    singer, n, dur, output = validate_args()

    reset_dirs()   # ← add this line

    print("Downloading audios...", flush=True)
    download_videos(singer, n)

    print("Trimming clips...", flush=True)
    trim_audios(dur)

    print("Merging mashup...", flush=True)
    merge_clips(output)

    print("Mashup created:", output)

if __name__ == "__main__":
    main()

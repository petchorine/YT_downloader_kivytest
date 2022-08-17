import os

from kivy.properties import ObjectProperty
from pytube import YouTube
import ffmpeg


def on_download_progress(stream, chunk, bytes_remaining):
    # octets qu'on a déjà téléchargés
    bytes_downloaded = stream.filesize - bytes_remaining
    # pourcentage des octets déjà téléchargés
    percent = bytes_downloaded * 100 / stream.filesize

    print(percent)
    print(f"Progression du téléchargement: {percent}% - {bytes_remaining}")


def download_video(url):
    # création d'un objet youtube
    youtube_video = YouTube(url)

    youtube_video.register_on_progress_callback(on_download_progress)


    # FILTRAGE ET TRI (pour sélectionner le meilleur stream video)
    streams = youtube_video.streams.filter(progressive=False, file_extension="mp4", type="video").order_by("resolution").desc()
    best_video_stream = streams[0]

    # FILTRAGE ET TRI (pour sélectionner le meilleur stream audio)
    streams = youtube_video.streams.filter(progressive=False, file_extension="mp4", type="audio").order_by("abr").desc()
    best_audio_stream = streams[0]

    # TELECHARGEMENT
    print("Téléchargement video...")
    best_video_stream.download("video")
    print("OK")

    print("Téléchargement audio...")
    best_audio_stream.download("audio")
    print("ok")

    # COMBINAISON DES FICHIERS AUDIO ET VIDEO
    audio_filename = os.path.join("audio", best_audio_stream.default_filename)
    video_filename = os.path.join("video", best_video_stream.default_filename)
    output_filename = best_video_stream.default_filename

    print("Combinaison des fichiers...")
    ffmpeg.output(ffmpeg.input(audio_filename), ffmpeg.input(video_filename), output_filename, vcodec="copy", acodec="copy", loglevel="quiet").run(overwrite_output=True)
    print("ok")

    # à la fin de l'opération de combinaison => suppression des fichiers et dossiers temporaires audio et video
    os.remove(audio_filename)
    os.remove(video_filename)
    os.rmdir("audio")
    os.rmdir("video")





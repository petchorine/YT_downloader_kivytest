from pytube import YouTube

BASE_YOUTUBE_URL = "https://www.youtube.com"


def get_video_url_from_user():
    # pour vérifier que l'url correspond bien à une vidéo Youtube (commençant par "https://www.youtube.com")
    while True:
        print("Entrez l'adresse de votre vidéo à télécharcher.")
        url_yt = input("-> ")

        # alternative pour vérifier le début d'une chaine : if url[:len(BASE_YOUTUBE_URL)] == BASE_YOUTUBE_URL:
        if url_yt.startswith(BASE_YOUTUBE_URL):
            # si c'est égal alors je sors de la boucle
            return url_yt
        # sinon j'affiche l'erreur et je boucle
        print("Cette url ne correspond pas à une vidéo Youtube !")


# Video courte
url = "https://www.youtube.com/watch?v=b8ifXl7Cvsk"
# Video longue
# url ="https://www.youtube.com/watch?v=oQl_eCA7EGk"
# fonction
#url = get_video_url_from_user()


def get_video_stream_itag_from_user(streams):
    print("")
    # LISTE FILTREE DES STREAMS
    print("LISTE DES STREAMS: ")
    index = 1
    for stream in streams:
        print(f"   {index} - ", stream.resolution)
        index += 1

    # CHOIX DE LA RESOLUTION EN FONCTION DE LA LISTE FILTREE
    print("")
    while True:
        print("Choisissez la résolution :")
        user_choice = input("-> ")

        if user_choice == "":
            print("ERREUR : vous devez entrer un nombre.")
        else:
            try:
                user_choice_int = int(user_choice)
            except:
                print("ERREUR: Vous devez entrer une valeur numérique.")
            else:
                if not 1 <= user_choice_int < index:
                    print(f"ERREUR : Vous devez choisir un nombre compris entre 1 et {index - 1}.")
                else:
                    itag = streams[int(user_choice)].itag
                    return itag


def on_download_progress(stream, chunk, bytes_remaining):
    # octets qu'on a déjà téléchargés
    bytes_downloaded = stream.filesize - bytes_remaining
    # pourcentage des octets déjà téléchargés
    percent = bytes_downloaded * 100 / stream.filesize
    print(percent)
    
    print(f"Progression du téléchargement: {percent}% - {bytes_remaining}")


# création d'un objet youtube
youtube_video = YouTube(url)

# PROGRESSION DU TELECHARGEMENT
# la cbk est définie plus haut dans le code 
youtube_video.register_on_progress_callback(on_download_progress)

# TITRE
print("TITRE: " + youtube_video.title)

# NOMBRE DE VUES
print("NB VUES: " + str(youtube_video.views))

# LISTE DE TOUS LES STREAMS
# print("LISTE DES STREAMS: ")
# streams = youtube_video.streams
# for stream in streams:
#     print("   ", stream)

# en "progressive=True", on est limité par la qualité à 720p
# streams = youtube_video.streams.filter(progressive=True, file_extension="mp4")

streams = youtube_video.streams.filter(progressive=False, file_extension="mp4")
print("LISTE DES STREAMS: ")
for stream in streams:
    print("   ", stream)


# demande la résolution à l'utilisateur
#itag = get_video_stream_itag_from_user(streams)


# TELECHARGEMENT
# télécharger un stream / en fonction de son itag
# le fichier sera téléchargé dans le dossier du projet (ou alors ci placer avec le terminal)
# stream = youtube_video.streams.get_by_itag(itag)
# print("Téléchargement...")
# stream.download()
# print("OK")

# télécharger un stream / en fonction de la meilleure qualité (en progressive=True)
# stream = youtube_video.streams.get_highest_resolution()
# print("Stream itag: ", stream)
# print("Téléchargement...")
# stream.download()
# print("OK")




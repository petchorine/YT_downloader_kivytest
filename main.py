import os
import ffmpeg
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from pytube import Playlist, YouTube


# liens pour les tests
# playlist courte : https://www.youtube.com/playlist?list=PL6wtbJKOh3fGOVxYNrL7nRQT6wcaThm7m
# video avec pleins de résolutions : https://www.youtube.com/watch?v=ExKpWKSrOPE


# taille de l'app à l'ouverture
Window.size = (700, 820)


# référence le popup paramétré dans le fichier kv associé
class MyPopup(Popup):
    pass


class YoutubeDwn(BoxLayout):
    BASE_YOUTUBE_URL = "https://www.youtube.com"
    compteur = 0
    tab_ck = []
    playlist_youtube_video = []
    selected_resolutions = []

    # récupère l'url entrée dans le champs "TextInput"
    # vérifie si l'url entrée commence bien par "https://www.youtube.com"
    # vérifie que le champs "TextInput" n'est pas vide
    def get_video_url_from_user(self):
        url = self.url_input.text

        # pour vérifier que l'url correspond bien à une vidéo Youtube (commençant par "https://www.youtube.com")
        if url.startswith(self.BASE_YOUTUBE_URL):
            # si ok => appel de la méthode de verification "playlist_or_not_playlist"
            self.playlist_or_not_playlist(url)
            # TO DO : vider le champ TextInput qd url est bonne
        else:
            # compteur permet de faire cette blague pourrie => 1x et 2x = msg ERREUR et 3x msg d'injure
            self.compteur += 1
            self.url_input.text = ""
            if self.compteur < 3:
                self.label_intro.text = "ERREUR : veuillez entrer une adresse valide !"
            else:
                self.label_intro.text = "ENTRE UNE ADRESSE VALIDE, SAC à PUE"

    # une fois l'url récupérée, vérifie si le mot "playlist" est dans l'url
    # si oui => crée un objet PyTube pour chaque vidéo et l'ajoute à la liste "playlist_youtube_video"
    # si non => crée un objet PyTube pour chaque vidéo et l'ajoute à la liste "playlist_youtube_video"
    # note : dans la doc, possible de passer l'url d'une seule video dans Playlist(url) mais je n'ai pas réussi
    def playlist_or_not_playlist(self, url):
        # permet de n'avoir dans "playlist_youtube_video" que les objet PyTube correspondant à l'url entrée
        # permettra par la suite de n'afficher que les videos correspondant à l'url
        if len(self.playlist_youtube_video) != 0:
            self.playlist_youtube_video = []

        if "playlist" not in url:
            youtube_video = YouTube(url)
            self.playlist_youtube_video.append(youtube_video)
        else:
            p = Playlist(url)
            for url in p.video_urls:
                youtube_video = YouTube(url)
                self.playlist_youtube_video.append(youtube_video)

        # après dispatch "playlist_or_not_playlist", appel de la méthode "show_playlist"
        # en paramètre : la liste "playlist_youtube_video"
        self.show_playlist(self.playlist_youtube_video)

    # affiche qqs infos pour chaque video (thumbnail, title, duration) dans une playlist
    def show_playlist(self, playlist_youtube_video):
        # efface les widgets (playlist ou video unique) des précédentes recherches
        self.ids.playlist_layout.clear_widgets()

        # boucle pour créér une ligne pour chaque video de la playlist
        for youtube_video in playlist_youtube_video:
            one_line_layout = BoxLayout(orientation="horizontal", size_hint=(1, None), height=(dp(100)))
            thumb_img = AsyncImage(source=f"{youtube_video.thumbnail_url}")
            lab_title = Label(text=f"{youtube_video.title}")
            lab_duration = Label(text=f"{str(round(youtube_video.length/60, 2))}")

            one_line_layout.add_widget(thumb_img)
            one_line_layout.add_widget(lab_title)
            one_line_layout.add_widget(lab_duration)

            self.ids.playlist_layout.add_widget(one_line_layout)

    # après choix entre "Video + audio" et "audio uniquement"
    # si "Video + audio" => affiche les différentes résolutions
    # permet de choisir la résolution video à télécharger
    # TO DO  : je n'ai pas encore fait le choix de quelle résolution garder pour les playlists..
    # ...je pense que j'afficherai la résolution de la 1ère video...
    # si cette résolution n'existe pas pour les videos suivantes => prendre la résolution au-dessus ou en-dessous
    def show_video_choice(self, instance):
        # raz du widget qui garde en mémoire les précédents affichages
        if self.video_choice.active:
            self.ids.quality_choice.clear_widgets()

        # TO DO : améliorer le code en créant une liste qui récupérerait tous les objets pytube
        # récupère l'url / crée un objet PyTube / filtre et tri les streams de l'objet "PyTube")
        url = self.url_input.text
        youtube_video = YouTube(url)
        streams = youtube_video.streams.filter(file_extension="mp4", type="video").order_by(
                "resolution").desc()

        # dans une liste "all_resolutions", récupère pour chaque objet PyTube (résolution, is_progressive, itag
        all_resolutions = []
        for stream in streams:
            # dans PyTube, la résolution est un str => supprime le "p" et convertit en int
            stream_resolution = int(stream.resolution[:-1])
            all_resolutions.append((stream_resolution, stream.is_progressive, stream.itag))

        # dans une liste "selected_resolutions" => ajoute seulement résolutions voulues
        # si "<= 720p" alors ajoute les videos "progressives" plus rapides à charger (limité aux videos <= 720p)
        # si "> 720" alors ajoute les videos "adaptatives"
        # TO DO : il peut y avoir plusieurs fois la même résolution mais avec différents codecs...
        # ...supprimer les doublons ou les garder en affichant le codec à côté
        for i in range(len(all_resolutions)):
            if (all_resolutions[i][0] > 720) or (all_resolutions[i][0] <= 720 and all_resolutions[i][1]):
                self.selected_resolutions.append(all_resolutions[i])

        box_resolutions = BoxLayout(orientation="horizontal", padding=(0, 0, 0, 20))
        for i in range(len(self.selected_resolutions)):
            # DEFINITION LAYOUT CONTENANT CHECKBOX ET RESOLUTION

            # TO DO : voir pour les fichiers "test" pour l'alignement des labels...
            # ...il faut peut être mettre un AnchorLayout sur "ck_and_resolution"

            ck_and_resolution = BoxLayout(orientation="horizontal")

            # DEFINITION CHECKBOX
            # choix par défaut (case cochée) => meilleure qualité (1er stream)
            if i == 0:
                c = CheckBox(group="ck_video", active=True, size_hint=(None, None), size=(sp(32), sp(32)))
            else:
                c = CheckBox(group="ck_video", size_hint=(None, None), size=(sp(32), sp(32)))

            # tab contenant les objets "Checkbox" avec leur état (actif ou non)
            self.tab_ck.append(c)

            # DEFINITION LABEL "RESOLUTION" EN REGARD DE CHAQUE CHECKBOX
            video_label = Label(text=f"{self.selected_resolutions[i][0]}p",
                                size_hint=(None, None),
                                size=(sp(32), sp(32)))

            # AFFICHAGE CHECKBOX + RESOLUTIONS
            ck_and_resolution.add_widget(c)
            ck_and_resolution.add_widget(video_label)
            # affichage "ck_and_resolution" dans "ck_resolution_and_btn"
            box_resolutions.add_widget(ck_and_resolution)
        self.ids.quality_choice.add_widget(box_resolutions)

        # DEFINITION BTN "TELECHARGER"
        btn_download = Button(text="Télécharger",
                              size_hint=(1, None),
                              height=dp(40),
                              background_normal="",
                              background_color=(0.4, 0.4, 1, 1))

        # appel de la méthode "resolution_choice
        btn_download.bind(on_press=self.download_video)
        # affichage du btn dans "ck_resolution_and_btn"
        self.ids.quality_choice.add_widget(btn_download)

    # TO DO : affiche l'évolution du chargement dans des progress bar et labels
    # note : marche pour l'instant uniquement dans le terminal
    def on_download_progress(self, stream, chunk, bytes_remaining):
        # octets qu'on a déjà téléchargés
        bytes_downloaded = stream.filesize - bytes_remaining
        # pourcentage des octets déjà téléchargés
        percent = int(bytes_downloaded * 100 / stream.filesize)

        print(percent)
        print(f"Progression du téléchargement: {percent}% - {bytes_remaining}")

        # TO DO : afficher l'évolution de la progress bar de chargement et du label
        # self.ids.progress_stream_value.value = percent
        # self.ids.progress_stream_label.text = f"{str(percent)}%"

        # TO DO : si playlist alors afficher l'évolution de la progress bar (+label) du nbre de videos restant à charger

    def download_video(self, instance):
        # TO DO : amélioration du code pour ne pas toujours répéter cette url
        url = self.url_input.text

        itag = 0
        resolution = 0

        # sélectionne la résolution correspondant à index de la checkbox active
        for i in range(len(self.tab_ck)):
            if self.tab_ck[i].active:
                itag = self.selected_resolutions[i][2]
                resolution = self.selected_resolutions[i][0]

        # TO DO : Voir comment je gère la résolution de chaque vidéo dans une playlist
        # POUR PLAYLIST
        if "playlist" in url:
            print("je suis une playlist video")
            p = Playlist(url)
            for url in p.video_urls:
                youtube_video = YouTube(url)
                stream = youtube_video.streams.get_by_itag(itag)
                print(f"Téléchargement...")
                # stream.download()
                print("OK")
        else:
            # POUR VIDEO UNIQUE
            youtube_video = YouTube(url)

            # appel de la méthode "on_download_progress" qui permet l'affichage de la progression
            youtube_video.register_on_progress_callback(self.on_download_progress)

            for i in range(len(self.selected_resolutions)):
                # si resolution <= 720p alors charge la video progressive
                if resolution <= 720:
                    stream = youtube_video.streams.get_by_itag(itag)
                    print(f"Téléchargement...")
                    stream.download()
                    print("OK")
                    break
                else:
                    stream_video = youtube_video.streams.get_by_itag(itag)

                    streams = youtube_video.streams.filter(progressive=False, file_extension="mp4",
                                                           type="audio").order_by("abr").desc()
                    best_audio_stream = streams[0]

                    # TELECHARGEMENT
                    print("Téléchargement video...")
                    stream_video.download("video")
                    print("OK")

                    print("Téléchargement audio...")
                    best_audio_stream.download("audio")
                    print("ok")

                    # COMBINAISON DES FICHIERS AUDIO ET VIDEO
                    audio_filename = os.path.join("audio", best_audio_stream.default_filename)
                    video_filename = os.path.join("video", stream_video.default_filename)
                    output_filename = stream_video.default_filename

                    print("Combinaison des fichiers...")
                    ffmpeg.output(ffmpeg.input(audio_filename), ffmpeg.input(video_filename), output_filename,
                                  vcodec="copy", acodec="copy", loglevel="quiet").run(overwrite_output=True)
                    print("ok")

                    # à la fin de l'opération de combinaison => suppr. des fichiers/dossiers temporaires audio/video
                    os.remove(audio_filename)
                    os.remove(video_filename)
                    os.rmdir("audio")
                    os.rmdir("video")

                    break

    # après choix entre "Video + audio" et "audio uniquement"
    # si "audio uniquement" => ne pas laisser le choix et charger la meilleure qualité par défaut
    # je voulais apprendre à implémenter un popup dans kivy donc...
    # btn oui (appel de méthode "download_audio") et non (appel de méthode "popup")
    def show_audio_choice(self, instance):
        if self.audio_choice.active:
            self.ids.quality_choice.clear_widgets()

        layout_info_and_btns = BoxLayout(orientation="vertical")

        info_audio_quality = Label(text="L'audio pèse kekouik donc on va prendre la meilleure qualité. Ok ?",
                                   font_size=15)
        layout_info_and_btns.add_widget(info_audio_quality)

        layout_buttons = BoxLayout(orientation="horizontal")

        oui_btn = Button(text="oui", size_hint=(1, None), height=dp(40))
        oui_btn.bind(on_press=self.download_audio)
        layout_buttons.add_widget(oui_btn)

        non_btn = Button(text="non", size_hint=(1, None), height=dp(40))
        popup = MyPopup()
        non_btn.bind(on_press=popup.open)
        layout_buttons.add_widget(non_btn)

        layout_info_and_btns.add_widget(layout_buttons)
        self.ids.quality_choice.add_widget(layout_info_and_btns)

    # si playlist => crée un objet "Playlist" puis téléchargement du meilleur stream audio associé à chaque objet PyTube
    # sinon => téléchargement du meilleur stream audio associé l'objet PyTube
    # TO DO : simplification du code sûrement possible
    # note : dans la doc, possible de passer l'url d'une seule video dans Playlist(url) mais je n'ai pas réussi
    def download_audio(self, instance):
        url = self.url_input.text

        if "playlist" in url:
            print("je suis une playlist audio")
            p = Playlist(url)
            for url in p.video_urls:
                youtube_video = YouTube(url)
                streams = youtube_video.streams.filter(progressive=False, file_extension="mp4", type="audio").order_by(
                    "abr").desc()
                best_stream = streams[0]

                print("Téléchargement...")
                best_stream.download()
                print("OK")
        else:
            print("je suis un unique audio")
            youtube_video = YouTube(url)
            streams = youtube_video.streams.filter(progressive=False, file_extension="mp4", type="audio").order_by(
                "abr").desc()
            best_stream = streams[0]
            print(best_stream.abr)
            print("Téléchargement...")
            best_stream.download()
            print("OK")


# classe principale
class YoutubeDownloaderApp(App):
    def build(self):
        return YoutubeDwn()


YoutubeDownloaderApp().run()

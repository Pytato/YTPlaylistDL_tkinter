from scrollframe import ScrollFrame
from tkinter import filedialog
from tkinter import ttk as tk
from datetime import datetime
from urllib import request
import pkinter as pk
import requests
import logging
import tkinter
import audio
import video
import time
import pafy
import os


class TkGUI:
    def __init__(self, root):
        self.tkGUILogger = logging.getLogger("PlaylistDL.tk_core.TkGUI")
        self.root = root
        self.options_gen = False
        self.quality_widget_pregen = False
        self.check_firstrun = True
        self.root.title("YTPlaylistDL")
        self.gen_base_widgets()
        self.root.mainloop()

    def gen_base_widgets(self):
        url_str = tkinter.StringVar()

        url_entry_frame = tk.Frame(self.root)
        url_entry_frame.pack(fill="x")

        url_label = tk.Label(url_entry_frame, text="Youtube URL:")
        url_label.grid(pady=5, padx=[5, 0])

        self.url_entry = tk.Entry(url_entry_frame, width=72, textvariable=url_str)
        self.url_entry.grid(column=1, row=0, padx=10, pady=5)

        url_scrape_button = tk.Button(url_entry_frame, text="Scrape URL", command=lambda: self.scrape_url(url_str))
        url_scrape_button.grid(column=1, row=1, sticky="E", padx=10)

        self.video_frame = tk.Frame(self.root)
        self.video_frame.pack(fill="x")
        self.video_frame.columnconfigure(0, weight=1)

    def gen_playlist_info(self):
        # The next thing to do!
        try:
            self.info_frame.pack_forget()
            self.info_frame.destroy()
        except AttributeError:
            pass

        video_from_playlist_array = []
        # Generate an array of video objects (pafy type)
        for video in self.playlist_to_dl["items"]:
            video_object = video["pafy"]
            video_from_playlist_array.append(video_object)
        # Use the scollbar in frame here!

        self.info_frame = tk.Labelframe(self.video_frame, labelanchor="n", text="Playlist Information")
        self.info_frame.grid(padx=10, row=0, sticky="we")

        scroll_frame = ScrollFrame(self.info_frame)
        scroll_frame.pack()

        for video in video_from_playlist_array:
            video_index = video_from_playlist_array.index(video)
            number_label = tk.Label(scroll_frame.frame, text=str(video_index+1)+") ")
            video_hyperlink = pk.Hyperlink(scroll_frame.frame, link=video.watchv_url, show_text=video.title)
            number_label.grid(column=0, row=video_index, sticky="e")
            video_hyperlink.grid(column=1, row=video_index, sticky="w")

        self.generate_options()

    def gen_video_info(self, video_object):
        try:
            self.info_frame.pack_forget()
            self.info_frame.destroy()
        except AttributeError:
            pass

        self.info_frame = tk.LabelFrame(self.video_frame, labelanchor="n", text="Video Information")
        self.info_frame.grid(padx=10, row=0, sticky="we", columnspan=3)

        video_title_label = tk.Label(self.info_frame, text="Title:")
        video_title = tk.Label(self.info_frame, text=video_object.title)
        video_title_label.grid(sticky="w", padx=[0, 10])
        video_title.grid(column=1, row=0, sticky="w")

        video_views_label = tk.Label(self.info_frame, text="Views:")
        video_views = tk.Label(self.info_frame, text=str(video_object.viewcount))
        video_views_label.grid(column=0, row=2, sticky="w", padx=[0, 10])
        video_views.grid(column=1, row=2, sticky="w")

        video_uploader_label = tk.Label(self.info_frame, text="Uploader: ")
        uploader_url = "https://www.youtube.com/user/"+video_object.username
        video_uploader = pk.Hyperlink(self.info_frame, show_text=video_object.author, link=uploader_url)
        video_uploader_label.grid(column=0, row=3, sticky="w", padx=[0, 10])
        video_uploader.grid(column=1, row=3, sticky="w")

        video_uploaded_label = tk.Label(self.info_frame, text="Uploaded:")
        video_uploaded = tk.Label(self.info_frame, text=video_object.published)
        video_uploaded_label.grid(column=0, row=4, sticky="w", padx=[0, 10])
        video_uploaded.grid(column=1, row=4, sticky="w")

        self.generate_options()

    def generate_options(self):
        if not self.options_gen:
            self.options_frame = tk.LabelFrame(self.video_frame, labelanchor="n", text="Options")
            self.options_frame.grid(row=1, padx=10, pady=[0, 10], sticky="we")

            self.format_choice = tkinter.StringVar()
            self.format_choice.set("Format")
            self.format_dropdown = tk.Combobox(self.options_frame, textvariable=self.format_choice, state="readonly",
                                               values=["m4a", "webm audio", "ogg", "mp4",
                                                       "webm video"], width=12)
            self.format_dropdown.grid(sticky="e", padx=[3, 0])
            self.format_dropdown.bind("<<ComboboxSelected>>", self.format_check)

            self.quality_choice = tkinter.StringVar()
            self.quality_choice.set("Choose format")
            self.quality_dropdown = tk.Combobox(self.options_frame, textvariable=self.quality_choice,
                                                width=13, state="disabled")
            self.quality_dropdown.grid(sticky="e", padx=3, column=1, row=0)

            self.download_dir_choice = tkinter.StringVar()
            self.download_dir_choice.set(os.path.abspath("./Downloads/"))
            self.download_dir_entry = tk.Entry(self.options_frame, textvariable=self.download_dir_choice, width=37)
            self.download_dir_window_open = tk.Button(self.options_frame, text="Browse...", command=self.browse_dirs)
            self.download_dir_entry.grid(sticky="e", column=2, row=0)
            self.download_dir_window_open.grid(sticky="e", column=3, row=0, padx=[3, 1])

            self.options_gen = True
            self.gen_dl_widgets()

    def gen_dl_widgets(self):
        self.currently_downloading = tkinter.StringVar()
        self.currently_downloading.set('Click "Begin Download" to start.')
        self.download_info_frame = tk.Frame(self.video_frame)
        self.download_info_frame.grid(column=0, row=2, padx=10, pady=5, sticky="we")
        start_download_button = tk.Button(self.download_info_frame, text="Begin Download",
                                          command=self.start_downloaders, width=84)
        self.download_load_bar = tk.Progressbar(self.download_info_frame, orient="horizontal", mode="determinate")
        self.download_current_label = tk.Label(self.download_info_frame, textvariable=self.currently_downloading,
                                               width=84)
        start_download_button.grid(pady=[0, 3], sticky="we")
        self.download_load_bar.grid(column=0, row=1, sticky="we")
        self.download_current_label.grid(column=0, row=2, sticky="we")

    def start_downloaders(self):
        possible_formats = {"audio": ["m4a", "webm audio", "ogg"], "video": ["mp4", "webm video"]}
        self.download_object = []
        local_format = self.format_choice.get()
        self.currently_downloading.set("Currently gathering download url(s).")
        self.download_info_frame.update_idletasks()
        if local_format in possible_formats["audio"]:
            audiodl = audio.AudioDL()
            if self.is_playlist:
                self.download_object = audiodl.audio_playlist_gather(set=self.playlist_to_dl,
                                                                     fformat=self.format_choice.get(),
                                                                     quality=self.quality_choice.get())
            else:
                self.download_object = audiodl.audio_single_gather(audio_pafy=self.video,
                                                                   fformat=self.format_choice.get(),
                                                                   quality=str(self.quality_choice.get()))
            self.download_from_object(self.download_object[0], self.download_object[1])

        elif self.format_choice.get() in possible_formats["video"]:
            videodl = video.VideoDL()
            if self.is_playlist:
                pass
            else:
                pass
            # self.download_from_object(self.download_object[0], self.download_object[1])

    def download_from_object(self, data_set, download_title):
        self.currently_downloading.set("Calculating full download-size.")
        self.download_info_frame.update_idletasks()
        time.sleep(1)
        download_size_total = 0
        download_size_dict_by_title = {}
        for dl_url in data_set.values():
            request_var = requests.head(dl_url)
            download_size_total += int(request_var.headers["content-length"])
            # download_size_dict_by_title[""]
        loading_bar_length = download_size_total
        self.download_load_bar.configure(maximum=loading_bar_length)
        time.sleep(1)
        safe_characters = (' ', '.', '_')
        file_title = "".join(c for c in download_title if c.isalnum() or c in safe_characters).rstrip()
        download_folder_name = file_title+" [{}]".format(datetime.strftime(datetime.today(),
                                                                           format="%d-%m-%y_%H%M%S"))
        local_download_dir = self.download_dir_choice.get().replace("\\", "/")
        os.mkdir(local_download_dir+"/"+download_folder_name)
        for title, dl_url in data_set.items():
            file_title = "".join(c for c in title if c.isalnum() or c in safe_characters).rstrip()
            self.currently_downloading.set("Currently downloading '{}'".format(file_title))
            self.download_info_frame.update_idletasks()
            time.sleep(1)
            request.urlretrieve(dl_url, filename=local_download_dir+"/"+download_folder_name+"/"+file_title)
            self.download_load_bar.step()
            self.download_info_frame.update_idletasks()
        self.currently_downloading.set("Finished downloading files.")

    def browse_dirs(self):
        download_dir_choice = filedialog.askdirectory(parent=self.root, initialdir="./Downloads/", mustexist=True,
                                                      title="Choose a download directory")
        self.download_dir_choice.set(download_dir_choice)

    def format_check(self, etc):
        possible_formats = {"audio": ["m4a", "webm audio", "ogg"], "video": ["mp4", "webm video"]}
        local_format_choice = self.format_dropdown.get()
        if local_format_choice == "Choose a format":
            return

        if self.quality_widget_pregen or self.check_firstrun is True:
            self.clear_quality_widgets()
            self.check_firstrun = False

        self.quality_widget_pregen = True

        if local_format_choice in possible_formats["audio"]:
            self.gen_bitrates()
        elif local_format_choice in possible_formats["video"]:
            self.gen_resolutions()

    def clear_quality_widgets(self):
        self.quality_dropdown.grid_forget()
        self.quality_dropdown.destroy()

    def gen_bitrates(self):
        self.quality_choice.set("Bitrate")
        self.quality_dropdown = tk.Combobox(self.options_frame, textvariable=self.quality_choice, state="readonly",
                                            values=["Highest", "320k", "256k", "192k", "160k", "128k", "98k"], width=13)
        self.quality_dropdown.grid(sticky="e", padx=5, column=1, row=0)

    def gen_resolutions(self):
        self.quality_choice.set("Resolution")
        self.quality_dropdown = tk.Combobox(self.options_frame, textvariable=self.quality_choice, state="readonly",
                                            values=["Highest", "1080p", "720p", "480p", "360p", "240p"], width=13)
        self.quality_dropdown.grid(sticky="e", padx=5, column=1, row=0)

    def scrape_url(self, user_url):
        self.is_playlist = False
        download_url = user_url.get()
        # Catch playlists, will be improved at some point to catch shortened URLs.
        if "playlist" in download_url:
            self.tkGUILogger.info("Playlist URL recognised, verifying integrity.")
            try:
                self.playlist_to_dl = pafy.get_playlist(download_url)
                print("Playlist: '{}' containing {} videos in found.".format(self.playlist_to_dl["title"],
                                                                             len(self.playlist_to_dl["items"])))
                self.is_playlist = True
                self.gen_playlist_info()
            except ValueError:
                self.url_entry.delete(0, tkinter.END)
                self.url_entry.insert(index=0, string="Improper URL!")

        if self.is_playlist is False:
            try:
                self.video = pafy.new(download_url)
                self.gen_video_info(self.video)

            except ValueError:
                self.url_entry.delete(0, tkinter.END)
                self.url_entry.insert(index=0, string="Improper URL!")
                pass

from tkinter import ttk as tk
import tkinter
from tkinter import filedialog
import pkinter as pk
import logging
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
        url_label.grid(pady=5)

        self.url_entry = tk.Entry(url_entry_frame, width=72, textvariable=url_str)
        self.url_entry.grid(column=1, row=0, padx=10, pady=5)

        url_scrape_button = tk.Button(url_entry_frame, text="Scrape URL", command=lambda: self.scrape_url(url_str))
        url_scrape_button.grid(column=1, row=1, sticky="E", padx=10)

        self.video_frame = tk.Frame(self.root)
        self.video_frame.pack(fill="x")
        self.video_frame.columnconfigure(0, weight=1)

    def gen_playlist_info(self, playlist_object):
        pass

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
        video_uploader = tk.Label(self.info_frame, text=video_object.author)
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
            self.options_frame.grid(row=1, padx=10, sticky="we", columnspan=3)

            self.format_choice = tkinter.StringVar()
            self.format_choice.set("Choose a format")
            self.format_dropdown = tk.Combobox(self.options_frame, textvariable=self.format_choice, state="readonly",
                                               values=["mp3", "webm audio", "ogg", "mp4",
                                                       "webm video"], width=15)
            self.format_dropdown.grid(sticky="e", padx=[3, 0])
            self.format_dropdown.bind("<<ComboboxSelected>>", self.format_check)

            self.quality_choice = tkinter.StringVar()
            self.quality_choice.set("Choose format first")
            self.quality_dropdown = tk.Combobox(self.options_frame, textvariable=self.quality_choice, state="disabled")
            self.quality_dropdown.grid(sticky="e", padx=3, column=1, row=0)

            self.download_dir_choice = tkinter.StringVar()
            self.download_dir_choice.set(os.path.abspath("./Downloads/").replace("\\", "/"))
            self.download_dir_entry = tk.Entry(self.options_frame, textvariable=self.download_dir_choice, width=26)
            self.download_dir_window_open = tk.Button(self.options_frame, text="Browse...", command=self.browse_dirs)
            self.download_dir_entry.grid(sticky="e", column=2, row=0)
            self.download_dir_window_open.grid(sticky="e", column=3, row=0, padx=[3, 1])

            self.options_gen = True

    def browse_dirs(self):
        download_dir_choice = filedialog.askdirectory(parent=self.root, initialdir="./Downloads/", mustexist=True,
                                                      title="Choose a download directory")
        self.download_dir_choice.set(download_dir_choice)

    def format_check(self, etc):
        possible_formats = {"audio": ["mp3", "m4a", "webm audio", "ogg"], "video": ["mp4", "webm video"]}
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
                                            values=["Highest", "320k", "256k", "192k", "160k", "128k", "98k"])
        self.quality_dropdown.grid(sticky="e", padx=5, column=1, row=0)

    def gen_resolutions(self):
        self.quality_choice.set("Resolution")
        self.quality_dropdown = tk.Combobox(self.options_frame, textvariable=self.quality_choice, state="readonly",
                                            values=["Highest", "1080p", "720p", "480p", "360p", "240p"])
        self.quality_dropdown.grid(sticky="e", padx=5, column=1, row=0)

    def scrape_url(self, user_url):
        is_playlist = False
        download_url = user_url.get()
        # Catch playlists, will be improved at some point to catch shortened URLs.
        if "playlist" in download_url:
            self.tkGUILogger.info("Playlist URL recognised, verifying integrity.")
            try:
                playlist_to_dl = pafy.get_playlist(download_url)
                print("Playlist: '{}' containing {} videos in found.".format(playlist_to_dl["title"],
                                                                             len(playlist_to_dl["items"])))
                self.gen_playlist_info(playlist_to_dl)
            except ValueError:
                self.url_entry.delete(0, tkinter.END)
                self.url_entry.insert(index=0, string="Improper URL!")

        if is_playlist is False:
            try:
                video = pafy.new(download_url)
                self.gen_video_info(video)

            except ValueError:
                self.url_entry.delete(0, tkinter.END)
                self.url_entry.insert(index=0, string="Improper URL!")
                pass

from tkinter import ttk as tk
import tkinter
import pkinter as pk
import logging
import pafy


class TkGUI:
    def __init__(self, root):
        self.tkGUILogger = logging.getLogger("PlaylistDL.tk_core.TkGUI")
        self.root = root
        self.options_gen = False
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
        url_scrape_button.grid(column=1, row=1, sticky="E", padx=10, pady=[0, 5])

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
            options_frame = tk.LabelFrame(self.video_frame, labelanchor="n", text="Options")
            options_frame.grid(row=1, padx=10, sticky="we", columnspan=3)

            self.format_choice = tkinter.StringVar()
            self.format_choice.set("Choose a format")
            self.format_dropdown = tk.Combobox(options_frame, textvariable=self.format_choice, state="readonly",
                                               values=["mp3", "webm audio", "ogg", "mp4",
                                                       "webm video"], width=15)
            self.format_dropdown.grid(sticky="e", padx=[0, 5])
            self.format_dropdown.bind("<<ComboboxSelected>>", self.format_check)

            self.options_gen = True

    def format_check(self):
        possible_formats = {"audio": ["mp3", "m4a", "webm audio", "ogg"], "video": ["mp4", "webm video"]}
        local_format_choice = self.format_dropdown.get()
        if local_format_choice == "Choose a format":
            return

        if local_format_choice in possible_formats["audio"]:
            self.gen_bitrates()
        elif local_format_choice in possible_formats["video"]:
            self.gen_resolutions()

    def gen_bitrates(self):
        pass
    
    def gen_resolutions(self):
        pass

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

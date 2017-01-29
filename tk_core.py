from tkinter import ttk as tk
import tkinter
import pkinter as pk
import logging
import pafy
# https://www.youtube.com/watch?v=DG2KHJILDzo


class TkGUI:
    def __init__(self, root):
        self.tkGUILogger = logging.getLogger("PlaylistDL.tk_core.TkGUI")
        self.root = root
        self.root.title("YTPlaylistDL")
        self.gen_base_widgets()

    def gen_base_widgets(self):
        url_str = tkinter.StringVar()
        url_entry_frame = tk.Frame(self.root)
        url_entry_frame.pack(fill="x")
        url_label = tk.Label(url_entry_frame, text="Youtube URL:")
        url_label.grid(pady=5)
        global url_entry
        url_entry = tk.Entry(url_entry_frame, width=72, textvariable=url_str)
        url_entry.grid(column=1, row=0, padx=10, pady=5)
        url_scrape_button = tk.Button(url_entry_frame, text="Scrape URL", command=lambda: self.scrape_url(url_str))
        url_scrape_button.grid(column=1, row=1, sticky="E", padx=10, pady=[0, 5])

    def gen_playlist_info(self, playlist_object):
        pass

    def gen_video_info(self, video_object):
        global info_frame
        try:
            info_frame.pack_forget()
            info_frame.destroy()
        except NameError:
            pass
        info_frame = tk.LabelFrame(self.root, labelanchor="n", text="Video Information")
        info_frame.pack(padx=10, fill="x")
        video_title_label = tk.Label(info_frame, text="Title:")
        video_title = tk.Label(info_frame, text=video_object.title)
        video_title_label.grid(sticky="w", padx=[0, 10])
        video_title.grid(column=1, row=0, sticky="w")
        video_views_label = tk.Label(info_frame, text="Views:")
        video_views = tk.Label(info_frame, text=str(video_object.viewcount))
        video_views_label.grid(column=0, row=2, sticky="w", padx=[0, 10])
        video_views.grid(column=1, row=2, sticky="w")
        video_uploader_label = tk.Label(info_frame, text="Uploader: ")
        video_uploader = tk.Label(info_frame, text=video_object.author)
        video_uploader_label.grid(column=0, row=3, sticky="w", padx=[0, 10])
        video_uploader.grid(column=1, row=3, sticky="w")
        video_uploaded_label = tk.Label(info_frame, text="Uploaded:")
        video_uploaded = tk.Label(info_frame, text=video_object.published)
        video_uploaded_label.grid(column=0, row=4, sticky="w", padx=[0, 10])
        video_uploaded.grid(column=1, row=4, sticky="w")
        self.generate_options()

    def generate_options(self):
        options_frame = tk.LabelFrame(self.root, labelanchor="n", text="Options")
        options_frame.pack(padx=10, fill="x")
        format_choice = tkinter.StringVar()
        format_choice.set("Choose a format")
        format_dropdown = tk.Combobox(options_frame, textvariable=format_choice, state="readonly",
                                      values=["Choose a format", "mp3", "webm audio", "ogg", "mp4", "webm video"])
        format_dropdown.grid(sticky="we")
        format_dropdown.set(value=0)


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
                url_entry.delete(0, tkinter.END)
                url_entry.insert(index=0, string="Improper URL!")

        if is_playlist is False:
            try:
                video = pafy.new(download_url)
                self.gen_video_info(video)

            except ValueError:
                url_entry.delete(0, tkinter.END)
                url_entry.insert(index=0, string="Improper URL!")
                pass

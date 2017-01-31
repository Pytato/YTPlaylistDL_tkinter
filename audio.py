import logging
import time


class AudioDL:
    def __init__(self):
        self.audioDL_logger = logging.getLogger("PlaylistDL.tk_core.audio.audioDL")
        self.audioDL_logger.debug("tk_core.audio.audioDL initialised.")

    def audio_playlist_gather(self, set, fformat="mp3", quality="", bitrate=0):
        self.audioDL_logger.debug("tk_core.audio.audioDL.audio_playlist_dl() started.")
        best_bitrates = {}
        time.sleep(0.2)
        if quality == "Highest":
            for video in set["items"]:
                dl_stream = video["pafy"].getbestaudio(preftype=fformat)
                if dl_stream is not None:
                    dl_url = dl_stream.url
                    best_bitrates[video["pafy"].title+"."+fformat] = dl_url
                    self.audioDL_logger.info("Found audio of '{0}' in quality, {1}. Added to list."
                                             .format(video["pafy"].title,
                                                     video["pafy"].getbestaudio(preftype=fformat).bitrate))
                else:
                    self.audioDL_logger.warning(video["pafy"].title+" does not have a stream in your chosen format, skipping.")
            self.audioDL_logger.info("List generation complete.")
            export_data = [best_bitrates, set["title"]]
            return export_data

        elif quality == "Low":
            for video in set["items"]:
                stream_qualities = {}
                # Iterate through the available audiostreams
                for stream in video["pafy"].audiostreams:
                    # If the stream is the right filetype, add the bitrate to the stream_qualitites array
                    if stream.extension == fformat:
                        # Generate a friendly bitrate number
                        s_bitrate = int(stream.bitrate.replace("k", ""))
                        # And give it the key value of its bitrate with a URL to download from attached.
                        stream_qualities[s_bitrate] = stream.url
                # Find the closest bitrate available in the dictionary and get the URL attached,
                # stick the URL in another array.
                closest_bitrate = min(stream_qualities, key=lambda x: abs(x-bitrate))
                best_bitrates[video["pafy"].title+"."+fformat] = stream_qualities[closest_bitrate]
                self.audioDL_logger.info("Found audio of '{0}' in quality, {1}k. Added to list."
                                         .format(video["pafy"].title, closest_bitrate))
            self.audioDL_logger.info("List generation complete.")
            export_data = [best_bitrates, set["title"]]
            return export_data
        else:
            self.audioDL_logger.error("Neither 'High' or 'Low' quality selected.")

    def audio_single_gather(self, audio_pafy, fformat, quality, bitrate=0):
        self.audioDL_logger.debug("tk_core.audio.audioDL.audio_single_gather() started.")
        # High quality downloads are the simplest to do
        # For compatibility
        export_url_dict = {}
        if quality == "Highest":
            self.audioDL_logger.info("Finding highest quality audio file in your chosen format.")
            audio_stream = audio_pafy.getbestaudio(preftype=fformat)
            export_url_dict[audio_pafy.title+"."+fformat] = audio_stream.url
            export_data = [export_url_dict, audio_pafy.title]
            return export_data

        elif quality == "Low":
            stream_qualities = {}
            best_bitrates = {}
            for stream in audio_pafy.audiostreams:
                if stream.extension == fformat:
                    stream_bitrate = int(stream.bitrate.replace("k", ""))
                    stream_qualities[stream_bitrate] = stream.url
            closest_bitrate = min(stream_qualities, key=lambda x: abs(x - bitrate))
            best_bitrates[audio_pafy.title + "." + fformat] = stream_qualities[closest_bitrate]
            self.audioDL_logger.info("Found audio of '{0}' in quality, {1}k. Added to list."
                                     .format(audio_pafy.title, closest_bitrate))
            export_data = [best_bitrates, audio_pafy.title]
            return export_data


import logging
import pafy
import time


class VideoDL:
    def __init__(self):
        self.video_logger = logging.getLogger("PlaylistDL.core.video.VideoDL")
        self.video_logger.debug("Logging init complete, class init complete.")

    def video_playlist_gather(self, set, fformat, quality):
        self.video_logger.debug("core.video.videoDL.video_playlist_gather() started.")
        best_resolutions = {}
        time.sleep(0.2)
        if quality == "High":
            for video in set["items"]:
                dl_stream = video["pafy"].getbestvideo(preftype=fformat)
                if dl_stream is not None:
                    dl_url = dl_stream.url
                    best_resolutions[video["pafy"].title+"."+fformat] = dl_url
                    self.video_logger.info("Found video of '{0}' in quality, {1}. Added to list."
                                           .format(video["pafy"].title,
                                                   video["pafy"].getbestvideo(preftype=fformat).resolution))
                else:
                    self.video_logger.warning(video["pafy"].title+" does not have a stream in your chosen format, skipping.")
            self.video_logger.info("List generation complete.")
            core.download_from_url(best_resolutions, set["title"])
        elif quality == "Low":
            # Asks for preferred resolution
            choices = [96, 128, 160, 192, 256, 320]
            resolution = 0
            while resolution not in choices:
                resolution = int(input("Resolution choices: {}\n\nEnter desired resolution (higher number is higher quality): ".format(choices)))
            self.video_logger.info(
                "resolution accepted, generating array of video streams that have a closest match to choice")
            for video in set["items"]:
                stream_qualities = {}
                # Iterate through the available videostreams
                for stream in video["pafy"].videostreams:
                    # If the stream is the right filetype, add the resolution to the stream_qualitites array
                    if stream.extension == fformat:
                        # Generate a friendly resolution number
                        s_resolution = int(stream.resolution.replace("p", ""))
                        # And give it the key value of its resolution with a URL to download from attached.
                        stream_qualities[s_resolution] = stream.url
                # Find the closest resolution available in the dictionary and get the URL attached,
                # stick the URL in another array.
                closest_resolution = min(stream_qualities, key=lambda x: abs(x-resolution))
                best_resolutions[video["pafy"].title+"."+fformat] = stream_qualities[closest_resolution]
                self.video_logger.info("Found video of '{0}' in quality, {1}k. Added to list."
                                       .format(video["pafy"].title, closest_resolution))
            self.video_logger.info("List generation complete.")
            core.download_from_url(best_resolutions, set["title"])
        else:
            self.video_logger.error("Neither 'High' or 'Low' quality selected.")


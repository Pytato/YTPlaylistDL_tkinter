# license stuff

import logging
import os
import time
import configparser
from datetime import datetime
import tkinter

import tk_core

# Setup
possible_logging_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
print("Gathering essential cfg options.")
cfg = configparser.ConfigParser()
cfg.read("./cfg/config.ini")
cfg_log_level = (cfg.get("Logging", "log_level")).upper()
if cfg_log_level not in possible_logging_levels:
    print("Logging level chosen is incorrect.")
    exit()
cfg_log_level = "logging."+cfg_log_level
print("Starting PlaylistDL.\n\nChecking for missing paths.")
root_paths = [cfg.get("Logging", "logging_file_location"), "./Downloads"]
for route_p in root_paths:
    if os.path.exists(route_p) is False:
        os.mkdir(route_p)
        print("Regenerated the path, "+route_p+".")
time.sleep(0.15)
# Logging
# Generate main logger
main_logger = logging.getLogger('PlaylistDL')
main_logger.setLevel(eval(cfg_log_level))
# Generate a standard format (save line room, PEP8 and sanity)
log_formats = logging.Formatter("{} | [%(name)s] | [%(levelname)s] : %(message)s"\
                                .format(datetime.strftime(datetime.today(), format="[%d-%m-%y | %H:%M:%S]")))
# Set up the handler for stream
stream_h = logging.StreamHandler()
stream_h.setFormatter(log_formats)
# Attach it to the main logger
main_logger.addHandler(stream_h)
if cfg.getboolean("Logging", "logging_to_file") is True:
    # Set up the handler for log files
    file_h = logging.FileHandler(filename="{}{}.log".format(cfg.get("Logging", "logging_file_location"),
                                                            datetime.strftime(datetime.today(),
                                                                              format="%d-%m-%y_%H%M%S")))
    file_h.setFormatter(log_formats)
    main_logger.addHandler(file_h)
main_logger.info("Logging has been configured, if you want to change formatting you will have to alter the source.")
main_window = tkinter.Tk()
tk_core_class = tk_core.TkGUI(main_window)
tk_core_class.mainloop()

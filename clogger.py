import logging
import datetime
import os

watch_log = logging.getLogger('autoganjlogs')
timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
watch_log.setLevel(logging.INFO)
watch_handler = logging.FileHandler(f"logs/autoganj_{timestamp}.log")
watch_handler.setFormatter(logging.Formatter('[%(name)s] %(message)s'))
watch_log.addHandler(watch_handler)


def clogger(message):
    """
    Logging for stuff.

    Params:
        message: str The message to log.
    """
    ts = datetime.datetime.now().strftime('%Y-%m-%d @ %H:%M:%S')
    watch_log.info(f"[{ts}] :: {message}")

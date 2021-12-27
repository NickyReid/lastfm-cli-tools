import os


class Config(object):
    API_KEY = "8257fbe241e266367f27e30b0e866aba"
    CLEAN = False  # Omits lyrics with swearing
    SWEARS = ["bitch", " ass ", "asshole"]  # not included in profanity library
    LYRIC_STASH_PATH = os.path.dirname(os.path.realpath(__file__)) + "/lyricsstash"
    RAW_DATA_PATH = os.path.dirname(os.path.realpath(__file__)) + "/rawdata"
    TOP_TRACKS_LIMIT = "100"  # The number of results to fetch
    TOP_TRACKS_PERIOD_OPTIONS = ["all", "7day", "1month", "3month", "6month", "12month"]
    TOP_TRACKS_PERIOD = (
        "random"  # random | overall | 7day | 1month | 3month | 6month | 12month
    )

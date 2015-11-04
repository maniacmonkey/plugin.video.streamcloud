__author__ = 'ror'

import xbmcaddon


class Settings:
    def __init__(self):
        pass

    def index(self, params):
        xbmcaddon.Addon('plugin.video.streamcloud').openSettings()
        pass
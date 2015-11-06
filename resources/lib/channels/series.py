__author__ = 'ror'

import xbmcgui
from resources.lib import const, http
from resources.lib.items.directory_item import DirectoryItem
from resources.lib.items.video_item import VideoItem


class Series:
    def __init__(self):
        self.item_list = []
        pass

    def index(self, params):
        print 'series->index'
        for letter in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.item_list.append(
                DirectoryItem(
                    letter,
                    "?view=series&action=list&letter=%s" % letter)
            )
        return self.item_list

    def search(self, params):
        dialog = xbmcgui.Dialog()
        d = dialog.input('Search', type=xbmcgui.INPUT_ALPHANUM)

        obj = http.get("%s/search.php?type=series&title=%s&lang=%s" % (const.SERVICE_URL, d, const.LANG))

        for video in obj:
            self.item_list.append(
                DirectoryItem(
                    "%s [%s]" % (video['title'], const.LANG_CODES[video['lang']]),
                    "?view=series&action=seasons&title=%s" % video['urlTerm'],
                    "%s/thumbs/%s.jpg" % (const.SERVICE_URL, video['urlTerm'])
                )
            )
        return self.item_list

    def list(self, params):
        letter = params('letter')

        if letter == "%23":
            letter = 1

        obj = http.get("%s/?type=series&letter=%s&lang=%s" % (const.SERVICE_URL, letter, const.LANG))

        for video in obj:
            self.item_list.append(
                DirectoryItem(
                    "%s [%s]" % (video['title'], const.LANG_CODES[video['lang']]),
                    "?view=series&action=seasons&title=%s" % (video['urlTerm']),
                    "%s/thumbs/%s.jpg" % (const.SERVICE_URL, video['urlTerm'])
                )
            )
        return self.item_list

    def seasons(self, params):
        print 'series->seasons'
        print '%s/series/getSeasons.php?title=%s' % (const.SERVICE_URL, params('title'))

        obj = http.get('%s/series/getSeasons.php?title=%s' % (const.SERVICE_URL, params('title')))

        for season in obj['seasons']:
            self.item_list.append(
                DirectoryItem(
                    "Season %s" % season,
                    "?view=series&action=episodes&title=%s&season=%s" % (params('title'), season)
                )
            )

        return self.item_list

    def episodes(self, params):
        print 'series->episodes'
        try:
            obj = http.get("%s/series/getEpisodes.php?title=%s&season=%s" %
                           (const.SERVICE_URL, params('title'), params('season')))

            if len(obj['episodes']):
                for episode in obj['episodes']:
                    self.item_list.append(
                        VideoItem(
                            "Episode %s" % episode,
                            "?view=player&action=start&title=%s&season=%s&episode=%s" %
                            (params('title'), params('season'), episode)
                        )
                    )
                return self.item_list
            else:
                raise Exception('Episodes not found')
        except Exception, e:
            print 'StreamCloud Error occurred: %s' % e
            dialog = xbmcgui.Dialog()
            dialog.ok("Error", "No Episodes hosted by StreamCloud in this Season")
        pass
import sys
import re

import xbmcgui
import xbmcplugin
from resources.lib.items.directory_item import DirectoryItem
from resources.lib.items.action_item import ActionItem
from resources.lib.items.video_item import VideoItem
from resources.lib import const, http
from resources.lib.channels.movies import Movies
from resources.lib.channels.documentations import Documentations
from resources.lib.channels.series import Series
from resources.lib.settings import Settings
from resources.lib.player import Player


class StreamCloud:
    def __init__(self):
        params = http.get_params(sys.argv[2])
        self.get = params.get
        self.item_list = []
        self.run()
        pass

    def run(self):
        view = self.get('view')
        action = self.get('action')
        items = self.dispatch(view, action, self.get)

        if items:
            self.item_list = items

        if self.get('action') is None:
            self.navigation(self.get("view"))

        for item in self.item_list:
            if isinstance(item, DirectoryItem):
                self.add_directory_item(item)     
            elif isinstance(item, ActionItem):
                self.add_action_item(item)
            elif isinstance(item, VideoItem):
                self.add_video_item(item)
                
        xbmcplugin.endOfDirectory(const.ADDON_HANDLE)
        pass

    def dispatch(self, view, action, params):
        if view is None or action is None:
            return

        instance = getattr(sys.modules[__name__], view.title())()
        return getattr(instance, action)(params)
        pass

    def add_directory_item(self, item):
        li = xbmcgui.ListItem(label=item.name, thumbnailImage=item.image)

        # check path is relative or absolute
        if re.search("^\?", item.path):
            url = const.BASE_URL + item.path
        else:
            url = item.path

        xbmcplugin.addDirectoryItem(handle=const.ADDON_HANDLE, url=url, listitem=li, isFolder=True)
        pass

    def add_action_item(self, item):
        li = xbmcgui.ListItem(label=item.name, thumbnailImage=item.image)
        xbmcplugin.addDirectoryItem(
            handle=const.ADDON_HANDLE, url=const.BASE_URL + item.path, listitem=li, isFolder=False
        )
        pass
        
    def add_video_item(self, item):
        li = xbmcgui.ListItem(label=item.title, thumbnailImage=item.image)
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(
            handle=const.ADDON_HANDLE, url=const.BASE_URL + item.path, listitem=li, isFolder=False
        )
        pass
        
    def navigation(self, view=u""):
        if view is None:
            view = "/"
        else:
            view = "/%s" % view

        navigation = {
            '/': {
                'Movies':                        '?view=movies',
                'Series (by kinox.to)':          '?view=series',
                'Series (by serienstream.to)':   'plugin://plugin.video.serienstream/',
                'Documentations':                '?view=documentations',
                'Settings':                      '?view=settings&action=index',
            },
            '/movies': {
                'Search':                        '?view=movies&action=search',
                'A-Z':                           '?view=movies&action=index'
            },
            '/documentations': {
                'Search':                        '?view=documentations&action=search',
                'A-Z':                           '?view=documentations&action=index'
            },
            '/series': {
                'Search':                        '?view=series&action=search',
                'A-Z':                           '?view=series&action=index'
            },
        }

        if view not in navigation:
            return

        for key in sorted(navigation[view]):
            if re.search('Settings', key):
                self.item_list.append(
                    ActionItem(key, navigation[view][key])
                )
            else:
                self.item_list.append(
                    DirectoryItem(key, navigation[view][key])
                )
        pass
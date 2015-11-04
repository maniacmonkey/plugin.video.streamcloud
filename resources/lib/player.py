__author__ = 'ror'

import re
import xbmcgui
import xbmcplugin
from resources.lib import const, http
from resources.lib.url_resolver import StreamcloudResolver


class Player:
    def __init__(self):
        pass

    def start(self, params):
        media_url = self.get_media_url(params)

        if media_url:
            item = xbmcgui.ListItem(path=media_url)
            xbmcplugin.setResolvedUrl(const.ADDON_HANDLE, True, item)
        pass

    def get_media_url(self, params):
        try:
            res = StreamcloudResolver()
            file_url = None

            mirror_count = 1
            switch = False
            x = 1

            while x <= mirror_count:
                url = res.get_mirror_url(params('title'), x, params('season'),  params('episode'))
                obj = http.get(url)

                if obj is not None and 'Stream' in obj:
                    m = re.search('<a href="(.+?)"', str(obj['Stream']))
                    file_url = res.get_media_url(m.group(1))

                    if res.canceled is True:
                        raise Exception('CANCELED')

                    if file_url is None and switch is False:
                        c = re.search('<b>Mirror</b>: \d+/(\d+)', str(obj['Replacement']))

                        if c:
                            mirror_count = int(c.group(1))
                        switch = True

                if file_url:
                    return file_url

                x += 1

            if not file_url:
                raise Exception('FILE_NOT_FOUND')

        except Exception, e:
            print 'StreamCloud Error occurred: %s' % e

            if str(e) == 'FILE_NOT_FOUND':
                dialog = xbmcgui.Dialog()
                dialog.ok("StreamCloud", "File Not Found or removed")
        pass
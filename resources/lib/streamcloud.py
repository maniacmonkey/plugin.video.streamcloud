import sys
import re
import xbmcgui
import xbmcplugin
import xbmcaddon
from resources.lib.url_resolver import StreamcloudResolver
from resources.lib.items.directory_item import DirectoryItem
from resources.lib.items.action_item import ActionItem
from resources.lib.items.video_item import VideoItem
from resources.lib import const, http


class StreamCloud:
    def __init__(self):
        params = self.get_params(sys.argv[2])
        self.get = params.get
        self.item_list = []
        self.run()
        pass
        
    def run(self):   
        if self.get('mode') == 'settings':
            self.settings()            
        elif self.get("mode") == 'enter':                 
            self.enter()                      
        elif self.get("mode") == 'search':
            self.search()
        elif self.get("mode") == 'az' and self.get("letter"):
            self.letter(self.get("letter"))
        elif self.get("mode") == 'az':
            self.letters() 
        elif self.get("mode") == 'seasons':
            self.seasons()
        elif self.get("mode") == 'episodes':
            self.episodes()
        elif self.get('mode') == 'play':
            self.play()
        else:
            self.navigation()

        for item in self.item_list:
            if isinstance(item, DirectoryItem):
                self.add_directory_item(item)     
            elif isinstance(item, ActionItem):
                self.add_action_item(item)
            elif isinstance(item, VideoItem):
                self.add_video_item(item)
                
        xbmcplugin.endOfDirectory(const.ADDON_HANDLE)
        pass
        
    def get_params(self, parameter_string):
        commands = {}
        split_commands = parameter_string[parameter_string.find('?')+1:]\
            .split('&')
        
        for command in split_commands:
            if len(command) > 0:
                split_command = command.split('=')
                name = split_command[0]
                value = split_command[1]
                commands[name] = value
        
        return commands
        
    def play_video(self, file_url):
        item = xbmcgui.ListItem(path=file_url)
        xbmcplugin.setResolvedUrl(const.ADDON_HANDLE, True, item)
        pass

    def add_directory_item(self, item):
        li = xbmcgui.ListItem(label=item.name, thumbnailImage=item.image)
        xbmcplugin.addDirectoryItem(
            handle=const.ADDON_HANDLE, url=const.BASE_URL + item.query,
            listitem=li, isFolder=True
        )
        pass
        
    def add_action_item(self, item):
        li = xbmcgui.ListItem(label=item.name, thumbnailImage=item.image)
        xbmcplugin.addDirectoryItem(
            handle=const.ADDON_HANDLE, url=const.BASE_URL + item.query, 
            listitem=li, isFolder=False
        )
        pass
        
    def add_video_item(self, item):
        li = xbmcgui.ListItem(label=item.title, thumbnailImage=item.image)
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(
            handle=const.ADDON_HANDLE, url=const.BASE_URL + item.query, 
            listitem=li, isFolder=False
        )
        pass
        
    def settings(self):
        xbmcaddon.Addon('plugin.video.streamcloud').openSettings()
        pass    
        
    def enter(self):
        self.item_list.append(
            DirectoryItem(
                "Search", "?mode=search&type=" + self.get('type'))
        )  
        self.item_list.append(
            DirectoryItem(
                "A-Z", "?mode=az&type=" + self.get('type'))
        )
        pass

    def navigation(self):    
        navigation = [
            {
                "name": "Movies", 
                "query": "?mode=enter&type=movies", 
                "type": "directory"
            }, 
            {
                "name": "Series",
                "query": "?mode=enter&type=series",
                "type": "directory"
            }, 
            {
                "name": "Documentations",
                "query": "?mode=enter&type=documentations",
                "type": "directory"
            }, 
            {
                "name": "Settings",
                "query": "?mode=settings",
                "type": "action"
            }
        ]
        
        for item in navigation:
            if item['type'] == 'directory':
                self.item_list.append(
                    DirectoryItem(item['name'], item['query'])
                )
            elif item['type'] == 'action':
                self.item_list.append(
                    ActionItem(item['name'], item['query'])
                )
        pass
        
    def search(self):
        type = self.get("type")
        dialog = xbmcgui.Dialog()
        d = dialog.input('Search', type=xbmcgui.INPUT_ALPHANUM)
        
        if type == "series" and d:
            obj = http.get("%s/search.php?type=series&title=%s&lang=%s" %
                           (const.SERVICE_URL, d, const.LANG))
            
            for video in obj:
                self.item_list.append(
                    DirectoryItem(
                        "%s [%s]" % (video['title'],
                                     const.LANG_CODES[video['lang']]),
                        "?mode=seasons&title=%s" %
                        (video['urlTerm']),
                        "%s/thumbs/%s.jpg" % (const.SERVICE_URL, video['urlTerm'])
                    )
                )   
        if (type == 'documentations' or type == 'movies') and d:
            obj = http.get("%s/search.php?type=%s&title=%s&lang=%s" %
                           (const.SERVICE_URL, type, d, const.LANG))
            
            for video in obj:
                self.item_list.append(
                    VideoItem(
                        "%s [%s]" % (video['title'],
                                     const.LANG_CODES[video['lang']]),
                        "?mode=play&title=" + video['urlTerm'], 
                        "%s/thumbs/%s.jpg" % (const.SERVICE_URL, video['urlTerm'])
                    )
                )
        pass
     
    def letter(self, letter):
        type = self.get("type")

        if letter == "%23":
            letter = 1
        if type == 'series':
            obj = http.get("%s/?type=series&letter=%s&lang=%s" %
                           (const.SERVICE_URL, letter, const.LANG))
        
            for video in obj:
                self.item_list.append(
                    DirectoryItem(
                        "%s [%s]" % (video['title'],
                                     const.LANG_CODES[video['lang']]),
                        "?mode=seasons&title=%s" %
                        (video['urlTerm']),
                        "%s/thumbs/%s.jpg" % (const.SERVICE_URL, video['urlTerm'])
                    )
                )
        elif type == 'movies' or type == 'documentations':
            obj = http.get("%s/?type=%s&letter=%s&lang=%s" %
                           (const.SERVICE_URL, type, letter, const.LANG))
        
            for video in obj:          
                self.item_list.append(
                    VideoItem(
                        "%s [%s]" % (video['title'],
                                     const.LANG_CODES[video['lang']]),
                        "?mode=play&title=" + video['urlTerm'],
                        "%s/thumbs/%s.jpg" % (const.SERVICE_URL, video['urlTerm'])
                    )
                ) 
        pass             
     
    def letters(self):   
        for letter in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.item_list.append(
                DirectoryItem(
                    letter, 
                    "?mode=az&type=%s&letter=%s" % (self.get('type'), letter))
            )
        pass
        
    def seasons(self):
        obj = http.get('%s/series/getSeasons.php?title=%s' %
                       (const.SERVICE_URL, self.get('title')))
        
        for season in obj['seasons']:
            self.item_list.append(
                DirectoryItem(
                    "Season %s" % season,
                    "?mode=episodes&title=%s&season=%s" %
                    (self.get('title'), season)
                )
            )
        pass
        
    def episodes(self):
        try:
            obj = http.get("%s/series/getEpisodes.php?title=%s&season=%s" %
                           (const.SERVICE_URL, self.get('title'), self.get('season')))

            if len(obj['episodes']):            
                for episode in obj['episodes']:
                    self.item_list.append(
                        VideoItem(
                            "Episode %s" % episode,
                            "?mode=play&title=%s&season=%s&episode=%s" %
                            (self.get('title'), self.get('season'), episode)
                        )
                    )
            else:
                raise Exception('Episodes not found')
        except Exception, e:
            print 'StreamCloud Error occurred: %s' % e
            dialog = xbmcgui.Dialog()
            dialog.ok("Error", "No Episodes hosted by StreamCloud in this Season")
        pass
        
    def play(self):
        # find a working mirror
        try:       
            res = StreamcloudResolver()
            file_url = None
            
            mirror_count = 1
            switch = False
            x = 1
            
            while x <= mirror_count:                   
                url = res.get_mirror_url(self.get('title'), x, self.get('season'),
                                         self.get('episode'))
                obj = http.get(url)
                
                if obj is not None and 'Stream' in obj:
                    m = re.search('<a href="(.+?)"', str(obj['Stream']))
                    file_url = res.get_media_url(m.group(1))
                    
                    if res.canceled is True:
                        raise Exception('CANCELED')
                    
                    if file_url is None and switch is False:
                        c = re.search('<b>Mirror</b>: \d+/(\d+)',
                                      str(obj['Replacement']))
                         
                        if c:
                            mirror_count = int(c.group(1))
                        switch = True

                if file_url:
                    self.play_video(file_url)
                    break
                
                x += 1              

            if not file_url:   
                raise Exception('FILE_NOT_FOUND')
                
        except Exception, e:
            print 'StreamCloud Error occurred: %s' % e
            
            if str(e) == 'FILE_NOT_FOUND':
                http.post(
                    "%s/report.php" % const.SERVICE_URL, 
                    {'type': 'unknown', 'title': self.get('title'), 'message': '404'}
                )
                dialog = xbmcgui.Dialog()
                dialog.ok("StreamCloud", "File Not Found or removed")
        pass
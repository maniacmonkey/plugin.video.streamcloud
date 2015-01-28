"""
StreamCloud streaming plugin
Copyright (C) 2014 rollov
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import re
from resources.resolver import StreamcloudResolver
from resources.lib.items.directory_item import DirectoryItem
from resources.lib.items.action_item import ActionItem 
from resources.lib.items.video_item import VideoItem
from resources import const, http

def play_video(file_url):
    item = xbmcgui.ListItem(path=file_url)
    xbmcplugin.setResolvedUrl(const.ADDON_HANDLE, True, item)

def get_params(parameterString):
    commands = {}
    splitCommands = parameterString[parameterString.find('?')+1:].split('&')
    
    for command in splitCommands: 
        if (len(command) > 0):
            splitCommand = command.split('=')
            name = splitCommand[0]
            value = splitCommand[1]
            commands[name] = value
    
    return commands
   
def add_directory_item(item):
    li = xbmcgui.ListItem(label=item.name, thumbnailImage=item.image)
    xbmcplugin.addDirectoryItem(
        handle=const.ADDON_HANDLE, url=const.BASE_URL + item.query, 
        listitem=li, isFolder=True
    )
    pass
    
def add_action_item(item):
    li = xbmcgui.ListItem(label=item.name, thumbnailImage=item.image)
    xbmcplugin.addDirectoryItem(
        handle=const.ADDON_HANDLE, url=const.BASE_URL + item.query, 
        listitem=li, isFolder=False
    )
    pass
    
def add_video_item(item):
    li = xbmcgui.ListItem(label=item.title, thumbnailImage=item.image)
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(
        handle=const.ADDON_HANDLE, url=const.BASE_URL + item.query, 
        listitem=li, isFolder=False
    )
    pass
    
def settings():
    xbmcaddon.Addon('plugin.video.streamcloud').openSettings()
    pass    
    
def enter():
    item_list.append(
        DirectoryItem(
            "Search", "?mode=search&type=" + get('type'), 'DefaultFolder.png') 
    )  
    item_list.append(
        DirectoryItem(
            "A-Z", "?mode=az&type=" + get('type'), 'DefaultFolder.png')
    )
    pass

def navigation():    
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
    
    #print const.LANG
    
    for item in navigation:
        if item['type'] == 'directory':
            item_list.append(
                DirectoryItem(item['name'], item['query'], 'DefaultFolder.png') 
            )
        elif item['type'] == 'action':
            item_list.append(
                ActionItem(item['name'], item['query'], 'DefaultFolder.png')
            )
    pass
    
def search():
    type = get("type")
    dialog = xbmcgui.Dialog()
    d = dialog.input('Search', type=xbmcgui.INPUT_ALPHANUM)
    
    if type == "series":               
        obj = http.get("%s/search.php?type=series&title=%s&lang=%s" % 
            (const.SERVICE_URL, d, const.LANG));
        
        for video in obj:
            item_list.append(
                DirectoryItem(
                    "%s [%s]" % (video['title'], 
                        const.LANG_CODES[video['lang']]),
                    "%s?mode=seasons&title=%s" % 
                        (const.BASE_URL, video['urlTerm']),
                    "%s/thumbs/%s.jpg" % (const.SERVICE_URL, video['urlTerm'])
                )
            )   
    if type == 'documentations' or type == 'movies':
        obj = http.get("%s/search.php?type=%s&title=%s&lang=%s" % 
            (const.SERVICE_URL, type, d, const.LANG))
        
        for video in obj:
            item_list.append(
                VideoItem(
                    "%s [%s]" % (video['title'], 
                        const.LANG_CODES[video['lang']]),
                    "?mode=play&title=" + video['urlTerm'], 
                    "%s/thumbs/%s.jpg" % (const.SERVICE_URL, video['urlTerm'])
                )
            )   
 
def letter(letter):
    type = get("type")

    if letter == "%23":
        letter = 1
    if type == 'series':
        obj = http.get("%s/?type=series&letter=%s&lang=%s" % 
            (const.SERVICE_URL, letter, const.LANG))
    
        for video in obj:
            item_list.append(
                DirectoryItem(
                    "%s [%s]" % (video['title'], 
                        const.LANG_CODES[video['lang']]),
                    "%s?mode=seasons&title=%s" % 
                        (const.BASE_URL, video['urlTerm']),
                    "%s/thumbs/%s.jpg" % (const.SERVICE_URL, video['urlTerm'])
                )
            )
    elif (type == 'movies' or type == 'documentations'):
        obj = http.get("%s/?type=%s&letter=%s&lang=%s" % 
            (const.SERVICE_URL, type, letter, const.LANG))           
    
        for video in obj:          
            item_list.append(
                VideoItem(
                    "%s [%s]" % (video['title'], 
                        const.LANG_CODES[video['lang']]), 
                    "?mode=play&title=" + video['urlTerm'], 
                    "%s/thumbs/%s.jpg" % (const.SERVICE_URL, video['urlTerm'])
                )
            ) 
    pass             
 
def letters():   
    for letter in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        item_list.append(
            DirectoryItem(
                letter, 
                "?mode=az&type=%s&letter=%s" % (get('type'), letter), 
                'DefaultFolder.png')
        )
    pass
    
def seasons():
    obj = http.get('%s/series/getSeasons.php?title=%s' % 
        (const.SERVICE_URL, get('title')))
    
    for season in obj['seasons']:
        item_list.append(
            DirectoryItem(
                "Season %s" % season,
                "%s?mode=episodes&title=%s&season=%s" % 
                    (const.BASE_URL, get('title'), season),
                'DefaultFolder.png'
            )
        )
    pass
    
def episodes():
    try:
        obj = http.get("%s/series/getEpisodes.php?title=%s&season=%s" % 
            (const.SERVICE_URL, get('title'), get('season')))

        if len(obj['episodes']):            
            for episode in obj['episodes']:
                item_list.append(
                    VideoItem(
                        "Episode %s" % episode,
                        "%s?mode=play&title=%s&season=%s&episode=%s" % 
                            (const.BASE_URL, get('title'), get('season'), 
                             episode),
                        "DefaultVideo.png"
                    )
                )
        else:
            raise Exception ('Episodes not found')        
    except Exception, e:
        print 'Streamcloud Error occured: %s' % e
        dialog = xbmcgui.Dialog()
        dialog.ok("Error", "No Episodes hosted by StreamCloud in this Season")
    pass
    
def play():
    # find a working mirror
    try:       
        res = StreamcloudResolver()
        file_url = None
        
        mirror_count = 1
        switch = False
        x = 1
        
        while x <= mirror_count:                   
            url = res.get_mirror_url(get('title'), x, get('season'), 
                get('episode'))
            obj = http.get(url)
            
            if obj != None and obj.has_key('Stream'):
                m = re.search('<a href=\"(.+?)\"', str(obj['Stream']))
                file_url = res.get_media_url(m.group(1))
                
                if res.canceled == True:
                    raise Exception ('CANCELED')
                
                if file_url == None and switch == False:
                     c = re.search('<b>Mirror<\/b>: \d+\/(\d+)', 
                        str(obj['Replacement']))
                     
                     if c:
                        mirror_count = int(c.group(1))
                     switch = True

            if file_url:
                play_video(file_url)
                break
            
            x += 1              

        if not file_url:   
            raise Exception ('FILE_NOT_FOUND')          
    except Exception, e:
        print 'Streamcloud Error occured: %s' % e
        
        if str(e) == 'FILE_NOT_FOUND':
            http.post(
                "%s/report.php" % const.SERVICE_URL, 
                {'type' : 'unknown', 'title' : get('title'), 'message' : '404'}
            )
            dialog = xbmcgui.Dialog()
            dialog.ok("StreamCloud", "File Not Found or removed")
    pass
        
params = get_params(sys.argv[2])
get = params.get
item_list = []
       
if get('mode') == 'settings':
    settings()            
elif get("mode") == 'enter':                 
    enter()                      
elif get("mode") == 'search':
    search()
elif get("mode") == 'az' and get("letter"):
    letter(get("letter"))
elif get("mode") == 'az':
    letters() 
elif get("mode") == 'seasons':
    seasons()
elif get("mode") == 'episodes':
    episodes()
elif get('mode') == 'play':
    play()
else:
    navigation()

for item in item_list:
    if isinstance(item, DirectoryItem):
        add_directory_item(item)     
    elif isinstance(item, ActionItem):
        add_action_item(item)
    elif isinstance(item, VideoItem):
        add_video_item(item)
        
xbmcplugin.endOfDirectory(const.ADDON_HANDLE)
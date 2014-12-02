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
import urllib
import urllib2
import json
import re
from resolver import StreamcloudResolver

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'movies')
service_url = "http://scheinweb.de/sc";

def play_video(file_url):
    item = xbmcgui.ListItem(path=file_url)
    xbmcplugin.setResolvedUrl(addon_handle, True, item)

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
    
def http_GET(url, data_type='json'):
    req = urllib2.Request(url)
    res = urllib2.urlopen(req).read()
	
    try:
        if data_type == 'json':
            return json.loads(res)
        else: 
            return res
    except Exception, e:
        return None
		
def http_POST(url, values):
    # https://docs.python.org/2/howto/urllib2.html
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    res = urllib2.urlopen(req)
    return res

if __name__ == "__main__":
    if (not sys.argv[2]):
        folders = [{"name": "Movies", "type": "movies"}, {"name": "Series", "type": "series"}, {"name": "Documentations", "type": "documentations"}]
                
        for folder in folders:
            li = xbmcgui.ListItem(folder['name'], iconImage='DefaultFolder.png')
            xurl = "%s?mode=enter&type=%s" % (base_url, folder['type'])
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=xurl, listitem=li, isFolder=True)
        
    else:
        params = get_params(sys.argv[2])
        get = params.get
        
        if (get("mode") == 'enter'):
            folders = [{"name": "Search", "mode": "search"}, {"name": "A-Z", "mode": "az"}]
            
            for folder in folders:
                li = xbmcgui.ListItem(folder['name'], iconImage='DefaultFolder.png')
                xurl = "%s?mode=%s&type=%s" % (base_url, folder['mode'], get('type'))
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=xurl, listitem=li, isFolder=True)
                   
        elif (get("mode") == 'search'):
            type = get("type")
            dialog = xbmcgui.Dialog()
            d = dialog.input('Search', type=xbmcgui.INPUT_ALPHANUM)
            
            if type == "series":               
                obj = http_GET("%s/search.php?type=series&title=%s" % (service_url, d));
                
                for x in obj:
                    li = xbmcgui.ListItem(x['title'], iconImage='%s/thumbs/%s.jpg' % (service_url, x['urlTerm']))
                    xurl = "%s?mode=seasons&title=%s" % (base_url, x['urlTerm'])
                    xbmcplugin.addDirectoryItem(handle=addon_handle, url=xurl, listitem=li, isFolder=True)
            
            if type == 'documentations' or type == 'movies':
                obj = http_GET("%s/search.php?type=%s&title=%s" % (service_url, type, d))
                
                for x in obj:
                    li = xbmcgui.ListItem(x['title'], iconImage='%s/thumbs/%s.jpg' % (service_url, x['urlTerm']))
                    li.setProperty('IsPlayable', 'true')
                    xurl = "%s?mode=play&title=%s" % (base_url, x['urlTerm'])
                    xbmcplugin.addDirectoryItem(handle=addon_handle, url=xurl, listitem=li)

        elif (get("mode") == 'az' and get("letter")):
            type = get("type")
            letter = get('letter')
            if letter == "%23":
                letter = 1
        
            if (type == 'series'):
                obj = http_GET("%s/?type=series&letter=%s" % (service_url, letter))
            
                for x in obj:
                    li = xbmcgui.ListItem(x['title'], iconImage='%s/thumbs/%s.jpg' % (service_url, x['urlTerm']))
                    xurl = "%s?mode=seasons&title=%s" % (base_url, x['urlTerm'])
                    xbmcplugin.addDirectoryItem(handle=addon_handle, url=xurl, listitem=li, isFolder=True)
            
            elif (type == 'movies' or type == 'documentations'):
                obj = http_GET("%s/?type=%s&letter=%s" % (service_url, type, letter))           
            
                for x in obj:
                    li = xbmcgui.ListItem(x['title'], iconImage='%s/thumbs/%s.jpg' % (service_url, x['urlTerm']))
                    xurl = "%s?mode=play&title=%s" % (base_url, x['urlTerm'])
                    li.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(handle=addon_handle, url=xurl, listitem=li)
        
        elif (get("mode") == 'az'):
            a = ["#", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
            
            for letter in a:
                li = xbmcgui.ListItem(letter, iconImage='DefaultFolder.png')
                xurl = "%s?mode=az&type=%s&letter=%s" % (base_url, get('type'), letter)
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=xurl, listitem=li, isFolder=True)
           
        elif (get("mode") == 'seasons'):
            obj = http_GET('%s/series/getSeasons.php?title=%s' % (service_url, get('title')))
            
            for x in obj['seasons']:
                li = xbmcgui.ListItem("Season %s" % x, iconImage='DefaultFolder.png')
                xurl = "%s?mode=episodes&title=%s&season=%s" % (base_url, get('title'), x)
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=xurl, listitem=li, isFolder=True) 
           
        elif (get("mode") == 'episodes'):
            try:
                obj = http_GET("%s/series/getEpisodes.php?title=%s&season=%s" % (service_url, get('title'), get('season')))

                if len(obj['episodes'])   :            
                    for x in obj['episodes']:
                        li = xbmcgui.ListItem("Episode %s" % x, iconImage='DefaultVideo.png')
                        li.setProperty('IsPlayable', 'true')
                        xurl = "%s?mode=play&title=%s&season=%s&episode=%s" % (base_url, get('title'), get('season'), x)
                        xbmcplugin.addDirectoryItem(handle=addon_handle, url=xurl, listitem=li)
                else:
                    raise Exception ('Episodes not found')
                    
            except Exception, e:
                print 'Streamcloud Error occured: %s' % e
                dialog = xbmcgui.Dialog()
                dialog.ok("Error", "No Episodes hosted by StreamCloud in this Season")
                
        elif (get('mode') == 'play'):
            # find a working mirror
            try:       
                res = StreamcloudResolver()
                file_url = None
                
                mirror_count = 1
                switch = False
                x = 1
                
                while x <= mirror_count:                   
                    url = res.get_mirror_url(get('title'), x, get('season'), get('episode'))
                    obj = http_GET(url)
                    
                    if obj != None and obj.has_key('Stream'):
                        m = re.search('<a href=\"(.+?)\"', str(obj['Stream']))
                        file_url = res.get_media_url(m.group(1))
                        
                        if res.canceled == True:
                            raise Exception ('CANCELED')
                        
                        if file_url == None and switch == False:
                             c = re.search('<b>Mirror<\/b>: \d+\/(\d+)', str(obj['Replacement']))
                             
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
                    http_POST("%s/report.php" % service_url, {'type' : 'unknown', 'title' : get('title'), 'message' : '404'})
                    dialog = xbmcgui.Dialog()
                    dialog.ok("StreamCloud", "File Not Found or removed")
            
xbmcplugin.endOfDirectory(addon_handle)
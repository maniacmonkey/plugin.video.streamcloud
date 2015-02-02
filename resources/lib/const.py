import sys
import xbmcplugin

BASE_URL = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])
SERVICE_URL = "http://scheinweb.de/sc"
LANG = xbmcplugin.getSetting(ADDON_HANDLE, 'prefLanguage')
LANG_CODES = {'1': "DE", '2': 'EN'}
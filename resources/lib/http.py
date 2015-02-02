import urllib
import urllib2
import json


def get(url, data_type='json'):
    req = urllib2.Request(url)
    res = urllib2.urlopen(req).read()

    try:
        if data_type == 'json':
            return json.loads(res)
        else:
            return res
    except Exception, e:
        return None


def post(url, values):
    # https://docs.python.org/2/howto/urllib2.html
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    res = urllib2.urlopen(req)
    return res
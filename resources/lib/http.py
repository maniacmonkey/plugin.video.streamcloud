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


def get_params(parameter_string):
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
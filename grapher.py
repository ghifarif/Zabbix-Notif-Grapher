#!/usr/bin/python

import json
import os
import sys
import pprint
import datetime
import requests

def main(argv):
    (params, slack) = load_params(argv)
    send_slack(params, slack)

def load_params(argv):
    slack = {'hook': argv[0],}
    if(len(argv) > 2):
        slack['channel'] = argv[1]

    params = {}
    for line in argv[2].split('\n'):
        kv = line.split(':')
        if(len(kv) > 1):
            params[kv[0].strip()] = ':'.join(kv[1:]).strip()

    items = []
    for it in [''] + list(range(1, 10)):
        item = load_item_params(['KEY', 'ID', 'NAME', 'VALUE'], it, params)
        if(('NAME' in item) and '*UNKNOWN*' not in item['NAME']):
            items.append(item)

    params['ITEMS'] = items
    return (params, slack)

def load_item_params(item_keys, item_index, params):
    item = {}
    item_index = str(item_index)
    for item_key in item_keys:
        if('ITEM_' + item_key + item_index in params):
            item[item_key] = params.pop('ITEM_' + item_key + item_index)
    return item

def send_slack(params, slack):
    itemids = '&'.join({'itemids[]=' + it['ID'] for it in params['ITEMS']})
    msg_prefix = params['MESSAGE_PREFIX'] if 'MESSAGE_PREFIX' in params else ''
    body = {
        'text': '{prefix} *{status}* {host}:[{severity}] {name} (<{zabbix}/history.php?action=showgraph&{itemids}|graph>)'.format(
            status=params['TRIGGER_STATUS'], severity=params['TRIGGER_SEVERITY'],name=params['TRIGGER_NAME'], host=params['HOST'],
            zabbix='https://YOURZBXURL', itemids=itemids, prefix=msg_prefix),
        'fallback': '{prefix} *{status}* {host}:[{severity}] {name}'.format(
            status=params['TRIGGER_STATUS'], severity=params['TRIGGER_SEVERITY'],name=params['TRIGGER_NAME'], host=params['HOST'], prefix=msg_prefix),
        'attachments': [
            {
                'color': get_status_color(params),
                'image_url': get_graph_thumb(params),
                'fields': [{
                    'title': it['NAME'],
                    'value':it['VALUE'],
                    'short':True
                } for it in params['ITEMS']
                ],
            },
        ]
    }
    if 'channel' in slack:
        body['channel'] = slack['channel']
    res = requests.post(slack['hook'], data=json.dumps(body))

def get_status_color(params):
    status = params['TRIGGER_STATUS']
    severity = params['TRIGGER_SEVERITY']
    if(status == 'OK'):
        if(severity == 'Information'):
            return '#0000FF'
        else:
            return '#00FF00'
    elif(status == 'PROBLEM'):
        if(severity == 'Information'):
            return '#0000FF'
        elif(severity == 'Warning'):
            return '#FF0000'
        else:
            return '#FF0000'
    return '#808080'

def get_graph_thumb(params):
    zabbix = ZabbixLib(host='https://$ZBXIP', user='$USER', passwd='$PASS')
    img = zabbix.loadGraphImage({it['ID'] for it in params['ITEMS']})
    path = '/???????/'+datetime.datetime.now().strftime("%xT%XZ")
    f = open("/usr/share/zabbix"+path,"w"); f.write(img); f.close()
    url = 'https://$ZBXIP'+path
    return url

class ZabbixLib:
    def __init__(self, host=None, user=None, pass=None):
        self.__auth = None
        self.__id = 1
        self.__host = host
        a = self.__request('user.login', {
            'user': 'user',
            'password': 'pass',
        })
        self.__auth = a

    def __request(self, method, param):
        body = {
            'jsonrpc': '2.0',
            'method': method,
            'params': param,
            'id': self.__id,
            'auth': self.__auth,
        }
        self.__id = self.__id + 1
        res = requests.post(self.__host + '/api_jsonrpc.php', json.dumps(body), headers={
                            'Content-Type': 'application/json'})
        obj = res.json()
        return obj['result']

    def loadGraphImage(self, itemids, period=10800):
        query = '&'.join({'period=' + str(period)} |
                         {'itemids[]=' + it for it in itemids})
        cookies = {'zbx_sessionid': self.__auth}
        res = requests.get(self.__host + '/chart.php?' +
                           query, cookies=cookies)
        return res.content

if __name__ == '__main__':
    main(sys.argv)

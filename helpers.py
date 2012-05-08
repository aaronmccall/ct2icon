import re
import unidecode
import json
import urllib2
import getpass
import templates
import random

import conf


def get_api_url():
    if not conf.api_url:
        conf.api_url = random.choice(conf.API_URLS) 
    return conf.api_url

def slugify(string):
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', '_', string)

def request_data_builder(auth={}, module='', section='', action='', data={}, filters={}):
    template = conf.REQUEST_TEMPLATE.copy()
    template['Auth'] = get_auth_data()
    template['Request'] = {
        'Module': module,
        'Section': section,
        'Action': action
    }
    if data:
        template['Request']['Data'] = data
    if filters:
        template['Request']['Filters'] = filters
    print template
    return template



def post_json(url, post_data):
    request = urllib2.Request(url, data=json.dumps(post_data), headers={
        'Content-Type': 'application/json'
    })

    try:
        response = urllib2.urlopen(request)
        return json.loads(response.read())
    except urllib2.HTTPError, err:
        return err


def get_auth_data():
    if conf.auth_data:
        return conf.auth_data
    username = raw_input('Username: ')
    phone_number = raw_input('Phone Number: ')
    password = getpass.getpass()

    conf.auth_data.update({
        'Username': username,
        'Phone': phone_number,
        'Password': password
    })

    return conf.auth_data

def set_session(session):
    conf.auth_data.clear()
    conf.auth_data['session'] = session
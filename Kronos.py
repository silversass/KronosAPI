import requests
import xml.etree.ElementTree as ET
from lxml import html
import re

class Character(object):

    def __init__(self, name=None, realm=None):

        """

            Character attributes:

            name, realm, guildName, level,
            factionId, genderId, raceId, classId

            Slots:
            0 = head
            1 = neck
            2 = shoulder
            3 = shirt
            4 = chest
            5 = waist
            6 = legs
            7 = feet
            8 = wrist
            9 = hands
            10 = finger 1
            11 = finger 2
            12 = trinket 1
            13 = trinket 2
            14 = back
            15 = main hand
            16 = off hand
            17 = ranged
            18 = tabard
        """

        if name is not None and realm is not None:
            self.gear = {str(k): None for k in xrange(19)}
            self.get_data(name, realm)

    def get_data(self, name, realm):

        url = 'http://armory.twinstar.cz/character-sheet.xml'
        payload = {'r': realm, 'cn': name}

        r = connect(url, payload)

        c_keys = ['name', 'realm', 'guildName', 'level', 'factionId',
                  'genderId', 'raceId', 'classId']

        """
            item_keys = ['id', 'slot', 'name', 'permanentenchant',
                          'randomPropertiesId', 'rarity']
        """

        def process(iterable, keys):
            root = ET.fromstring(r.text)
            for child in root.iter(iterable):
                if iterable == 'item':
                    self.gear[child.attrib['slot']] = child.attrib['id']
                else:
                    for k in keys:
                        setattr(self, k, child.attrib[k])

        # Currently pulling only character info and gear ID's
        process('character', c_keys)
        process('item', keys=None)


class Item(object):

    def __init__(self, ID=None):

        if ID is not None:
            self.strength = 0
            self.agility = 0
            self.stamina = 0
            self.intellect = 0
            self.spirit = 0
            self.armor = 0
            self.get_data(ID)

    def get_data(self, ID):

        url = 'http://vanilla-twinhead.twinstar.cz'
        payload = {'item': ID}

        r = connect(url, payload)

        all_stats = ['Strength', 'Agility', 'Stamina',
                     'Intellect', 'Spirit', 'Armor']

        # Parse raw html page into an object with a tree structure
        tree = html.fromstring(r.content)

        stats = [d.strip('+') for d in tree.xpath('//td/text()')]
        stats = [''.join([d for s in all_stats if s in d]).split() for d in stats]
        stats = filter(None, stats)

        for d in stats:
            key = d[1]
            value = int(d[0])
            setattr(self, key.lower(), value)


def search(slot, level):

    url = 'https://vanilla-twinhead.twinstar.cz/?items'
    payload = {
                'is_name': '',
                'is_slot[]': slot,
                'is_quality[]': '2, 3, 4, 5, 6, 7',
                'is_level_min': '',
                'is_level_max': '',
                'is_rlevel_min': '',
                'is_rlevel_max': level,
                'is_do_search': 'Submit'
            }

    r = requests.post(url, data=payload)
    temp = re.search('data:\[[^<>]*\]', r.content).group()
    item_list = map(lambda x: int(x[3:]), re.findall(':?id:\d+', temp))

    return item_list


def connect(url, payload):
    try:
        r = requests.get(url, params=payload)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print '[ERROR] ', e
    return r
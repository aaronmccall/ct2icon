""" Transforms for people and households """
import re

class InvalidPerson(Exception):
    pass

csz_re = re.compile(r"^(?P<city>[^,]+),\s*(?P<state>[a-zA-Z]+)\s*(?P<zip>\d{5}-*\d{0,4})")
def csz_handler(key, value, out_dict):
    csz_match = csz_re.match(value)
    if csz_match:
        out_dict.update(csz_match.groupdict())
    else:
        raise InvalidPerson()

addr2_re = re.compile(r"(?P<address_1>^.*)(?=ste|suite|apt|space|cabin)(?P<address_2>.*)", re.I)
def addr_handler(key, value, out_dict):
    two_addresses = addr2_re.match(value)
    if two_addresses:
        out_dict['address_1'] = two_addresses.group('address_1').strip()
        out_dict['address_2'] = two_addresses.group('address_2').strip()
    else:
        out_dict['address_1'] = value

def phone_mapper(key, value, person, out_dict, phones):
    if key == 'primary_phone':
        out_dict['phone'] = value
    else:
        if value in [person['Primary Phone'], out_dict['phone']]:
            return
        if not value:
            return
        phones.append({
            'id': key.replace('_phone', '').title(),
            'phone': value
        })

STATUS_MAP = {
    'Guest': 'Newcomer',
    'Unknown': 'Newcomer'
}
def status_handler(key, value, out_dict):
    if value in STATUS_MAP:
        out_dict['status'] = STATUS_MAP[value]
    else:
        out_dict['status'] = value

def gender_handler(key, value, out_dict):
    out_dict[key] = value[:1]

def birthday_handler(key, value, out_dict):
    if not value:
        return None
    date_parts = value.split('/')
    if len(date_parts) == 3:
        year_template = "19%s" if int(date_parts[2]) > 20 else "20%s"
        birth_date = "%s-%s-%s" % (
            year_template % date_parts[2],
            date_parts[0].zfill(2),
            date_parts[1].zfill(2)
        )
        out_dict['birth_date'] = birth_date

def name_handler(key, value, out_dict):

    if value:
        out_dict['preferred_name'] = value

mapper = {
    'address': addr_handler,
    'city_state_zip': csz_handler,
    'membership_status': status_handler,
    'gender': gender_handler,
    'birthday': birthday_handler, 
    'name': name_handler
}

GENDER_MAP = {'F': 'Female', 'M': 'Male'}
RELATIONSHIP_MAP = {'default': 'Other','Married Female': 'Wife', 'Married Male': 'Husband'}
def relationship_handler(person):
    if 'gender' not in person:
        print person
        return

    relationship = '%s %s' % (
        person['marital_status'], 
        GENDER_MAP[person['gender']]
    ) if person['gender'] else person['marital_status']

    if relationship in RELATIONSHIP_MAP:
        person['relationship'] = RELATIONSHIP_MAP[relationship]
    else:
        person['relationship'] = RELATIONSHIP_MAP['default']
    del person['marital_status']

def greeting_handler(person):
    if 'and' not in person['formal_greeting'] and '&' not in person['formal_greeting']:
        person['mail_to'] = person['formal_greeting']
    else:
        person['mail_to'] = "%s %s" % (person['first_name'], person['last_name'])
    del person['formal_greeting']
    del person['informal_greeting']

def household_from_person(icon_person):
    hh_dict = {
        'address_1': icon_person['address_1'],
        'city': icon_person['city'],
        'state': icon_person['state'],
        'zip': icon_person['zip'],
        'first_name': icon_person['informal_greeting'],
        'last_name': icon_person['last_name'],
        'phone': icon_person['phone'],
        'mail_to': icon_person['formal_greeting'],
        'status': icon_person['status']
    }

    if 'address_2' in icon_person:
        hh_dict['address_2'] = icon_person['address_2']
    
    return hh_dict
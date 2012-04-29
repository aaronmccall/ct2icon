""" Data key and value transforms for mapping ChurchTrac data to IconCMO """
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

mapper = {
    'address': addr_handler,
    'city_state_zip': csz_handler,
    'membership_status': status_handler
}
import yaml, csv
import re
import unidecode

import transforms



empty_csz = {'city': '', 'state': '', 'zip': ''}

def slugify(str):
    str = unidecode.unidecode(str).lower()
    return re.sub(r'\W+', '_', str)

def household_from_person(person_dict):
    hh_dict = {
        'address_1': person_dict['address_1'],
        'city': person_dict['city'],
        'state': person_dict['state'],
        'zip': person_dict['zip'],
        'first_name': person_dict['informal_greeting'],
        'last_name': person_dict['last_name'],
        'phone': person_dict['phone'],
        'mail_to': person_dict['formal_greeting'],
        'status': person_dict['status']
    }

    if 'address_2' in person_dict:
        hh_dict['address_2'] = person_dict['address_2']
    
    return hh_dict

def run():
    person_file = open('/Users/Aaron/Dropbox/HVWC/church_trac.people.csv', 'rU')
    person_dicts = list(csv.DictReader(person_file, dialect='excel'))

    people = []
    households = {}
    not_imported = []
    for person in person_dicts:
        try:
            person_dict = {'phone': ''}
            phones = []
            for key in person:
                if 'Age' in key: continue
                new_key = slugify(key)
                if new_key in transforms.mapper:
                    transforms.mapper[new_key](new_key, person[key], person_dict)
                elif 'phone' in new_key:
                    transforms.phone_mapper(new_key, person[key], person, person_dict, phones)
                else:
                    person_dict[new_key] = person[key]

            # generate a key for the households dict
            hh_key = slugify("%s %s %s" % (person_dict['last_name'], person_dict['address_1'], 
                                           person_dict['zip']))
            person_dict['household'] = hh_key
            # If the current hh_key isn't in the households dict, add it
            if hh_key not in households:
                households[hh_key] = household_from_person(person_dict)
            if phones:
                person_dict['phones'] = phones
            # Add this person
            people.append(person_dict)
        except transforms.InvalidPerson:
            not_imported.append(person)

    people.insert(0, households)

    yaml_persons = yaml.dump_all(people, default_flow_style=False)
    person_file = open('church_trac.people.yaml', 'w')
    person_file.write(yaml_persons)
    person_file.close

    yaml_not_importeds = yaml.dump_all(not_imported, default_flow_style=False)
    not_imported_file = open('church_trac.people.not_imported.yaml', 'w')
    not_imported_file.write(yaml_not_importeds)
    not_imported_file.close

if __name__ == '__main__':
    run()
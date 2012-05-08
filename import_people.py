import argparse
import yaml
import csv
import os.path
import functools

import helpers
import transforms
import conf
  

def import_churchtrac_people(in_file):
    directory = os.path.dirname(in_file)
    ct_person_file = open(in_file, 'rU')
    ct_people = list(csv.DictReader(ct_person_file, dialect='excel'))
    print "Attempting to import %d people from ChurchTrac" % len(ct_people)
    ct_person_file.close()

    people = []
    households = {}
    not_imported = []
    for ct_person in ct_people:
        try:
            icon_person = {'phone': ''}
            phones = []
            for key in ct_person:
                if 'Age' in key: continue
                new_key = helpers.slugify(key)
                if new_key in transforms.people.mapper:
                    transforms.people.mapper[new_key](new_key, ct_person[key], icon_person)
                elif 'phone' in new_key:
                    transforms.people.phone_mapper(new_key, ct_person[key], ct_person, icon_person, phones)
                else:
                    icon_person[new_key] = ct_person[key]

            # generate a key for the households dict
            hh_key = helpers.slugify("%s %s %s" % (icon_person['last_name'], icon_person['address_1'], 
                                           icon_person['zip']))
            icon_person['household_id'] = hh_key
            # If the current hh_key isn't in the households dict, add it
            if hh_key not in households:
                households[hh_key] = transforms.people.household_from_person(icon_person)
            if phones:
                icon_person['phones'] = phones

            # Run transforms that need to be run after icon_person dict is complete
            transforms.people.relationship_handler(icon_person)
            transforms.people.greeting_handler(icon_person)

            # Add this icon_person
            people.append(icon_person)
        except transforms.people.InvalidPerson:
            not_imported.append(ct_person)

    print "Converted %d households" % len(households)
    print "Converted %d people" % len(people)

    yaml_households = yaml.dump(households, default_flow_style=False)
    icon_household_file = open(os.path.join(directory, 'icon.households.yaml'), 'w')
    icon_household_file.write(yaml_households)
    icon_household_file.close()

    yaml_persons = yaml.dump_all(people, default_flow_style=False)
    icon_person_file = open(os.path.join(directory, 'icon.people.yaml'), 'w')
    icon_person_file.write(yaml_persons)
    icon_person_file.close()
    
    print "%d people were not converted due to invalid format" % len(not_imported)
    yaml_not_importeds = yaml.dump_all(not_imported, default_flow_style=False)
    not_imported_file = open(os.path.join(directory, 'church_trac.people.not_imported.yaml'), 'w')
    not_imported_file.write(yaml_not_importeds)
    not_imported_file.close()

    import_icon_people(in_file)

def import_icon_people(in_file):

    auth_data = helpers.get_auth_data()

    directory = os.path.dirname(in_file)

    households_file = open(os.path.join(directory, 'icon.households.yaml'), 'r')
    people_file = open(os.path.join(directory, 'icon.people.yaml'), 'r')

    households = yaml.load(households_file)
    people = yaml.load_all(people_file)

    household_creator = functools.partial(helpers.request_data_builder,
                                          helpers.get_auth_data(),
                                          'membership', 'households', 'create')

    member_creator = functools.partial(helpers.request_data_builder,
                                          helpers.get_auth_data(),
                                          'membership', 'members', 'create')

    i = 0
    for person in people:
        if person['household_id'] in households:
            household = households[person['household_id']]
            if not 'id' in household:
                if household['status'] in conf.DEFAULT_STATUSES:
                    household['status'] = conf.DEFAULT_STATUSES[household['status']]
                hh_data = helpers.post_json(helpers.get_api_url(), household_creator(household))
                print hh_data       
        break

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE', type=str, nargs=1, help='The file to import.')
    del_args = ['-d', '--delete']
    parser.add_argument(*del_args, action='store_true', help='Delete existing temp files.')
    cont_args = ['-c', '--continue']
    parser.add_argument(*cont_args, action='store_true', help='Continue using existing temp files.')
    args = parser.parse_args()

    if args.file and 'csv' in os.path.basename(args.file[0]) and os.path.exists(args.file[0]):
        in_file = args.file[0]
        if os.path.exists(os.path.join(os.path.dirname(in_file), 'icon.people.yaml')) \
           and not args.delete and not getattr(args, 'continue'):
            print parser.print_help()
            print 'Temp files exist use %s to continue or %s to start over.' % (
                ('%s (%s)' % tuple(cont_args)), ('%s (%s)' % tuple(del_args))
            )
        elif getattr(args, 'continue'):
            import_icon_people(in_file)
        else:
            import_churchtrac_people(in_file)
    else:
        parser.print_help()
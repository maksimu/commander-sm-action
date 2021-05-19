import logging
import os
from os import environ
from actions_toolkit import core

from keepercommandersm import Commander
from keepercommandersm.storage import FileKeyValueStorage

for k, v in os.environ.items():
    print(f'{k}={v}')

# os.environ['INPUT_NAME'] = 'Actions Toolkit'
# who_to_greet = core.get_input('who-to-greet')


def find_record(all_secrets, search_term):

    found_rec = None
    for r in all_secrets.get('records'):
        if r.uid == search_term or r.title == search_term:
            found_rec = r
    
    return found_rec

def value_retrieve_and_set(record, secret_value_location, destination_str):

    if secret_value_location == 'password':
        
        destination_arr = destination_str.split(':')

        env_var_name = None

        if len(destination_arr) == 1:
            env_var_name = destination_arr[0].strip()
        elif len(destination_arr) == 2:
            dest = destination_arr[0].strip()
            
            if dest == 'env':
                env_var_name = destination_arr[1].strip()

         
            
        os.environ[env_var_name] = record.password


    elif secret_value_location.startswith('file:'):
        file_name = secret_value_location.split(":")
        
        file_found = None
        for file in record.files:
            if file.name == file_name:
                file_found = file
        
        
        is_file_destination = destination_str.startswith('file:')

        if is_file_destination:
            destination_path = destination_str.lstrip('file:')    # /path/to/file.json

            file.save_file(destination_path, True)
        else:
            core.error("Only file destination is currently supported. Ex. file:/path/to/file.json")

    


core.info('TEST INFO: Run successfully.')

keeper_server = environ.get('KEEPER_SERVER')
SECRET_CONFIG = environ.get('SECRET_CONFIG')
SECRETS = environ.get('SECRETS')



# KEEPER_SECRET_KEY = core.get_input('keeper-secret-key')
core.info('SECRET_CONFIG=%s' % SECRET_CONFIG)
core.info('SECRETS=%s' % SECRETS)


# 1. Authenticate Commander
if keeper_server:
    core.info('Setting Keeper server=%s' % keeper_server)
    Commander.server = keeper_server

config_file_path = "gha-config.json"
config_file = open(config_file_path, "wt")

n = config_file.write(SECRET_CONFIG)
config_file.close()


Commander.config = FileKeyValueStorage(config_file_path)
all_secrets = Commander.fetch()



# SECRETS = """
#   uid123 password | PASSWORD
#   uid321 file/config.json | file://path/to/file.json
# """

secrets_entries = SECRETS.splitlines()

for se in secrets_entries:
    
    # uid123 password | PASSWORD
    se_parts = se.split('|')

    # 1. Splitting and getting record
    # record
    record_details_str    = se_parts[0].strip()            # uid123 password 
    record_details_arr    = record_details_str.split()     # ['uid123', 'password'] OR ['uid321', 'file:config.json']
    record_identifier     = record_details_arr[0]          # 'uid123'
    secret_value_location = record_details_arr[1]          # Field to retrieve. ex. 'password'
    record = find_record(all_secrets, record_identifier)
    # destination

    # 2. Storring
    destination_str = se_parts[1].strip()               # 'PASSWORD' OR 'file:/path/to/file.json'
    
    value_retrieve_and_set(record, secret_value_location, destination_str)


    



# core.set_failed('TEST ERROR: SSL certificates installation failed.')
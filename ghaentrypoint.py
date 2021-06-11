import json
import os
from enum import Enum
from os import environ
from actions_toolkit import core

from keepercommandersm import Commander
from keepercommandersm.storage import InMemoryKeyValueStorage


class DestinationKey(Enum):

    ENV = 'env'
    OUT = 'out'
    FILE = 'file'


class RecordActionEntry:

    def __init__(self):
        self.uid = None
        self.field = None
        self.destination_type = DestinationKey.ENV
        self.destination_val = None

    @staticmethod
    def from_query_entries(query_entries):
        secrets_entries = query_entries.splitlines()

        raes = []
        for se in secrets_entries:
            raes.append(RecordActionEntry.from_entry(se))

        return raes

    @staticmethod
    def from_entry(record_action_entry_str):

        se_parts = record_action_entry_str.split('|') # [uid123 password], [PASSWORD]

        record_details_str = se_parts[0].strip()            # uid123 password
        record_details_arr = record_details_str.split()     # ['uid123', 'password'] OR ['uid321', 'file:config.json']
        record_uid = record_details_arr[0]          # 'uid123'
        secret_value_location = record_details_arr[1]          # Field to retrieve. ex. 'password'

        destination_str = se_parts[1].strip()

        destination_arr = destination_str.split(':')

        if len(destination_arr) == 1:
            destination_key = DestinationKey.ENV
            destination_val = destination_arr[0]
        elif len(destination_arr) == 2:
            destination_key = DestinationKey(destination_arr[0])
            destination_val = destination_arr[1]
        else:
            raise Exception("Destination string was not properly formatted. Err #DE1")

        rae = RecordActionEntry()
        rae.uid = record_uid.strip()
        rae.field = secret_value_location.strip()
        rae.destination_type = destination_key
        rae.destination_val = destination_val.strip()

        return rae


def find_record(secrets, search_term):

    found_rec = None
    for s in secrets:
        if s.uid == search_term or s.title == search_term:
            found_rec = s
    
    return found_rec


def __save_to_file(record, rae):
    file_name = rae.destination_val

    core.info("Processing file %s" % file_name)
    core.debug("Number of files in secret: %s" % len(record.files))
    file_found = None
    for f in record.files:

        if f.name == file_name or f.title == file_name:
            core.info("Found file '%s'" % file_name)
            if file_found:
                core.warning(
                    "More than two files named %s in record uid=%s. Make sure to have unique names for files." % (
                    file_name, record.uid))
                # TODO Is there a way to get files by their UID? or some other unique identifier?

            file_found = f

    if not file_found:
        core.warning("No files found named %s" % file_found)
        # core.end_group()
        return

    core.info("Located file %s" % file_name)

    is_file_destination = rae.destination_type == DestinationKey.FILE

    if is_file_destination:
        core.info("File destination: %s" % rae.destination_val)

        file_found.save_file(rae.destination_val, True)
        core.debug("File saved to %s" % rae.destination_val)
    else:
        core.error("Only file destination is currently supported. Ex. file:/path/to/file.json")


def run_action():

    core.info('-= Keeper Commander GitHub Action =-')

    keeper_server = environ.get('KEEPER_SERVER')
    secret_config = environ.get('SECRET_CONFIG')
    secret_query = environ.get('SECRETS')
    verify_ssl_certs = environ.get('VERIFY_SSL_CERTS')

    if verify_ssl_certs:
        verify_ssl_certs = verify_ssl_certs.lower() in ['true', '1', 't', 'y', 'yes']
    else:
        verify_ssl_certs = True

    if not secret_config:
        core.set_failed("Commander configuration is empty")

    core.debug('Secret query:%s' % secret_query)

    # 1. Authenticate Commander
    if keeper_server:
        core.info('Keeper server: %s' % keeper_server)
        Commander.server = keeper_server

    Commander.verify_ssl_certs = verify_ssl_certs

    Commander.config = InMemoryKeyValueStorage(secret_config)

    record_actions = RecordActionEntry.from_query_entries(secret_query)

    # Get only UIDs of the records from the query list
    uids = [r.uid for r in record_actions]

    # Retrieving only secrets that were asked in the action
    retrieved_secrets = Commander.get_secrets(uids)

    core.debug("Begin retrieving secrets from Keeper...")
    core.info("Retrieved %s secrets." % len(retrieved_secrets))

    core.debug("Secrets to retrieve: %s" % len(record_actions))

    count = 0
    outputs_map = {}

    for record_action in record_actions:

        count += 1

        core.info("Retrieving secret %s: uid=%s" % (str(count), record_action.uid))

        record = find_record(retrieved_secrets, record_action.uid)

        # core.set_secret(record.password)

        if not record:
            core.warning("Record uid=%s not found. Make sure you have this record added to the application you are using." % record_action.uid)
        else:
            core.info("Secret uid=%s, dest=%s" % (record.uid, record_action.destination_type))

            if record_action.destination_type != DestinationKey.FILE and record_action.field != 'password':
                raise Exception("Currently supporting only password fields or files")

            if record_action.destination_type == DestinationKey.ENV:
                if record.password:
                    os.environ[record_action.destination_val] = record.password
                    import subprocess
                    subprocess.call(['setx', 'Hello', 'World!'], shell=True)
                    proc = subprocess.Popen("ls", stdout=subprocess.PIPE, env={'MyVar': 'MyVal'})


                else:
                    core.warning("Password field is empty")

            elif record_action.destination_type == DestinationKey.OUT:
                outputs_map[record_action.destination_val] = record.password
            elif record_action.destination_type == DestinationKey.FILE:
                __save_to_file(record, record_action)
            else:
                raise Exception("Unknown destination type specified: %s" % record_action.destination_type)

    if outputs_map:
        outputs_json = json.dumps(outputs_map)
        core.debug('out-pwds = %s' % outputs_json)
        core.set_output('out-pwds', outputs_json)

    os.environ['MyTest'] = 'This Is Max'
    core.info("Finish retrieving secrets from Keeper Security")


if __name__ == '__main__':
    run_action()

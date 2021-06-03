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
        self.destination = DestinationKey.ENV
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
        rae.destination = destination_key
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
        core.end_group()
        return

    core.info("Located file %s" % file_name)

    is_file_destination = rae.destination == DestinationKey.FILE

    if is_file_destination:
        core.info("File destination: %s" % rae.destination_val)

        file_found.save_file(rae.destination_val, True)
        core.debug("File saved to %s" % rae.destination_val)
    else:
        core.error("Only file destination is currently supported. Ex. file:/path/to/file.json")


def value_retrieve_and_set(record, rae):

    core.start_group("Secret uid=%s" % record.uid)

    if rae.destination != DestinationKey.FILE and rae.field != 'password':
        raise Exception("Currently supporting only password fields or files")

    if rae.destination == DestinationKey.ENV:
        os.environ[rae.destination_val] = record.password
    elif rae.destination == DestinationKey.OUT:
        core.set_output(rae.destination_val, record.password)
    elif rae.destination == DestinationKey.FILE:
        __save_to_file(record, rae)
    else:
        raise Exception("Unknown destination type specified: %s" % rae.destination)

    core.end_group()


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

    core.debug('Secret query=%s' % secret_query)

    # 1. Authenticate Commander
    if keeper_server:
        core.info('Setting Keeper server: %s' % keeper_server)
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

    # secrets_entries = secret_query.splitlines()

    core.debug("Secrets to retrieve: %s" % len(record_actions))

    count = 0
    for rae in record_actions:

        count += 1

        core.start_group("Retrieving secret %s: uid=%s" % (str(count), rae.uid))

        record = find_record(retrieved_secrets, rae.uid)

        # 2. Storing

        value_retrieve_and_set(record, rae)

        core.end_group()

    core.info("Finish retrieving secrets from Keeper Security")


if __name__ == '__main__':
    run_action()
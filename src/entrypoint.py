import os
from os import environ
from actions_toolkit import core

from keepercommandersm import Commander
from keepercommandersm.storage import FileKeyValueStorage


def find_record(secrets, search_term):

    found_rec = None
    for s in secrets.get('records'):
        if s.uid == search_term or s.title == search_term:
            found_rec = s
    
    return found_rec


def value_retrieve_and_set(record, secret_value_location, destination_str):

    core.start_group("Secret uid=%s" % record.uid)
    if secret_value_location == 'password':
        core.info("Processing: Password field")
        destination_arr = destination_str.split(':')

        if len(destination_arr) == 1:
            env_var_name = destination_arr[0].strip()
            os.environ[env_var_name] = record.password

        elif len(destination_arr) == 2:
            dest = destination_arr[0].strip()
            
            if dest == 'env':
                env_var_name = destination_arr[1].strip()
                os.environ[env_var_name] = record.password

            elif dest == 'out':
                out_name = destination_arr[1].strip()
                core.set_output(out_name, record.password)

    elif secret_value_location.startswith('file:'):
        
        file_name = secret_value_location.split(":")[1]
        
        core.info("Processing file %s" % file_name)
        core.debug("Number of files in secret: %s" % len(record.files))
        file_found = None
        for f in record.files:

            if f.name == file_name or f.title == file_name:
                core.info("Found file '%s'" % file_name)
                if file_found:
                    core.warning("More than two files named %s in record uid=%s. Make sure to have unique names for files." % (file_name, record.uid))
                    # TODO Is there a way to get files by their UID? or some other unique identifier?

                file_found = f

        if not file_found:
            core.warning("No files found named %s" % file_found)
            core.end_group()
            return

        core.info("Located file %s" % file_name)
        
        is_file_destination = destination_str.startswith('file:')

        if is_file_destination:
            destination_path = destination_str.lstrip('file:').strip()    # /path/to/file.json
            core.info("File destination: %s" % destination_path)

            file_found.save_file(destination_path, True)
            core.debug("File saved to %s" % destination_path)
        else:
            core.error("Only file destination is currently supported. Ex. file:/path/to/file.json")
    
    core.end_group()


def run_action():

    core.info('Keeper Commander')

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

    config_file_path = "gha-config.json"
    config_file = open(config_file_path, "wt")

    config_file.write(secret_config)
    config_file.close()

    Commander.config = FileKeyValueStorage(config_file_path)
    core.debug("Begin retrieving secrets from Keeper...")
    all_secrets = Commander.fetch()
    core.info("Retrieved %s secrets." % len(all_secrets))

    secrets_entries = secret_query.splitlines()

    core.debug("Secrets to retrieve: %s" % len(secrets_entries))

    count = 0
    for se in secrets_entries:

        count = count + 1

        core.start_group("Retrieving secret %s" % str(count))

        # uid123 password | PASSWORD
        se_parts = se.split('|')

        # 1. Splitting and getting record
        # record
        record_details_str = se_parts[0].strip()            # uid123 password
        record_details_arr = record_details_str.split()     # ['uid123', 'password'] OR ['uid321', 'file:config.json']
        record_identifier = record_details_arr[0]          # 'uid123'
        secret_value_location = record_details_arr[1]          # Field to retrieve. ex. 'password'
        record = find_record(all_secrets, record_identifier)

        # 2. Storing
        destination_str = se_parts[1].strip()               # 'PASSWORD' OR 'file:/path/to/file.json'

        value_retrieve_and_set(record, secret_value_location, destination_str)

        core.end_group()

    core.info("Finish retrieving secrets from Keeper Security")

    # core.set_failed('TEST ERROR: SSL certificates installation failed.')


if __name__ == '__main__':
    run_action()

import os
from os import environ
from actions_toolkit import core

from keepercommandersm import Commander
from keepercommandersm.storage import FileKeyValueStorage

for k, v in os.environ.items():
    print(f'{k}={v}')

# os.environ['INPUT_NAME'] = 'Actions Toolkit'
# who_to_greet = core.get_input('who-to-greet')


# core.error('TEST ERROR: Something went wrong.')


core.info('TEST INFO: Run successfully.')

SECRET_CONFIG = environ.get('SECRET_CONFIG') 
SECRETS = environ.get('SECRETS')



# KEEPER_SECRET_KEY = core.get_input('keeper-secret-key')
core.info('SECRET_CONFIG=%s' % SECRET_CONFIG)
core.info('SECRETS=%s' % SECRETS)



# core.set_failed('TEST ERROR: SSL certificates installation failed.')
import os
from os import environ
from actions_toolkit import core

from keepercommandersm import Commander
from keepercommandersm.storage import FileKeyValueStorage

for k, v in os.environ.items():
    print(f'{k}={v}')

# os.environ['INPUT_NAME'] = 'Actions Toolkit'
# core.get_input('name')
# who_to_greet = core.get_input('who-to-greet')

# core.info('who_to_greet=%s' % who_to_greet)

core.error('TEST ERROR: Something went wrong.')


core.info('TEST INFO: Run successfully.')

KEEPER_SECRET_KEY = environ.get('KEEPER_SECRET_KEY') 
core.info('KEEPER_SECRET_KEY=%s' % KEEPER_SECRET_KEY)



# core.set_failed('TEST ERROR: SSL certificates installation failed.')
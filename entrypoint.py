import os
from actions_toolkit import core

for k, v in os.environ.items():
    print(f'{k}={v}')

# os.environ['INPUT_NAME'] = 'Actions Toolkit'
# core.get_input('name')
# who_to_greet = core.get_input('who-to-greet')

# core.info('who_to_greet=%s' % who_to_greet)

core.error('TEST ERROR: Something went wrong.')


core.info('TEST INFO: Run successfully.')


core.set_failed('TEST ERROR: SSL certificates installation failed.')
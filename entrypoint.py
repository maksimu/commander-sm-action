import os
from actions_toolkit import core

os.environ['INPUT_NAME'] = 'Actions Toolkit'
core.get_input('name')

core.error('TEST ERROR: Something went wrong.')


core.info('TEST INFO: Run successfully.')


core.set_failed('TEST ERROR: SSL certificates installation failed.')
#  _  __
# | |/ /___ ___ _ __  ___ _ _ ®
# | ' </ -_) -_) '_ \/ -_) '_|
# |_|\_\___\___| .__/\___|_|
#              |_|
#
# Keeper Commander
# Copyright 2021 Keeper Security Inc.
# Contact: ops@keepersecurity.com
#
import os

from dotenv import load_dotenv

import ghaentrypoint

dotenv_path = os.path.join(os.path.dirname(__file__), 'test.env')
load_dotenv(dotenv_path)


ghaentrypoint.run_action()

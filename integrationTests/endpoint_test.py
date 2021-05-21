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

from src import entrypoint

dotenv_path = os.path.join(os.path.dirname(__file__), 'test.env')
load_dotenv(dotenv_path)


entrypoint.run_action()

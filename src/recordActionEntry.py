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
from enum import Enum


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

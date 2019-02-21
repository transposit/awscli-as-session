#
# Copyright 2018 Transposit Corporation. All Rights Reserved.
# Copyright (c) 2012-2013 Mitch Garnaat http://garnaat.org/
# Copyright 2012-2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.


import getpass
import json
import logging
import os
import sys
import datetime

from copy import deepcopy
from hashlib import sha1
from dateutil.parser import parse
from dateutil.tz import tzlocal
from botocore.compat import total_seconds

from awscli.customizations.commands import BasicCommand

logger = logging.getLogger(__name__)


class MFACredentials(BasicCommand):
    NAME = 'mfa-credentials'
    SYNOPSIS = 'aws mfa-credentials'
    EXAMPLES = ''

    DESCRIPTION = 'Generate a session token with MFA and print the results.'

    def _run_main(self, parsed_args, parsed_globals):

        cred_provider = self._session.get_component('credential_provider')
        assume_role = cred_provider.get_provider('assume-role')
        cache = assume_role.cache

        cache_key = self._create_cache_key()

        response = self._load_from_cache(cache, cache_key)
        if response is None:
            response = self._get_credentials()
            self._write_to_cache(cache, cache_key, response)
        else:
            logger.debug("Credentials for role retrieved from cache.")

        credentials = {
            'Version': 1,
            'AccessKeyId': response['Credentials']['AccessKeyId'],
            'SecretAccessKey': response['Credentials']['SecretAccessKey'],
            'SessionToken': response['Credentials']['SessionToken'],
            'Expiration': response['Credentials']['Expiration']
        }

        print(json.dumps(credentials))

        return 0

    def _get_credentials(self):
        iam = self._session.create_client('iam')
        user = iam.get_user()
        mfas = iam.list_mfa_devices(UserName=user['User']['UserName'])
        serial = mfas['MFADevices'][0]['SerialNumber']

        prompt = 'Enter MFA code for %s: ' % serial
        token_code = getpass.getpass(prompt, os.fdopen(0, 'w'))

        token = self._session.create_client('sts').get_session_token(
            DurationSeconds=60*60, SerialNumber=serial, TokenCode=token_code)

        return token

    # Portions below copied and adapted from botocore/credentials.py

    def _create_cache_key(self):
        """Create a predictable cache key for the current configuration.
        The cache key is intended to be compatible with file names.
        """
        credentials = self._session.get_credentials()
        args = {}
        args['AccessKeyId'] = credentials.access_key
        args['SecretAccessKey'] = credentials.secret_key
        if credentials.token:
            args['SessionToken'] = credentials.token

        args = json.dumps(args, sort_keys=True)
        argument_hash = sha1(args.encode('utf-8')).hexdigest()
        return self._make_file_safe(argument_hash)

    def _make_file_safe(self, filename):
        # Replace :, path sep, and / to make it the string filename safe.
        filename = filename.replace(':', '_').replace(os.path.sep, '_')
        return filename.replace('/', '_')

    def _load_from_cache(self, cache, cache_key):
        if cache_key in cache:
            creds = deepcopy(cache[cache_key])
            if not self._is_expired(creds):
                return creds
            else:
                logger.debug(
                    "Credentials were found in cache, but they are expired."
                )
        return None

    def _write_to_cache(self, cache, cache_key, response):
        cache[cache_key] = deepcopy(response)

    def _is_expired(self, credentials):
        """Check if credentials are expired."""
        end_time = _parse_if_needed(credentials['Credentials']['Expiration'])
        seconds = total_seconds(end_time - _local_now())
        return seconds < 60*5

    def __init__(self, session):
        super(MFACredentials, self).__init__(session)


def _local_now():
    return datetime.datetime.now(tzlocal())


def _parse_if_needed(value):
    if isinstance(value, datetime.datetime):
        return value
    return parse(value)

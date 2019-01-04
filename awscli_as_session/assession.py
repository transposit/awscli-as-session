#
# Copyright 2018 Transposit Corporation. All Rights Reserved.
#

import os

from awscli.customizations.commands import BasicCommand
from subprocess import Popen


class AsSession(BasicCommand):
    NAME = 'as-session'
    SYNOPSIS = 'aws as-session command [args ...]'
    EXAMPLES = 'aws as-session terraform plan'

    DESCRIPTION = 'Invoke a command with session environment variables set.'

    #
    # Override __call__ rather than implementing _run_main because we
    # expressly don't want arguments parsed.
    #
    def __call__(self, args, parsed_globals):
        if len(args) == 0:
            raise ValueError('usage: %s' % self.SYNOPSIS)
        if len(args) == 1 and args[0] == 'help':
            self._display_help([], parsed_globals)

        credentials = self._session.get_credentials()
        env = os.environ
        env.pop('AWS_PROFILE', None)
        env['AWS_ACCESS_KEY_ID'] = credentials.access_key
        env['AWS_SECRET_ACCESS_KEY'] = credentials.secret_key
        if credentials.token:
            env['AWS_SESSION_TOKEN'] = credentials.token

        p = Popen(args, env=env)
        p.wait()
        return 0

    def __init__(self, session):
        super(AsSession, self).__init__(session)

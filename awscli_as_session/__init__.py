from awscli.customizations.commands import BasicCommand
from subprocess import Popen
import os


def awscli_initialize(cli):
    cli.register('building-command-table.main', inject_commands)


def inject_commands(command_table, session, **kwargs):
    command_table['as-session'] = AsSession(session)


class AsSession(BasicCommand):
    NAME = 'ias-session'
    SYNOPSIS = 'aws get-session'
    EXAMPLES = ''

    DESCRIPTION = 'Invoke a command with session environment variables set.'

    def __call__(self, args, parsed_globals):
        credentials = self._session.get_credentials()
        env = os.environ
        env['AWS_ACCESS_KEY_ID'] = credentials.access_key
        env['AWS_SECRET_ACCESS_KEY'] = credentials.secret_key
        if credentials.token:
            env['AWS_SESSION_TOKEN'] = credentials.token

        p = Popen(args, env=env)
        p.wait()
        return 0

    def __init__(self, session):
        super(AsSession, self).__init__(session)

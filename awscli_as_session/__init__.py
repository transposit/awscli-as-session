#
# Copyright 2018 Transposit Corporation. All Rights Reserved.
#

from .assession import AsSession
from .mfacredentials import MFACredentials


def awscli_initialize(cli):
    cli.register('building-command-table.main', inject_commands)


def inject_commands(command_table, session, **kwargs):
    command_table['as-session'] = AsSession(session)
    command_table['mfa-credentials'] = MFACredentials(session)

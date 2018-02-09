awscli-as-session
=============

aws-cli plugin that invokes a specified command with environment variables that hold the relevant credentials.

This was designed with Terraform in mind which doesn't gracefully handle AWS profiles that use roles and MFA devices.
For example:

    [identity-account]
    aws_access_key_id = AKXXXXXXXXXXXXXXXXXX
    aws_secret_access_key = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    [production]
    role_arn = arn:aws:iam::001122334455:role/production-admin
    source_profile = identity-account
    mfa_serial = arn:aws:iam::667788990011:mfa/my-user

Terraform has no mechanism to prompt (or cache) the MFA value. We can use this plugin to fill that gap:

    $ aws configure set plugins.awscli_as_session awscli_as_session
    $ aws --profile production as-session terraform plan

This will prompt for the MFA code the first time and cache it until it expires; naturally it shares that cache with
other, unrelated aws-cli commands for the same profile.

------------
Installation
------------

    $ pip install git+git://github.com/transposit/awscli-as-session.git

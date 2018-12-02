# awscli-as-session

aws-cli plugin that adds two new subcommands:

 * as-session -- invokes a specified command with environment variables that hold the
   relevant credentials.
 * mfa-credentials -- authenticates with MFA and prints out the credentials in
   a form usable by the credential_process directive in .aws/credentials

## as-session

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

## mfa-credentials

The aws cli doesn't allow for profiles that require MFA authentication
*without* assuming a role. (the exmple below does not work)

```
[identity]
aws_access_key_id = xxx
aws_secret_access_key = xxx

[identity-admin]
source_profile=identity
mfa_serial=arn:aws:iam::667788990011:mfa/ahl
```

This command gives us a workaround:

```
[identity-admin]
credential_process = /Users/ahl/src/aws-mfa/aws-mfa.sh identity
```

------------
Installation
------------

    $ pip install git+git://github.com/transposit/awscli-as-session.git

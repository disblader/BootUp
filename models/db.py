
if not request.env.web2py_runtime_gae:
    db = DAL('sqlite://storage.sqlite')

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager
#
# auth = Auth(db)
# service = Service()
# plugins = PluginManager()
#
# ## create all tables needed by auth if not custom tables
# auth.define_tables(username=False, signature=False)
#
# ## configure email
# mail = auth.settings.mailer
# mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
# mail.settings.sender = 'you@gmail.com'
# mail.settings.login = 'username:password'
#
# ## configure auth policy
# auth.settings.registration_requires_verification = False
# auth.settings.registration_requires_approval = False
# auth.settings.reset_password_requires_verification = True
#
# ## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
# ## register with janrain.com, write your domain:api_key in private/janrain.key
# from gluon.contrib.login_methods.janrain_account import use_janrain
# use_janrain(auth, filename='private/janrain.key')

## Address table definition

# Fields
street_address = Field('street_address', 'string', required=True)
city = Field('city', 'string', required=True)
country = Field('country', 'string', required=True)
postcode = Field('postcode', 'string', length=7, required=True)

# Table definition
db.define_table('address',
                street_address, city, country, postcode,
                format = '%(street_address)s %(postcode)s')

## Credit Card table definition

# Fields
number = Field('number', 'bigint', required=True)
# Expiration should store month and year. However, the closest data type for this is 'date'.
# We will use it and ignore the day component
expiration = Field('expiration', 'date', required=True)
# pid stands for personal identification code
pid = Field('pid', 'integer', required=True)
address = Field('address', db.address, required=True)

# Table definition
db.define_table('credit_card',
                number, expiration, pid, address,
                format='%(number)s')

## User table definition

# Fields
username = Field('username', 'string', unique=True, required=True)
real_name = Field('real_name', 'string', required=True)
birthdate = Field('birthdate', 'date', required=True)
address = Field('address', db.address, required=True)
credit_card = Field('credit_card', db.credit_card, required=True)

# Table declaration
db.define_table('user',
                username, real_name, birthdate, address, credit_card,
                format='%(username)s')

## Bootable table definition

# Fields
# All of the properties are required in order to create this object
title = Field('title', 'string', required=True)
description = Field('description', 'string', length=120, required=True)
category = Field('category', 'string', requires=IS_IN_SET(['Art', 'Comics', 'Crafts', 'Fashion', 'Film', 'Games', 'Music', 'Photography', 'Technology']), required=True)
funding_goal = Field('funding_goal', 'decimal(19,2)', required=True)
image = Field('image', 'upload', required=True)
status = Field('status', requires=IS_IN_SET(['Not Available', 'Open For Pledges', 'Funded', 'Not Funded']), required=True)
creation_date = Field('creation_date', 'date', required=True)
user = Field('user', db.user, required=True)
long_description = Field('long_description', 'text', required=True)
# Bootable manager history description
bm_description = Field('bm_description', 'text', required=True)
funded_on = Field('funded_on', 'date', required=False)


# Table declaration
db.define_table('bootable',
                title, description, category, funding_goal, image, status, creation_date, user, long_description, bm_description, funded_on,
                format='%(title)s')

## Pledge table definition
## To reiterate the specification: a 'pledge' is a concrete instance of a user pledging some money towards a specific
## bootable, as opposed to a 'pledge tier', which is an entity defining rewards for a certain amount of money pledged

# Fields
value = Field('value', 'decimal(19,2)', required=True)
bootable = Field('bootable', db.bootable, required=True)
user = Field('user', db.user, required=True)

# Table Definition
db.define_table('pledge',
                value, bootable, user,
                format='%(user)s')

## Pledge Tier table definition
## To reiterate what is said in the specification, a pledge tier is a set of rewards that the user is to be rewarded
## with if it pledges a required amount of money; as opposed to an entity defining what user pledged towards what
## bootable and for what amount

# Fields
pledge_value = Field('pledge_value', 'decimal(19,2)', required=True)
description = Field('description', 'text', required=True)
includes_lower = Field('includes_lower', 'boolean', default=False)
bootable = Field('bootable', db.bootable, required=True)

# Table declaration

db.define_table('pledge_tier',
                pledge_value, description, includes_lower, bootable,
                format='%(pledge_value)s')
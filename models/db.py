
if not request.env.web2py_runtime_gae:
    db = DAL('sqlite://storage.sqlite')

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
# While address should be required, it is significantly easier to handle the sign-up process when it is not
address = Field('address', db.address, required=False)

# Table definition
db.define_table('credit_card',
                number, expiration, pid, address,
                format='%(number)s')

## User table definition

# Fields
username = Field('username', 'string', unique=True, required=True, requires=IS_ALPHANUMERIC('Username must consist of letters and numbers only'))
real_name = Field('real_name', 'string', required=True, requires=IS_ALPHANUMERIC('Your name must consist of letters and numbers only'))
birthdate = Field('birthdate', 'date', required=True)
# The next two fields, while technically should be required, are made not to be to ease the creation of the user object
address = Field('address', db.address, required=False)
credit_card = Field('credit_card', db.credit_card, required=False)

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
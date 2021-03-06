
if not request.env.web2py_runtime_gae:
    db = DAL('sqlite://storage.sqlite')
## Address table definition

# Fields
street_address = Field('street_address', 'string', required=True, requires=IS_NOT_EMPTY())
city = Field('city', 'string', required=True, requires=IS_NOT_EMPTY())
country = Field('country', 'string', required=True, requires=IS_NOT_EMPTY())
postcode = Field('postcode', 'string', length=8, required=True, requires=[IS_NOT_EMPTY(),IS_MATCH('\w{4} \w{3}', error_message="Must consist of 2 blocks of 4 symbols and 3 symbols respectively (e.g. AB12 CD12)")])

# Table definition
db.define_table('address',
                street_address, city, country, postcode,
                format = '%(street_address)s %(postcode)s')

## Credit Card table definition

# Fields
number = Field('number', 'bigint', required=True, requires=[IS_NOT_EMPTY(), IS_MATCH('\d{16}', error_message="Must consist of 16 numbers")])
# Expiration should store month and year. However, the closest data type for this is 'date'.
# We will use it and ignore the day component
expiration = Field('expiration', 'date', required=True, requires=IS_NOT_EMPTY())
# pid stands for personal identification code
pid = Field('pid', 'integer', required=True, requires=[IS_NOT_EMPTY(), IS_MATCH('\d{3}', error_message="Must consist of 3 numbers on the back of your credit card")])
# While address should be required, it is significantly easier to handle the sign-up process when it is not
address = Field('address', db.address, required=False, readable = False, writable = False)

# Table definition
db.define_table('credit_card',
                number, expiration, pid, address,
                format='%(number)s')

## User table definition

# Fields
username = Field('username', 'string', unique=True, required=True, requires=IS_NOT_EMPTY())
real_name = Field('real_name', 'string', required=True, requires=IS_NOT_EMPTY())
birthdate = Field('birthdate', 'date', required=True, requires=IS_NOT_EMPTY())
# The next two fields, while technically should be required, are made not to be to ease the creation of the user object
address = Field('address', db.address, required=False, readable = False, writable = False)
credit_card = Field('credit_card', db.credit_card, required=False, readable = False, writable = False)

# Table declaration
db.define_table('user',
                username, real_name, birthdate, address, credit_card,
                format='%(username)s')

## Bootable table definition

# Fields
# All of the properties are required in order to create this object
title = Field('title', 'string', required=True, label="Bootable Title")
description = Field('description', 'string', length=120, required=True, label="Short Description (up to 120 characters)")
category = Field('category', 'string', requires=IS_IN_SET(['Art', 'Comics', 'Crafts', 'Fashion', 'Film', 'Games', 'Music', 'Photography', 'Technology']), required=True)
funding_goal = Field('funding_goal', 'decimal(19,2)', required=True)
image = Field('image', 'upload', required=True)
status = Field('status', requires=IS_IN_SET(['Not Available', 'Open For Pledges', 'Funded', 'Not Funded']), required=True, readable = False, writable = False)
creation_date = Field('creation_date', 'date', required=True, readable = False, writable = False)
user = Field('user', db.user, required=True, readable = False, writable = False)
long_description = Field('long_description', 'text', required=True)
# Bootable manager history description
bm_description = Field('bm_description', 'text', required=True, label="Description about yourself as a project creator")
# The next field is not in the specification; it exists as a cache. This poses some synchronisation issues that would have
# to be taken care of in a real-world application, however is beyond this assessment.
# This value is to be updated every time a pledge is made.
funded_so_far = Field('funded_so_far', 'decimal(19,2)', readable = False, writable = False, default=0)

# Table declaration
db.define_table('bootable',
                title, description, category, funding_goal, image, status, creation_date, user, long_description, bm_description, funded_so_far,
                format='%(title)s')

## Pledge table definition
## To reiterate the specification: a 'pledge' is a concrete instance of a user pledging some money towards a specific
## bootable, as opposed to a 'pledge tier', which is an entity defining rewards for a certain amount of money pledged

# Fields
value = Field('value', 'decimal(19,2)', label="Your pledge", required=True, requires=IS_NOT_EMPTY())
bootable = Field('bootable', db.bootable, required=True, readable = False, writable = False)
user = Field('user', db.user, required=True, readable = False, writable = False)

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
bootable = Field('bootable', db.bootable, required=True, readable = False, writable = False)

# Table declaration

db.define_table('pledge_tier',
                pledge_value, description, includes_lower, bootable,
                format='%(pledge_value)s')


# The following function generates the string that will represent the collection of descriptions that the given
# concrete pledge will generate
#
# E.g. if the given pledge is a pledge of value 85 on a bootable which has a
# rewards tier at 65 that includes the lower reward, which would be the one at 45, which does not include the lower
# reward, then the string generated will be concatenation of the reward of the 65 tier reward and the 45 tier reward.
# If the concrete pledge will be 50, however, then the returned string would be just the description of the 45 tier,
# as it does not include any other rewards.
def generate_rewards_string(pledge):

    bootable__for_this_pledge = db(db.bootable.id == pledge.bootable.id).select().first()
    pledge_tier = db((db.pledge_tier.bootable == bootable__for_this_pledge) & (db.pledge_tier.pledge_value <= pledge.value)).select(db.pledge_tier.ALL, orderby=~db.pledge_tier.pledge_value).first()

    reward_string = pledge_tier.description

    # This next loop recursively adds the descriptions of the rewards to the reward string for as long as it
    # encounters pledge tiers that include lower value tiers, and as long as a lower value tier exists.

    while (pledge_tier is not None) & (pledge_tier.includes_lower):
        last_value = pledge_tier.pledge_value
        pledge_tier = db((db.pledge_tier.bootable == bootable__for_this_pledge) & (db.pledge_tier.pledge_value < last_value)).select(db.pledge_tier.ALL, orderby=~db.pledge_tier.pledge_value)
        if pledge_tier is not None:
            pledge_tier = pledge_tier.first()
            reward_string += '; ' + pledge_tier.description

    return reward_string
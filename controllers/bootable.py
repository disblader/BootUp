# This controller will control actions related to the bootables (like pledging towards a bootable, viewing them, etc.)
import datetime
from decimal import *


# This is the controller for the action of creating or editing a bootable
#
# INPUT:
# 'bootable' - if you pass a bootable ID into this page as a request variable, then the page becomes an edit page for that
#               bootable. Otherwise it creates a new bootable.
def edit():
    # This action is only available if you're logged in
    check_and_redirect()

    if request.vars.bootable:
        bootable = db(db.bootable.id == request.vars.bootable).select().first()

        form = SQLFORM(db.bootable, bootable, submit_button='Submit the changes', showid=False)

        if form.process().accepted:
            session.flash = 'The Bootable got updated successfully!'
            redirect(URL('user', 'dashboard'))

    else:
        form = SQLFORM(db.bootable,
                   submit_button='Create this Bootable!')

        user = db(db.user.username == session.logged_in_user).select(db.user.ALL).first()

        if form.validate():
            id = db.bootable.insert(title=form.vars.title,
                           description=form.vars.description,
                           category=form.vars.category,
                           funding_goal=Decimal(form.vars.funding_goal),
                           image=form.vars.image,
                           status='Not Available',  # This is a default for all newly created bootables
                           creation_date=datetime.date.today(),
                           user=user,
                           long_description=form.vars.long_description,
                           bm_description=form.vars.bm_description,
                           funded_so_far=0)

            redirect(URL('edit_rewards', vars={'new':True, 'bootable':id}))

    return dict(form=form)


# This controller is for editing the rewards of the bootable page
#
# INPUT:
# 'new' - if an argument 'new' exists, then we display a welcoming sort of a message thing. Go to the view and check it
# 'bootable' - YOU MUST pass a bootable id as an argument 'bootable', so that this page could tell which bootable to load
# 'tier_id' - if passed in, will open an already existing pledge tier with that ID for editing. Otherwise displays
#        a form for creating a new reward tier.
def edit_rewards():

    pledge_tier = None
    bootable = db(db.bootable.id == request.vars.bootable).select().first()
    all_tiers = db(db.pledge_tier.bootable == bootable).select(db.pledge_tier.ALL)

    print(all_tiers)

    if request.vars.tier_id:
        pledge_tier = db(db.pledge_tier.id == request.vars.tier_id).select().first()

        form = SQLFORM(db.pledge_tier,
                        pledge_tier,
                        showid=False,
                        submit_button='Update this rewards tier!')

        if form.process().accepted:
            session.flash = 'Successfully updated the reward tier.'
            # the form doesn't refresh the page by default (causing stale data to appear) soooo.... This ugly workaround
            # Also, it's late so I don't know how to prevent 'new' from getting added easily. So I'm making an if statement. Don't judge me!
            if request.vars.new:
                redirect(URL(vars={'bootable':request.vars.bootable, 'tier_id':request.vars.tier_id}))
            else:
                redirect(URL(vars={'bootable':request.vars.bootable, 'tier_id':request.vars.tier_id, 'new':request.vars.new}))

    else:
        form = SQLFORM(db.pledge_tier, showid=False, submit_button='Create this rewards tier!')
        # We insert manually because we need to fill some hidden data in
        if form.validate():
            db.pledge_tier.insert(
                pledge_value=form.vars.pledge_value,
                description=form.vars.description,
                includes_lower=form.vars.includes_lower,
                bootable=bootable
            )
            response.flash = 'Success! Created a new reward tier'

            # the form doesn't refresh the page by default (causing stale data to appear) soooo.... This ugly workaround
            # Also, it's late so I don't know how to prevent 'new' from getting added easily. So I'm making an if statement. Don't judge me!
            if request.vars.new:
                redirect(URL(vars={'bootable':request.vars.bootable}))
            else:
                redirect(URL(vars={'bootable':request.vars.bootable, 'new':request.vars.new}))



    return dict(form=form, pledge_tier=pledge_tier, all_tiers=all_tiers)


# This is the controller for viewing a bootable.
#
# As security is not a concern, we assume that this controller was reached through legitimate means and hence
# no argument validation is performed
#
# INPUT: the request has to have an attribute named 'id' which is the ID of the bootable which is to be displayed
def view():

    bootable = db(db.bootable.id == request.vars.id).select().first()
    pledge_tiers = db(db.pledge_tier.bootable == bootable).select(db.pledge_tier.ALL, orderby=db.pledge_tier.pledge_value)

    # This is an array of objects that store the display information for the part of the page about the users that
    # pledged towards this bootable
    pledge_display_objects =[]

    pledges = db(db.pledge.bootable == bootable).select()

    current_user = None
    current_user_pledge = None

    if session.logged_in_user:
        current_user = db(db.user.username == session.logged_in_user).select().first()

    for a_pledge in pledges:

        if current_user is not None:
            if a_pledge.user.id == current_user.id:
                current_user_pledge = a_pledge

        # that is a function found in the db.py model
        reward_string = generate_rewards_string(a_pledge)

        user = db(db.user.id == a_pledge.user.id).select(db.user.ALL).first()

        display_object = {
            'value':a_pledge.value,
            'rewards':reward_string,
            'username':user.username
        }

        pledge_display_objects.append(display_object)

    return dict(bootable=bootable,
                pledge_tiers=pledge_tiers,
                pledge_display_objects=pledge_display_objects,
                current_user_pledge=current_user_pledge,
                current_user=current_user)


# Returns the image for the bootable
def show():
    return response.download(request,db)


# This is the controller for the pledge page. What it does is quite straightforward: it displays the pledge tiers
# available for the supplied bootable and lets the user enter the amount of money that the user wants to pledge to the
# project
#
# This same controller also handles input from itself as well
def pledge():
    # This action is only available to logged in users
    check_and_redirect()

    bootable = db(db.bootable.id == request.vars.id).select(db.bootable.ALL).first()
    user = db(db.user.username == session.logged_in_user).select(db.user.ALL).first()

    # The user can end up in here if he wasn't logged in, pressed pledge and got redirected here. If that is the case,
    # we need to check if the user has pledged towards this by any chance.
    # The following lines do that by checking if a pledge with the combination expected exist
    stuff = db((db.pledge.user == user) & (db.pledge.bootable == bootable)).select().first()
    if stuff:
        # this means that there exists a pledge from this user to this bootable. Redirect back with a message
        session.flash = "You have already pledged towards this project"
        redirect(URL('view', vars={'id':request.vars.id}))

    form = SQLFORM(db.pledge,
                   submit_button='Make this pledge!')

    # We're preventing the default form IO in order to get some other stuff going
    if form.validate():
        # inserts the new entry into the table of pledges
        db.pledge.insert(value=form.vars.value, bootable=bootable, user=user)

        # Updates the bootable's funded_so_far value
        db(db.bootable.id == bootable.id).update(funded_so_far=(bootable.funded_so_far + Decimal(form.vars.value)))

        bootable = db(db.bootable.id == bootable.id).select().first()
        # If the bootable's funded_so_far is higher than the funding goal, the bootable becomes funded
        if bootable.funded_so_far >= bootable.funding_goal:
            db(db.bootable.id == bootable.id).update(status = 'Funded')

        session.flash = 'You successfully pledged ' + \
                        str(request.vars.value) + \
                        ' towards \'' \
                        + bootable.title + '\''
        redirect(URL('bootable', 'view', vars={'id':bootable.id}))

    pledge_tiers = db(db.pledge_tier.bootable == bootable).select(db.pledge_tier.ALL, orderby=db.pledge_tier.pledge_value)

    return dict(pledge_tiers=pledge_tiers,
                bootable=bootable,
                form=form)
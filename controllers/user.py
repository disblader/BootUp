# This is a controller for user actions (like logging in, checking their user profile, etc.)


# This is the log-in action. It is a simplified log-in (no password, just username), as no security is to be implemented
# for the purpose of this assessment
def login():

    # # If 'error' exists on the request arguments, then flash it
    # # This is used to display reasons why the user was redirected to the login page, if that is indeed how it got here
    # if request.vars.error:
    #     response.flash = request.vars.error

    form = FORM(INPUT(_name='username', requires=IS_IN_DB(db, db.user.username, error_message='The user cannot be found; please try again')),
                INPUT(_type='submit'))

    if form.process(formname='login_form').accepted:
        session.flash = 'Hello, ' + form.vars.username
        log_user_in(form.vars.username)
        if (request.vars.next_c is not None) & (request.vars.next_f is not None):
            redirect(URL(request.vars.next_c, request.vars.next_f))
        else:
            redirect(URL('default', 'index'))

    return dict(form=form)


# This is the action of editing your own user data.
# Requires the user to be logged in
def edit():
    check_and_redirect()
    return dict()


# Pretty straightforward: logs the user out
def logout():
    session.flash = 'Hope to see you again soon!'
    log_user_out()
    response.flash = session.logged_in_user
    redirect(URL('default', 'index'))


# This controller retrieves and passes on to the view a list of objects that display information about
# the pledges that the user has made to bootables.
def my_pledges():

    check_and_redirect()
    username = session.logged_in_user

    user = db(db.user.username == username).select().first()

    pledges = db(db.pledge.user == user).select(db.pledge.ALL);

    display_objects = []

    for pledge in pledges:
        bootable = db(db.bootable.id == pledge.bootable.id).select().first()

        pledge_tier = db((db.pledge_tier.bootable == bootable) & (db.pledge_tier.pledge_value <= pledge.value)).select(db.pledge_tier.ALL, orderby=~db.pledge_tier.pledge_value).first()

        reward_string = pledge_tier.description

        # This next loop recursively adds the descriptions of the rewards to the reward string for as long as it
        # encounters pledge tiers that include lower value tiers, and as long as a lower value tier exists.

        while (pledge_tier is not None) & (pledge_tier.includes_lower):
            last_value = pledge_tier.pledge_value
            pledge_tier = db((db.pledge_tier.bootable == bootable) & (db.pledge_tier.pledge_value < last_value)).select(db.pledge_tier.ALL, orderby=~db.pledge_tier.pledge_value)
            if pledge_tier is not None:
                pledge_tier = pledge_tier.first()
                reward_string += '; ' + pledge_tier.description

        display_object = {
            'title':bootable.title,
            'value':pledge.value,
            'rewards':reward_string,
            'funded_so_far':bootable.funded_so_far,
            'funding_goal':bootable.funding_goal,
            'status':bootable.status
        }

        display_objects.append(display_object)

    return dict(results=display_objects)


# This control gathers up the information required for the BM dashboard. That is, it collects the information on the
# BM's bootables, and generates a list of available actions to be performed on that bootable. Then it passes this
# information to be displayed in the view
def dashboard():

    # The following three functions generate elements that take a certain action upon the given bootable.
    # Used to ease the generation of the actions for the state machine
    # There's a bit more about that below in this function
    def delete_action(bootable):
        return A('Delete', _class='btn', _href=URL('delete_bootable', vars={'id':bootable.id}))

    def open_for_pledges_action(bootable):
        return A('Open for Pledges', _class='btn', _href=URL('open_for_pledges', vars={'id':bootable.id}))

    def close_action(bootable):
        return A('Close', _class='btn', _href=URL('close_bootable', vars={'id':bootable.id}))

    check_and_redirect()
    username = session.logged_in_user

    user = db(db.user.username == username).select().first()

    bootables = db(db.bootable.user == user).select(db.bootable.ALL);

    display_objects = []

    for bootable in bootables:

        # This next bit before the construction of the display_object executes part of the state machine of the bootable
        # It is only a part of it because the transition 'Open For Pledges' -> 'Funded' is automatic
        # For the diagram of the state machine, check the design document

        if bootable.status == 'Not Available':
            actions = [delete_action(bootable), open_for_pledges_action(bootable)]
        elif bootable.status == 'Open For Pledges':
            actions = [close_action(bootable)]
        elif bootable.status == 'Funded':
            actions = [delete_action(bootable)]
        elif bootable.status == 'Not Funded':
            actions = [delete_action(bootable), open_for_pledges_action(bootable)]

        display_object = {
            'bootable': bootable,
            'actions': actions
        }

        display_objects.append(display_object)

    return dict(results=display_objects)


# This is the operation to delete a bootable
# As the assessment is not evaluated for security, the action assumes that the action is legitimately invoked.
#
# This operation also produces feedback via the web2py 'flash'
#
# INPUT: the request has to have an attribute named 'id' which is the ID of the bootable on which the operation
# will be performed
def delete_bootable():
    bootable = db(db.bootable.id == request.vars.id).select(db.bootable.title).first()
    session.flash = 'Deleted the bootable \'' + bootable.title + '\''
    db(db.bootable.id == request.vars.id).delete()
    redirect(URL('dashboard'))
    return dict()


# This is the operation to open for pledges a bootable
# As the assessment is not evaluated for security, the action assumes that the action is legitimately invoked.
#
# This operation also produces feedback via the web2py 'flash'
#
# INPUT: the request has to have an attribute named 'id' which is the ID of the bootable on which the operation
# will be performed
def open_for_pledges():
    bootable = db(db.bootable.id == request.vars.id).select(db.bootable.title).first()
    session.flash = 'Opened the bootable \'' + bootable.title + '\' for pledges'
    db(db.bootable.id == request.vars.id).update(status='Open For Pledges')
    redirect(URL('dashboard'))
    return dict()


# This is the operation to 'close' a bootable
# As the assessment is not evaluated for security, the action assumes that the action is legitimately invoked.
#
# This operation also produces feedback via the web2py 'flash'

# INPUT: the request has to have an attribute named 'id' which is the ID of the bootable on which the operation
# will be performed
def close_bootable():
    bootable = db(db.bootable.id == request.vars.id).select(db.bootable.title).first()
    session.flash = 'Closed the bootable \'' + bootable.title + '\'. It is no longer available for pledging.'
    db(db.bootable.id == request.vars.id).update(status='Not Funded')
    redirect(URL('dashboard'))
    return dict()
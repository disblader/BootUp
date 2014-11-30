# This is a controller for user actions (like logging in, checking their user profile, etc.)


# This is the log-in action. It is a simplified log-in (no password, just username), as no security is to be implemented
# for the purpose of this assessment
def login():

    # If 'error' exists on the request arguments, then flash it
    # This is used to display reasons why the user was redirected to the login page, if that is indeed how it got here
    if request.vars.error:
        response.flash = request.vars.error

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
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
        log_user_in(form.vars.username)
        redirect(URL(request.vars.next_c, request.vars.next_f))

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

# This controller retrieves and passes on to the view a list of bootables that the user has pledged towards
def my_pledges():

    check_and_redirect()
    username = session.logged_in_user

    pledges = db(db.pledge.user == (db.user.username == username)).select(db.pledge.ALL);

    bootables = []

    for pledge in pledges:
        print(' ')
        bootable = db.bootable(db.bootable.id == pledge.bootable.id)
        print(bootable.title)
        bootables.append(bootable)

    print(bootables)
    return dict(results=bootables)
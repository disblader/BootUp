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

    if form.process().accepted:
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

# A straightforward form, generated based on the user table
def signup():
    user_form = SQLFORM(db.user)


    # if form.process().accepted:
        # id = db.address.insert(**db.address._filter_fields(form.vars))
        # form.vars.client=id
        # id = db.credit_card.insert(**db.credit_card._filter_fields(form.vars))
        # response.flash='Thanks for filling the form'

    # return dict(user_form=user_form, address_form=address_form, credit_card_form=credit_card_form, credit_card_address_form=credit_card_address_form)
    return dict(user_form=user_form)
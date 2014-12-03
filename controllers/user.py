# This is a controller for user actions (like logging in, checking their user profile, etc.)


# This page creates a new user, or updates an existing user based on whether a user is logged in.
# If a user is logged in, then it automatically goes to editing mode.
# Otherwise goes to signup mode.
def signup_or_edit():

    if session.logged_in_user:
        redirect(URL('edit'))
    else:

        # I'm deep-copying the fields from the DB tables because I'm not sure if otherwise side-effects would not be
        # introduced when changing the name of the fields

        # Create form
        form = SQLFORM.factory(db.user, db.address)

        if form.validate():
            address_id = db.address.insert(street_address=form.vars.street_address,
                                           city=form.vars.city,
                                           country=form.vars.country,
                                           postcode=form.vars.postcode)

            address = db(db.address.id == address_id).select().first()

            user_id = db.user.insert(username=form.vars.username,
                                        real_name=form.vars.real_name,
                                        birthdate=form.vars.birthdate,
                                        address=address)

            # Now this might seem dodgy; after all, all data should be set up straight away.
            # However, this is not an issue. Whenever the user tries to log in, if it hasn't finished the last step
            # (i.e. setting up the credit card), the user will be redirected to the page asking them to finish creating
            # their account. So the user will never end up logging in without finishing their account
            session.flash='Successfully created the account. Please provide credit card information to finish creation.'

            redirect(URL('finalise', vars={'user_id':user_id, 'new':True}))

    return dict(form=form)


# The user gets redirected here to edit his/her account details.
def edit():

    print('Potato jam')

    check_and_redirect()

    user = db(db.user.username == session.logged_in_user).select().first()
    form_user = SQLFORM(db.user, user, showid=False)

    if form_user.process().accepted:
        session.flash = 'General user information updated'

    address = db(db.address.id == user.address.id).select().first()
    form_user_address = SQLFORM(db.address, address, showid=False)

    if form_user_address.process().accepted:
        session.flash = 'User address updated'

    credit_card = db(db.credit_card.id == user.credit_card.id).select().first()
    form_credit_card = SQLFORM(db.credit_card, credit_card, showid=False)

    if form_credit_card.process().accepted:
        session.flash = 'User credit card updated'

    credit_card_address = db(db.address.id == credit_card.address.id).select().first()
    form_credit_card_address = SQLFORM(db.address, credit_card_address, showid=False)

    if form_credit_card_address.process().accepted:
        session.flash = 'User billing address updated'

    return dict(form_user=form_user, form_user_address=form_user_address, form_credit_card=form_credit_card, form_credit_card_address=form_credit_card_address)


# This is the page to which users are redirected to finish their account (i.e. provide credit card information).
# When a user tries to log in, if they hadn't finished their account, they will always be redirected to this page
# INPUT:
# user_id - the ID of the user on whom the finalisation is to be performed
# new - if this argument exists, then new user instructions will be displayed
def finalise():

    if request.vars.new:
        form = SQLFORM.factory(db.credit_card, db.address)

        if form.validate():
            address_id = db.address.insert(street_address=form.vars.street_address,
                                           city=form.vars.city,
                                           country=form.vars.country,
                                           postcode=form.vars.postcode)

            address = db(db.address.id == address_id).select().first()

            credit_card_id = db.credit_card.insert(number=form.vars.number,
                                        expiration=form.vars.expiration,
                                        pid=form.vars.pid,
                                        address=address)

            credit_card = db(db.credit_card.id == credit_card_id).select().first()

            db(db.user.id == request.vars.user_id).update(credit_card=credit_card)

            user = db(db.user.id == request.vars.user_id).select().first()

            session.flash = 'Thank you for for creating an account on BootUp'
            log_user_in(user.username)

            redirect(URL('default', 'index'))

    return dict(form=form)


# This is the log-in action. It is a simplified log-in (no password, just username), as no security is to be implemented
# for the purpose of this assessment
def login():

    # # If 'error' exists on the request arguments, then flash it
    # # This is used to display reasons why the user was redirected to the login page, if that is indeed how it got here
    # if request.vars.error:
    #     response.flash = request.vars.error

    form = FORM(INPUT(_name='username', _placeholder="Enter your username here", requires=IS_IN_DB(db, db.user.username, error_message='The user cannot be found; please try again')),
                INPUT(_type='submit'))

    if form.process(formname='login_form').accepted:
        session.flash = 'Hello, ' + form.vars.username
        log_user_in(form.vars.username)
        if (request.vars.next_c is not None) & (request.vars.next_f is not None):
            redirect(URL(request.vars.next_c, request.vars.next_f, vars=request.vars))
        else:
            redirect(URL('default', 'index'))

    return dict(form=form)


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

    pledges = db(db.pledge.user == user).select(db.pledge.ALL)

    display_objects = []

    for pledge in pledges:
        bootable = db(db.bootable.id == pledge.bootable.id).select().first()

        # that is a function found in the db.py model
        reward_string = generate_rewards_string(pledge)

        display_object = {
            'id':bootable.id,
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
            # Aside from the state machine actions, projects in this state can also be edited
            actions = [delete_action(bootable),
                       open_for_pledges_action(bootable),
                       A('Edit Information', _class='btn', _href=URL('bootable', 'edit', vars={'bootable':bootable.id})),  # Edit the bootable
                       A('Edit Rewards', _class='btn', _href=URL('bootable', 'edit_rewards', vars={'bootable':bootable.id}))]  # Edit the rewards
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
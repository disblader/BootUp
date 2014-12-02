# This controller will control actions related to the bootables (like pledging towards a bootable, viewing them, etc.)
import datetime


# This is the controller for the action of creating a bootable
def create():
    # This action is only available if you're logged in
    check_and_redirect()

    #
    # form = FORM(INPUT(),
    #             # Title
    #             # Description
    #             # Category
    #             # Funding Goal
    #             # Image
    #             # Status
    #             # Creation Date
    #             # User
    #             # Long Description
    #             # BM Description
    #             # Funded so far
    # )

    today = datetime.date.today().strftime('%y-%m-%d')

    form = SQLFORM(db.bootable, hidden=dict(creation_date=today))

    return dict(form=form)


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

        if (current_user is not None) & (a_pledge.user.id == current_user.id):
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

    # form = SQLFORM.factory(
    #             Field('value', 'decimal(19,2)', label="Value of your pledge") requires=IS_NOT_EMPTY()),
    #             )

    form = SQLFORM.factory(db.pledge,
                   submit_button='Make this pledge!')

    if form.validate():
        print(form.vars)

    # <input type="hidden" name="id" value="{{=bootable.id}}"/>

    # The following line checks if the invocation was in fact the form submission
    if request.vars.value:

        # inserts the new entry into the table of pledges
        db.pledge.insert(value=request.vars.value, bootable=bootable, user=user)

        # Updates the bootable's funded_so_far value
        db(db.bootable.id == bootable.id).update(funded_so_far = (bootable.funded_so_far + request.vars.value))

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

    return dict(pledge_tiers = pledge_tiers, bootable=bootable, form=form)
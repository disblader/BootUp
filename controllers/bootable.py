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

    print(bootable.image)

    return dict(bootable=bootable, pledge_tiers=pledge_tiers)


# Returns the image for the bootable
def show():
    return response.download(request,db)
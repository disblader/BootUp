# This controller will control actions related to the bootables (like pledging towards a bootable, viewing them, etc.)
import datetime


# This is the controller for the action of creating a bootable
def create():
    # This action is only available if you're logged in
    check_and_redirect()

    form = FORM(INPUT(),
                # Title
                # Description
                # Category
                # Funding Goal
                # Image
                # Status
                # Creation Date
                # User
                # Long Description
                # BM Description
                # Funded so far
    )

    today = datetime.date.today().strftime('%y-%m-%d')

    form = SQLFORM(db.bootable, hidden=dict(creation_date=today))

    return dict(form=form)


#
def view():
    return dict()
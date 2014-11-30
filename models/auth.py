# This model defines some helper functions to make authentication checking more centralised
# The data for this model is actually stored in the session

# This function checks whether the user is logged in and if that is not the case, redirects to login with
# a link back to the desired page.
def check_and_redirect():
    if not session or not session.logged_in_user:
        redirect(URL('user','login', vars={'next_c':request.controller,'next_f':request.function, 'error':'You must log in before you can do that'}))

# Logs the user in (i.e. defines a session variable that is the username. The existence of it counts as the user being
# 'logged in')
def log_user_in(username):
    print('Logging user in: ' + username)
    session.logged_in_user = username

# Logs the user out (i.e. resets the session variable that is the username. The lack of the variable is interpreted as
# the user not being logged in)
def log_user_out():
    if session and session.logged_in_user:
        session.logged_in_user = None
    else:
        print('Log out was called, but no user is logged in')



# This is the controller for the homepage. Homepage requests do not take any input; hence no processing is required.
def index():
    return dict()

def search():
    # The dictionary that will be returned to the view
    results = None

    search_term = request.vars.search_term

    search_category = None

    # The category selection of 'All Categories' should be ignored
    if (request.vars.search_category is not None) & (request.vars.search_category != 'All Categories'):
        search_category = request.vars.search_category


    if (search_term is not None) & (search_category is not None):
        # The following condition summarised would be something like
        # (title like search term OR description like search term) AND category == search category
        results = db(((db.bootable.title.like('%' + search_term + '%')) | (db.bootable.description.like('%' + search_term + '%')))
                     & (db.bootable.category == search_category)).select()
    elif search_term is not None:
        results = db(db.bootable.title.like('%' + search_term + '%') | db.bootable.description.like('%' + search_term + '%')).select()
    elif search_category is not None:
        results = db(db.bootable.category == search_category).select()


    return dict(results=results)



# @cache.action()
# def download():
#     """
#     allows downloading of uploaded files
#     http://..../[app]/default/download/[filename]
#     """
#     return response.download(request, db)
#
#
# def call():
#     """
#     exposes services. for example:
#     http://..../[app]/default/call/jsonrpc
#     decorate with @services.jsonrpc the functions to expose
#     supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
#     """
#     return service()
#
#
# @auth.requires_login()
# def api():
#     """
#     this is example of API with access control
#     WEB2PY provides Hypermedia API (Collection+JSON) Experimental
#     """
#     from gluon.contrib.hypermedia import Collection
#     rules = {
#         '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
#         }
#     return Collection(db).process(request,response,rules)

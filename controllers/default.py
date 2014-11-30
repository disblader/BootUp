
# This is the controller for the homepage. Homepage requests do not take any input; hence no processing is required.
def index():
    closest_to_funding = db(db.bootable.status == 'Open For Pledges').select(orderby=~db.bootable.funded_so_far, limitby=(0,5))

    return dict(closest_to_funding = closest_to_funding)

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
        # (title like search term OR description like search term) AND category == search category AND status is not 'Not Available'
        results = db(((db.bootable.title.like('%' + search_term + '%')) | (db.bootable.description.like('%' + search_term + '%')))
                     & (db.bootable.category == search_category)
                     & (db.bootable.status != 'Not Available')).select()
    elif search_term is not None:
        results = db((db.bootable.title.like('%' + search_term + '%') | db.bootable.description.like('%' + search_term + '%'))
                    & (db.bootable.status != 'Not Available')).select()
    elif search_category is not None:
        results = db(db.bootable.category == search_category
                     & (db.bootable.status != 'Not Available')).select()


    return dict(results=results)

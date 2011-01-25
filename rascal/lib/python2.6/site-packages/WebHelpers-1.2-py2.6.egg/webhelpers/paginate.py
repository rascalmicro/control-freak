"""
paginate: a module to help split up lists or results from ORM queries
=======================================================================

What is pagination?
---------------------

This module helps dividing large lists of items into pages. The user 
is shown one page at a time and can navigate to other pages. Imagine you 
are offering a company phonebook and let the user search the entries. If 
the search result contains 23 entries but you may want to display no 
more than 10 entries at once. The first page contains entries 1-10, the 
second 11-20 and the third 21-23. See the documentation of the "Page" 
class for more information. 

How do I use it?
------------------

One page of items is represented by the *Page* object. A *Page* gets
initalized with two parameters at least:

- the collection of items to pick a range from
- the page number that is required (default is 1 - the first page)

A simple example (ipython session)::

    # Set up the routes context (only if you are not using a Pylons application)
    >>> import routes
    >>> mapper=routes.Mapper()
    >>> mapper.connect(None, '/{controller}')

    # Create a sample collection of 1000 items
    >>> my_collection = range(1000)

    # Create a Page object for the 3rd page (20 items per page is the default)
    >>> my_page = Page(my_collection, page=3)

    # The page object can be printed directly to get its details
    >>> my_page
    Page:
    Collection type:  <type 'list'>
    (Current) page:   3
    First item:       41
    Last item:        60
    First page:       1
    Last page:        50
    Previous page:    2
    Next page:        4
    Items per page:   20
    Number of items:  1000
    Number of pages:  50
    <BLANKLINE>

    # Print a list of items on the current page
    >>> my_page.items
    [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]

    # The *Page* object can be used as an iterator:
    >>> for my_item in my_page: print my_item,
    40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59

    # On a web page you will want to use a "pager" that creates links that
    # the user can click on to load other pages in the set.
    # [The ">>" prompt is to hide untestable examples from doctest.]
    >> my_page.pager()
    1 2 [3] 4 5 .. 50       (this is actually HTML)

    # The pager can be customized:
    >> my_page.pager('$link_previous ~3~ $link_next (Page $page of $page_count)')
    1 2 [3] 4 5 6 .. 50 > (Page 3 of 50)

Please see the documentation on ``Page`` and ``Page.pager()``. There are many
parameters that customize the Page's behavior.

URL generator
-------------

The ``Page.pager()`` method requires a URL generator to create the links to the other
pages. You can supply a callback function to the constructor, or let it
fall back to ``pylons.url.current`` or ``routes.url_for`` (in that order). If
none of these are available, you'll get a ``NotImplementedError``.

Pylons applications can simply let it default to ``pylons.url.current``, which
is available in Pylons 0.9.7 and later.

Older versions of Paginate (up to 1.0b5) used ``routes.url_for`` in all cases.
This caused an unnecessary dependency on Routes, and was untenable when
``url_for`` was deprecated and Pylons 1.x no longer supported it. Nevertheless
it remains for backward compatibility.

To provide your own callback, create a function that takes a *page* argument
and optional *partial* argument, and returns the URL to that page. Pass this
function as the ``Page`` constructor's *url* argument.

Note that the *page* and *partial* arguments may be called something else! You
can rename these by specifying *page_param* and/or *partial_param* in
``Page.pager()``. Just make sure to be consistent between the pager args and
callback args.

Also note that any extra keyword args passed to the ``Page`` constructor or
``Page.pager()`` will be passed to the callback, so it should expect them.

A typical callback will return the current page's URL, converting the keyword
args to query parameters.  This is what ``pylons.url.current`` and
``routes.url_for``, except that these also use keyword args to override path
variables.

The *partial* arg will be unspecified for a normal URL. It will have the value
1 (int) for a partial URL.

Examples::

    # Example 1: explicitly use pylons.url.current
    page = Page(MY_COLLECTION, url=pylons.url.current)

    # Example 2: implicitly use pylons.url.current.
    page = Page(MY_COLLECTION)

    # Example 3: a dumb callback that uses string interpolation.
    def get_page_url(page, partial=None):
        url = "%s?page=%s" % (THE_URL, page)
        if partial:
            url += "&partial=1"
        return url
    page = Page(MY_COLLECTION, url=get_page_url) 

    # Example 4: a smarter callback that uses ``update_params``, which converts
    # keyword args to query parameters.
    from webhelpers.tools import update_params
    def get_page_url(**kw):
        return update_params("/content", **kw)
    page = Page(MY_COLLECTION, url=get_page_url)



Can I use AJAX / AJAH?
------------------------

Yes. See *partial_param* and *onclick* in ``Page.pager()``.

Notes
-------

Page numbers and item numbers start at 1. This concept has been used
because users expect that the first page has number 1 and the first item
on a page also has number 1. So if you want to use the page's items by
their index number please note that you have to substract 1.

This module is the successor to the obsolete ``webhelpers.pagination``
module.  It is **NOT** API compatible.

This version of paginate is based on the code from
http://workaround.org/cgi-bin/hg-paginate that is known at the
"Paginate" module on PyPI.
"""

__version__ = '0.3.7'
__date__ = '2009-04-23'
__author__ = 'Christoph Haas <email@christoph-haas.de>'
__copyright__ = 'Copyright (c) 2007,2008 Christoph Haas <email@christoph-haas.de>'

# License:
# 
# This software can be used under the terms of the MIT license:
# 
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the 
# "Software"), to deal in the Software without restriction, including 
# without limitation the rights to use, copy, modify, merge, publish, 
# distribute, sublicense, and/or sell copies of the Software, and to 
# permit persons to whom the Software is furnished to do so, subject to 
# the following conditions:
# 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import re
from string import Template
import warnings

# Import the webhelpers to create URLs
from webhelpers.html import literal, HTML

# import SQLAlchemy if available
try:
    import sqlalchemy
    import sqlalchemy.orm   # Some users report errors if this is not imported.
except:
    sqlalchemy_available = False
else:
    sqlalchemy_available = sqlalchemy.__version__

def get_wrapper(obj, sqlalchemy_session=None):
    """
    Auto-detect the kind of object and return a list/tuple
    to access items from the collection.
    """
    # If the collection is a sequence we can use it directly
    if isinstance(obj, (list, tuple)):
        return obj

    # If object is iterable we can use it directly
    if hasattr(obj, "__iter__") and hasattr(obj, "__len__"):
        return obj

    # Is SQLAlchemy 0.4 or better available? (0.3 is not supported - sorry)
    if sqlalchemy_available[:3] != '0.3':
        # Is the collection a query?
        if isinstance(obj, sqlalchemy.orm.query.Query):
            return _SQLAlchemyQuery(obj)

        # Is the collection an SQLAlchemy select object?
        if isinstance(obj, sqlalchemy.sql.expression.CompoundSelect) \
            or isinstance(obj, sqlalchemy.sql.expression.Select):
                return _SQLAlchemySelect(obj, sqlalchemy_session)

    raise TypeError("Sorry, your collection type is not supported by the "
        "paginate module. You can provide a list, a tuple, a SQLAlchemy "
        "select object or a SQLAlchemy ORM-query object.")

class _SQLAlchemySelect(object):
    """
    Iterable that allows to get slices from an SQLAlchemy Select object
    """
    def __init__(self, obj, sqlalchemy_session=None):
        if not isinstance(sqlalchemy_session, sqlalchemy.orm.scoping.ScopedSession):
            raise TypeError("If you want to page an SQLAlchemy 'select' object then you "
                    "have to provide a 'sqlalchemy_session' argument. See also: "
                    "http://www.sqlalchemy.org/docs/04/session.html")

        self.sqlalchemy_session = sqlalchemy_session
        self.obj = obj

    def __getitem__(self, range):
        if not isinstance(range, slice):
            raise Exception, "__getitem__ without slicing not supported"
        offset = range.start
        limit = range.stop - range.start
        select = self.obj.offset(offset).limit(limit)
        return self.sqlalchemy_session.execute(select).fetchall()

    def __len__(self):
        return self.sqlalchemy_session.execute(self.obj).rowcount

class _SQLAlchemyQuery(object):
    """
    Iterable that allows to get slices from an SQLAlchemy Query object
    """
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, range):
        if not isinstance(range, slice):
            raise Exception, "__getitem__ without slicing not supported"
        return self.obj[range]

    def __len__(self):
        return self.obj.count()

# Since the items on a page are mainly a list we subclass the "list" type
class Page(list):
    """A list/iterator of items representing one page in a larger
    collection.

    An instance of the "Page" class is created from a collection of things. 
    The instance works as an iterator running from the first item to the 
    last item on the given page. The collection can be:

    - a sequence
    - an SQLAlchemy query - e.g.: Session.query(MyModel)
    - an SQLAlchemy select - e.g.: sqlalchemy.select([my_table])

    A "Page" instance maintains pagination logic associated with each 
    page, where it begins, what the first/last item on the page is, etc. 
    The pager() method creates a link list allowing the user to go to
    other pages.

    **WARNING:** Unless you pass in an item_count, a count will be 
    performed on the collection every time a Page instance is created. 
    If using an ORM, it's advised to pass in the number of items in the 
    collection if that number is known.

    Instance attributes:

    original_collection
        Points to the collection object being paged through

    item_count
        Number of items in the collection

    page
        Number of the current page

    items_per_page
        Maximal number of items displayed on a page

    first_page
        Number of the first page - starts with 1

    last_page
        Number of the last page

    page_count
        Number of pages

    items
        Sequence/iterator of items on the current page

    first_item
        Index of first item on the current page - starts with 1

    last_item
        Index of last item on the current page
        
    """
    def __init__(self, collection, page=1, items_per_page=20,
        item_count=None, sqlalchemy_session=None, presliced_list=False,
        url=None, **kwargs):
        """Create a "Page" instance.

        Parameters:

        collection
            Sequence, SQLAlchemy select object or SQLAlchemy ORM-query
            representing the collection of items to page through.

        page
            The requested page number - starts with 1. Default: 1.

        items_per_page
            The maximal number of items to be displayed per page.
            Default: 20.

        item_count (optional)
            The total number of items in the collection - if known.
            If this parameter is not given then the paginator will count
            the number of elements in the collection every time a "Page"
            is created. Giving this parameter will speed up things.
        
        presliced_list (optional)
            Indicates whether the collection, when a list, has already
            been sliced for the current viewing page, and thus should
            *not* be sliced again.

        sqlalchemy_session (optional)
            If you want to use an SQLAlchemy (0.4) select object as a
            collection then you need to provide an SQLAlchemy session object.
            Select objects do not have a database connection attached so it
            would not be able to execute the SELECT query.

        url (optional)
            A URL generator function. See module docstring for details.
            This is used only by ``.pager()``.

        Further keyword arguments are used as link arguments in the pager().
        """
        self._url_generator = url

        # 'page_nr' is deprecated.
        if 'page_nr' in kwargs:
            warnings.warn("'page_nr' is deprecated. Please use 'page' instead.")
            page = kwargs['page_nr']
            del kwargs['page_nr']

        # 'current_page' is also deprecated.
        if 'current_page' in kwargs:
            warnings.warn("'current_page' is deprecated. Please use 'page' instead.")
            page = kwargs['current_page']
            del kwargs['current_page']

        # Safe the kwargs class-wide so they can be used in the pager() method
        self.kwargs = kwargs

        # Save a reference to the collection
        self.original_collection = collection

        # Decorate the ORM/sequence object with __getitem__ and __len__
        # functions to be able to get slices.
        if collection is not None:
            # Determine the type of collection and use a wrapper for ORMs
            self.collection = get_wrapper(collection, sqlalchemy_session)
        else:
            self.collection = []

        # The self.page is the number of the current page.
        # The first page has the number 1!
        try:
            self.page = int(page) # make it int() if we get it as a string
        except (ValueError, TypeError):
            self.page = 1

        self.items_per_page = items_per_page

        # Unless the user tells us how many items the collections has
        # we calculate that ourselves.
        if item_count is not None:
            self.item_count = item_count
        else:
            self.item_count = len(self.collection)

        # Compute the number of the first and last available page
        if self.item_count > 0:
            self.first_page = 1
            self.page_count = ((self.item_count - 1) / self.items_per_page) + 1
            self.last_page = self.first_page + self.page_count - 1

            # Make sure that the requested page number is the range of valid pages
            if self.page > self.last_page:
                self.page = self.last_page
            elif self.page < self.first_page:
                self.page = self.first_page

            # Note: the number of items on this page can be less than
            #       items_per_page if the last page is not full
            self.first_item = (self.page - 1) * items_per_page + 1
            self.last_item = min(self.first_item + items_per_page - 1, self.item_count)

            # We subclassed "list" so we need to call its init() method
            # and fill the new list with the items to be displayed on the page.
            # We use list() so that the items on the current page are retrieved
            # only once. Otherwise it would run the actual SQL query everytime
            # .items would be accessed.
            if presliced_list:
                self.items = self.collection
            else:
                self.items = list(self.collection[self.first_item-1:self.last_item])

            # Links to previous and next page
            if self.page > self.first_page:
                self.previous_page = self.page-1
            else:
                self.previous_page = None

            if self.page < self.last_page:
                self.next_page = self.page+1
            else:
                self.next_page = None

        # No items available
        else:
            self.first_page = None
            self.page_count = 0
            self.last_page = None
            self.first_item = None
            self.last_item = None
            self.previous_page = None
            self.next_page = None
            self.items = []

        # This is a subclass of the 'list' type. Initialise the list now.
        list.__init__(self, self.items)


    def __repr__(self):
        return ("Page:\n"
            "Collection type:  %(type)s\n"
            "(Current) page:   %(page)s\n"
            "First item:       %(first_item)s\n"
            "Last item:        %(last_item)s\n"
            "First page:       %(first_page)s\n"
            "Last page:        %(last_page)s\n"
            "Previous page:    %(previous_page)s\n"
            "Next page:        %(next_page)s\n"
            "Items per page:   %(items_per_page)s\n"
            "Number of items:  %(item_count)s\n"
            "Number of pages:  %(page_count)s\n"
            % {
            'type':type(self.collection),
            'page':self.page,
            'first_item':self.first_item,
            'last_item':self.last_item,
            'first_page':self.first_page,
            'last_page':self.last_page,
            'previous_page':self.previous_page,
            'next_page':self.next_page,
            'items_per_page':self.items_per_page,
            'item_count':self.item_count,
            'page_count':self.page_count,
            })

    def pager(self, format='~2~', page_param='page', partial_param='partial',
        show_if_single_page=False, separator=' ', onclick=None,
        symbol_first='<<', symbol_last='>>',
        symbol_previous='<', symbol_next='>',
        link_attr={'class':'pager_link'}, curpage_attr={'class':'pager_curpage'},
        dotdot_attr={'class':'pager_dotdot'}, **kwargs):
        """
        Return string with links to other pages (e.g. "1 2 [3] 4 5 6 7").

        format:
            Format string that defines how the pager is rendered. The string
            can contain the following $-tokens that are substituted by the
            string.Template module:

            - $first_page: number of first reachable page
            - $last_page: number of last reachable page
            - $page: number of currently selected page
            - $page_count: number of reachable pages
            - $items_per_page: maximal number of items per page
            - $first_item: index of first item on the current page
            - $last_item: index of last item on the current page
            - $item_count: total number of items
            - $link_first: link to first page (unless this is first page)
            - $link_last: link to last page (unless this is last page)
            - $link_previous: link to previous page (unless this is first page)
            - $link_next: link to next page (unless this is last page)

            To render a range of pages the token '~3~' can be used. The 
            number sets the radius of pages around the current page.
            Example for a range with radius 3:

            '1 .. 5 6 7 [8] 9 10 11 .. 500'

            Default: '~2~'

        symbol_first
            String to be displayed as the text for the %(link_first)s 
            link above.

            Default: '<<'

        symbol_last
            String to be displayed as the text for the %(link_last)s 
            link above.

            Default: '>>'

        symbol_previous
            String to be displayed as the text for the %(link_previous)s 
            link above.

            Default: '<'

        symbol_next
            String to be displayed as the text for the %(link_next)s 
            link above.

            Default: '>'

        separator:
            String that is used to seperate page links/numbers in the 
            above range of pages.

            Default: ' '

        page_param:
            The name of the parameter that will carry the number of the 
            page the user just clicked on. The parameter will be passed 
            to a url_for() call so if you stay with the default 
            ':controller/:action/:id' routing and set page_param='id' then 
            the :id part of the URL will be changed. If you set 
            page_param='page' then url_for() will make it an extra 
            parameters like ':controller/:action/:id?page=1'. 
            You need the page_param in your action to determine the page 
            number the user wants to see. If you do not specify anything 
            else the default will be a parameter called 'page'.

        partial_param:
            When using AJAX/AJAH to do partial updates of the page area the
            application has to know whether a partial update (only the
            area to be replaced) or a full update (reloading the whole
            page) is required. So this parameter is the name of the URL
            parameter that gets set to 1 if the 'onclick' parameter is
            used. So if the user requests a new page through a Javascript
            action (onclick) then this parameter gets set and the application
            is supposed to return a partial content. And without
            Javascript this parameter is not set. The application thus has
            to check for the existance of this parameter to determine
            whether only a partial or a full page needs to be returned.
            See also the examples in this modules docstring.

            Default: 'partial'

        show_if_single_page:
            if True the navigator will be shown even if there is only 
            one page
            
            Default: False

        link_attr (optional)
            A dictionary of attributes that get added to A-HREF links 
            pointing to other pages. Can be used to define a CSS style 
            or class to customize the look of links.

            Example: { 'style':'border: 1px solid green' }

            Default: { 'class':'pager_link' }

        curpage_attr (optional)
            A dictionary of attributes that get added to the current 
            page number in the pager (which is obviously not a link).
            If this dictionary is not empty then the elements
            will be wrapped in a SPAN tag with the given attributes.

            Example: { 'style':'border: 3px solid blue' }

            Default: { 'class':'pager_curpage' }

        dotdot_attr (optional)
            A dictionary of attributes that get added to the '..' string
            in the pager (which is obviously not a link). If this 
            dictionary is not empty then the elements will be wrapped in 
            a SPAN tag with the given attributes.

            Example: { 'style':'color: #808080' }

            Default: { 'class':'pager_dotdot' }

        onclick (optional)
            This paramter is a string containing optional Javascript code
            that will be used as the 'onclick' action of each pager link.
            It can be used to enhance your pager with AJAX actions loading another 
            page into a DOM object. 

            In this string the variable '$partial_url' will be replaced by
            the URL linking to the desired page with an added 'partial=1'
            parameter (or whatever you set 'partial_param' to).
            In addition the '$page' variable gets replaced by the
            respective page number.

            Note that the URL to the destination page contains a 'partial_param' 
            parameter so that you can distinguish between AJAX requests (just 
            refreshing the paginated area of your page) and full requests (loading 
            the whole new page).

            [Backward compatibility: you can use '%s' instead of '$partial_url']

            jQuery example:
                "$('#my-page-area').load('$partial_url'); return false;"

            Yahoo UI example:
                "YAHOO.util.Connect.asyncRequest('GET','$partial_url',{
                    success:function(o){YAHOO.util.Dom.get('#my-page-area').innerHTML=o.responseText;}
                    },null); return false;"

            scriptaculous example:
                "new Ajax.Updater('#my-page-area', '$partial_url',
                    {asynchronous:true, evalScripts:true}); return false;"

            ExtJS example:
                "Ext.get('#my-page-area').load({url:'$partial_url'}); return false;"
            
            Custom example:
                "my_load_page($page)"

        Additional keyword arguments are used as arguments in the links.
        Otherwise the link will be created with url_for() which points 
        to the page you are currently displaying.
        """
        self.curpage_attr = curpage_attr
        self.separator = separator
        self.pager_kwargs = kwargs
        self.page_param = page_param
        self.partial_param = partial_param
        self.onclick = onclick
        self.link_attr = link_attr
        self.dotdot_attr = dotdot_attr

        # Don't show navigator if there is no more than one page
        if self.page_count == 0 or (self.page_count == 1 and not show_if_single_page):
            return ''


        # Replace ~...~ in token format by range of pages
        result = re.sub(r'~(\d+)~', self._range, format)

        # Interpolate '%' variables
        result = Template(result).safe_substitute({
            'first_page': self.first_page,
            'last_page': self.last_page,
            'page': self.page,
            'page_count': self.page_count,
            'items_per_page': self.items_per_page,
            'first_item': self.first_item,
            'last_item': self.last_item,
            'item_count': self.item_count,
            'link_first': self.page>self.first_page and \
                    self._pagerlink(self.first_page, symbol_first) or '',
            'link_last': self.page<self.last_page and \
                    self._pagerlink(self.last_page, symbol_last) or '',
            'link_previous': self.previous_page and \
                    self._pagerlink(self.previous_page, symbol_previous) or '',
            'link_next': self.next_page and \
                    self._pagerlink(self.next_page, symbol_next) or ''
        })

        return literal(result)

    def get_url_generator(self):
        """Return a URL generator. See module docstring for details."""
        if self._url_generator is None:
            try:
                import pylons
                self._url_generator = pylons.url.current
            except (ImportError, AttributeError):
                try:
                    import routes
                    self._url_generator = routes.url_for
                except (ImportError, AttributeError):
                    raise NotImplementedError("no URL generator available")
        return self._url_generator


    #### Private methods ####
    def _range(self, regexp_match):
        """
        Return range of linked pages (e.g. '1 2 [3] 4 5 6 7 8').

        Arguments:
            
        regexp_match
            A "re" (regular expressions) match object containing the
            radius of linked pages around the current page in
            regexp_match.group(1) as a string

        This funtion is supposed to be called as a callable in 
        re.sub.
        
        """
        radius = int(regexp_match.group(1))

        # Compute the first and last page number within the radius
        # e.g. '1 .. 5 6 [7] 8 9 .. 12'
        # -> leftmost_page  = 5
        # -> rightmost_page = 9
        leftmost_page = max(self.first_page, (self.page-radius))
        rightmost_page = min(self.last_page, (self.page+radius))

        nav_items = []

        # Create a link to the first page (unless we are on the first page
        # or there would be no need to insert '..' spacers)
        if self.page != self.first_page and self.first_page < leftmost_page:
            nav_items.append( self._pagerlink(self.first_page, self.first_page) )

        # Insert dots if there are pages between the first page
        # and the currently displayed page range
        if leftmost_page - self.first_page > 1:
            # Wrap in a SPAN tag if nolink_attr is set
            text = '..'
            if self.dotdot_attr:
                text = HTML.span(c=text, **self.dotdot_attr)
            nav_items.append(text)

        for thispage in xrange(leftmost_page, rightmost_page+1):
            # Hilight the current page number and do not use a link
            if thispage == self.page:
                text = '%s' % (thispage,)
                # Wrap in a SPAN tag if nolink_attr is set
                if self.curpage_attr:
                    text = HTML.span(c=text, **self.curpage_attr)
                nav_items.append(text)
            # Otherwise create just a link to that page
            else:
                text = '%s' % (thispage,)
                nav_items.append( self._pagerlink(thispage, text) )

        # Insert dots if there are pages between the displayed
        # page numbers and the end of the page range
        if self.last_page - rightmost_page > 1:
            text = '..'
            # Wrap in a SPAN tag if nolink_attr is set
            if self.dotdot_attr:
                text = HTML.span(c=text, **self.dotdot_attr)
            nav_items.append(text)

        # Create a link to the very last page (unless we are on the last
        # page or there would be no need to insert '..' spacers)
        if self.page != self.last_page and rightmost_page < self.last_page:
            nav_items.append( self._pagerlink(self.last_page, self.last_page) )

        return self.separator.join(nav_items)

    def _pagerlink(self, page, text):
        """
        Create a URL that links to another page using url_for().

        Parameters:
            
        page
            Number of the page that the link points to

        text
            Text to be printed in the A-HREF tag
        """
        # Let the url_for() from webhelpers create a new link and set
        # the variable called 'page_param'. Example:
        # You are in '/foo/bar' (controller='foo', action='bar')
        # and you want to add a parameter 'page'. Then you
        # call the navigator method with page_param='page' and
        # the url_for() call will create a link '/foo/bar?page=...'
        # with the respective page number added.
        link_params = {}
        # Use the instance kwargs from Page.__init__ as URL parameters
        link_params.update(self.kwargs)
        # Add keyword arguments from pager() to the link as parameters
        link_params.update(self.pager_kwargs)
        link_params[self.page_param] = page

        # Get the URL generator
        if self._url_generator is not None:
            url_generator = self._url_generator
        else:
            try:
                import pylons
                url_generator = pylons.url.current
            except (ImportError, AttributeError):
                try:
                    import routes
                    url_generator = routes.url_for
                    config = routes.request_config()
                except (ImportError, AttributeError):
                    raise NotImplementedError("no URL generator available")
                else:
                    # if the Mapper is configured with explicit=True we have to fetch
                    # the controller and action manually
                    if config.mapper.explicit:
                        if hasattr(config, 'mapper_dict'):
                            for k, v in config.mapper_dict.items():
                                link_params[k] = v

        # Create the URL to load a certain page
        link_url = url_generator(**link_params)

        if self.onclick: # create link with onclick action for AJAX
            # Create the URL to load the page area part of a certain page (AJAX
            # updates)
            link_params[self.partial_param] = 1
            partial_url = url_generator(**link_params)
            try: # if '%s' is used in the 'onclick' parameter (backwards compatibility)
                onclick_action = self.onclick % (partial_url,)
            except TypeError:
                onclick_action = Template(self.onclick).safe_substitute({
                  "partial_url": partial_url,
                  "page": page
                })
            return HTML.a(text, href=link_url, onclick=onclick_action, **self.link_attr)
        else: # return static link
            return HTML.a(text, href=link_url, **self.link_attr)

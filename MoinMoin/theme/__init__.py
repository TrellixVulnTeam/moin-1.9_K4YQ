# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - Theme Package

    @copyright: 2003-2005 by Thomas Waldmann (MoinMoin:ThomasWaldmann)
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin import i18n, wikiutil, config, version
from MoinMoin.Page import Page
from MoinMoin.util import pysupport

modules = pysupport.getPackageModules(__file__)


class ThemeBase:
    """ Base class for themes 
    
    This class supply all the standard template that sub classes can 
    use without rewriting the same code. If you want to change certain 
    elements, override them. 
    """
    
    name = 'base'
    
    # fake _ function to get gettext recognize those texts:
    _ = lambda x: x

    # TODO: remove icons that are not used any more.
    icons = {
        # key         alt                        icon filename      w   h
        # ------------------------------------------------------------------
        # navibar
        'help':       ("%(page_help_contents)s", "moin-help.png",   12, 11),
        'find':       ("%(page_find_page)s",     "moin-search.png", 12, 12),
        'diff':       (_("Diffs"),               "moin-diff.png",   15, 11),
        'info':       (_("Info"),                "moin-info.png",   12, 11),
        'edit':       (_("Edit"),                "moin-edit.png",   12, 12),
        'unsubscribe':(_("Unsubscribe"),         "moin-unsubscribe.png",  14, 10),
        'subscribe':  (_("Subscribe"),           "moin-subscribe.png",14, 10),
        'raw':        (_("Raw"),                 "moin-raw.png",    12, 13),
        'xml':        (_("XML"),                 "moin-xml.png",    20, 13),
        'print':      (_("Print"),               "moin-print.png",  16, 14),
        'view':       (_("View"),                "moin-show.png",   12, 13),
        'home':       (_("Home"),                "moin-home.png",   13, 12),
        'up':         (_("Up"),                  "moin-parent.png", 15, 13),
        # FileAttach
        'attach':     ("%(attach_count)s",       "moin-attach.png",  7, 15),
        # RecentChanges
        'rss':        (_("[RSS]"),               "moin-rss.png",    36, 14),
        'deleted':    (_("[DELETED]"),           "moin-deleted.png",60, 12),
        'updated':    (_("[UPDATED]"),           "moin-updated.png",60, 12),
        'new':        (_("[NEW]"),               "moin-new.png",    31, 12),
        'diffrc':     (_("[DIFF]"),              "moin-diff.png",   15, 11),
        # General
        'bottom':     (_("[BOTTOM]"),            "moin-bottom.png", 14, 10),
        'top':        (_("[TOP]"),               "moin-top.png",    14, 10),
        'www':        ("[WWW]",                  "moin-www.png",    11, 11),
        'mailto':     ("[MAILTO]",               "moin-email.png",  14, 10),
        'news':       ("[NEWS]",                 "moin-news.png",   10, 11),
        'telnet':     ("[TELNET]",               "moin-telnet.png", 10, 11),
        'ftp':        ("[FTP]",                  "moin-ftp.png",    11, 11),
        'file':       ("[FILE]",                 "moin-ftp.png",    11, 11),
        # search forms
        'searchbutton': ("[?]",                  "moin-search.png", 12, 12),
        'interwiki':  ("[%(wikitag)s]",          "moin-inter.png",  16, 16),
    }
    del _

    # Style sheets - usually there is no need to override this in sub
    # classes. Simply supply the css files in the css directory.

    # Standard set of style sheets
    stylesheets = (
        # media         basename
        ('all',         'common'),
        ('screen',      'screen'),
        ('print',       'print'),
        ('projection',  'projection'),
        )

    # Used in print mode
    stylesheets_print = (
        # media         basename
        ('all',         'common'),
        ('all',         'print'),
        )

    # Used in slide show mode
    stylesheets_projection = (
        # media         basename
        ('all',         'common'),
        ('all',         'projection'),
       )   

    stylesheetsCharset = 'utf-8'

    def __init__(self, request):
        """
        Initialize the theme object.
        
        @param request: the request object
        """
        self.request = request
        self.cfg = request.cfg
        self._cache = {} # Used to cache elements that may be used several times

    def img_url(self, img):
        """ Generate an image href

        @param img: the image filename
        @rtype: string
        @return: the image href
        """
        return "%s/%s/img/%s" % (self.cfg.url_prefix, self.name, img)
        
    def emit_custom_html(self, html):
        """
        generate custom HTML code in `html`
        
        @param html: a string or a callable object, in which case
                     it is called and its return value is used
        @rtype: string
        @return: string with html
        """
        if html:
            if callable(html): html = html(self.request)
        return html

    def logo(self):
        """ Assemble logo with link to front page

        The logo contain an image and or text or any html markup the
        admin inserted in the config file. Everything it enclosed inside
        a div with id="logo".
        
        @rtype: unicode
        @return: logo html
        """
        html = u''
        if self.cfg.logo_string:
            pagename = wikiutil.getFrontPage(self.request).page_name
            pagename = wikiutil.quoteWikinameURL(pagename)
            logo = wikiutil.link_tag(self.request, pagename, self.cfg.logo_string)
            html = u'''<div id="logo">%s</div>''' % logo
        return html

    def interwiki(self, d):
        """ Assemble the interwiki name display, linking to page_front_page
        
        @param d: parameter dictionary
        @rtype: string
        @return: interwiki html
        """
        html = u''
        if self.request.cfg.show_interwiki:
            # Show our interwikiname or Self (and link to page_front_page)
            pagename = wikiutil.getFrontPage(self.request).page_name
            pagename = wikiutil.quoteWikinameURL(pagename)
            link = wikiutil.link_tag(self.request, pagename, self.request.cfg.interwikiname or 'Self')
            html = u'<div id="interwiki"><span>%s</span></div>' % link
        return html
        
    def title(self, d):
        """ Assemble the title (now using breadcrumbs)
        
        @param d: parameter dictionary
        @rtype: string
        @return: title html
        """
        _ = self.request.getText
        content = []
        if d['title_link']: # having a link means we have a (linked) pagename ONLY as title, not a message title
                            # XXX this method is rather ugly and should be improved
            curpage = ''
            segments = d['page_name'].split('/') # was: title_text
            for s in segments[:-1]:
                curpage += s
                content.append("<li>%s</li>" % Page(self.request, curpage).link_to(self.request, s))
                curpage += '/'
            content.append(('<li><a class="backlink" title="%(title)s" href="%(href)s">%(text)s</a></li>') % {
                'title': _('Click to do a full-text search for this title'),
                'href': d['title_link'],
                'text': wikiutil.escape(segments[-1]),
                })
        else:
            content.append('<li>%s</li>' % wikiutil.escape(d['title_text']))

        html = '''
<ul id="pagelocation">
%s
</ul>
''' % "".join(content)
        return html

    def username(self, d):
        """ Assemble the username / userprefs link
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: username html
        """
        request = self.request
        _ = request.getText
        
        userlinks = []
        # Add username/homepage link for registered users. We don't care
        # if it exists, the user can create it.
        if request.user.valid and request.user.name:
            interwiki = wikiutil.getInterwikiHomePage(request)
            name = request.user.name
            aliasname = request.user.aliasname
            if not aliasname:
                aliasname = name
            title = "%s @ %s" % (aliasname, interwiki[0])
            # link to (interwiki) user homepage
            homelink = (request.formatter.interwikilink(1, title=title, id="userhome", *interwiki) +
                        request.formatter.text(name) +
                        request.formatter.interwikilink(0, title=title, id="userhome", *interwiki))
            userlinks.append(homelink)        
            # link to userprefs action
            userlinks.append(d['page'].link_to(request, text=_('Preferences'),
                                               querystr={'action': 'userprefs'}, id="userprefs"))
           
        if request.cfg.show_login:
            if request.user.valid:
                userlinks.append(d['page'].link_to(request, text=_('Logout', formatted=False),
                                                   querystr={'action': 'logout', 'logout': 'logout'}, id="logout"))
            else:
                userlinks.append(d['page'].link_to(request, text=_("Login", formatted=False),
                                                   querystr={'action': 'login'}, id="login"))

        userlinks = [u'<li>%s</li>' % link for link in userlinks]
        html = u'<ul id="username">%s</ul>' % ''.join(userlinks)
        return html

    # Schemas supported in toolbar links, using [url label] format
    linkSchemas = [r'http://', r'https://', r'ftp://', 'mailto:', r'irc://', ] + \
                  [x + ':' for x in config.url_schemas]

    def splitNavilink(self, text, localize=1):
        """ Split navibar links into pagename, link to page

        Admin or user might want to use shorter navibar items by using
        the [page title] or [url title] syntax. In this case, we don't
        use localization, and the links goes to page or to the url, not
        the localized version of page.

        @param text: the text used in config or user preferences
        @rtype: tuple
        @return: pagename or url, link to page or url
        """
        request = self.request
        
        # Handle [pagename title] or [url title] formats
        if text.startswith('[') and text.endswith(']'):
            try:
                pagename, title = text[1:-1].strip().split(' ', 1)
                title = title.strip()
                localize = 0
            except (ValueError, TypeError):
                # Just use the text as is.
                pagename = title = text

        # Handle regular pagename like "FrontPage"
        else:
            # Use localized pages for the current user
            if localize:
                page = wikiutil.getSysPage(request, text)
            else:
                page = Page(request, text)
            pagename = page.page_name
            title = page.split_title(request)
            title = self.shortenPagename(title)
            link = page.link_to(request, title)


        from MoinMoin import config
        for scheme in self.linkSchemas:
            if pagename.startswith(scheme):
                title = wikiutil.escape(title)
                link = '<a href="%s">%s</a>' % (pagename, title)
                return pagename, link

        # remove wiki: url prefix
        if pagename.startswith("wiki:"):
            pagename = pagename[5:]

        # try handling interwiki links
        try:
            interwiki, page = pagename.split(':', 1)
            thiswiki = request.cfg.interwikiname
            if interwiki == thiswiki:
                pagename = page
                title = page
            else:
                return (pagename,
                        self.request.formatter.interwikilink(True, interwiki, page) +
                        page +
                        self.request.formatter.interwikilink(False, interwiki, page)
                        )
        
        except ValueError:
            pass
                  
        # Normalize page names, replace '_' with ' '. Usually
        # all names use spaces internally, but for
        # [name_with_spaces label] we must save the underscores
        # until this point.
        pagename = request.normalizePagename(pagename)
        link = Page(request, pagename).link_to(request, title)

        return pagename, link

    def shortenPagename(self, name):
        """ Shorten page names
        
        Shorten very long page names that tend to break the user
        interface. The short name is usually fine, unless really stupid
        long names are used (WYGIWYD).

        If you don't like to do this in your theme, or want to use
        different algorithm, override this method.
        
        @param name: page name, unicode
        @rtype: unicode
        @return: shortened version.
        """
        maxLength = self.maxPagenameLength()
        # First use only the sub page name, that might be enough
        if len(name) > maxLength:
            name = name.split('/')[-1]
            # If it's not enough, replace the middle with '...'
            if len(name) > maxLength:
                half, left = divmod(maxLength - 3, 2)
                name = u'%s...%s' % (name[:half + left], name[-half:])
        return name
        
    def maxPagenameLength(self):
        """ Return maximum length for shortened page names """
        return 25 

    def navibar(self, d):
        """ Assemble the navibar

        @param d: parameter dictionary
        @rtype: unicode
        @return: navibar html
        """
        request = self.request
        found = {} # pages we found. prevent duplicates
        items = [] # navibar items
        item = u'<li class="%s">%s</li>'
        current = d['page_name']

        # Process config navi_bar
        if request.cfg.navi_bar:
            for text in request.cfg.navi_bar:
                pagename, link = self.splitNavilink(text)
                if pagename == current:
                    cls = 'wikilink current'
                else:
                    cls = 'wikilink'
                items.append(item % (cls, link))
                found[pagename] = 1

        # Add user links to wiki links, eliminating duplicates.
        userlinks = request.user.getQuickLinks()
        for text in userlinks:
            # Split text without localization, user knows what he wants
            pagename, link = self.splitNavilink(text, localize=0)
            if not pagename in found:
                if pagename == current:
                    cls = 'userlink current'
                else:
                    cls = 'userlink'
                items.append(item % (cls, link))
                found[pagename] = 1

        # Add current page at end
        if not current in found:
            title = d['page'].split_title(request)
            title = self.shortenPagename(title)
            link = d['page'].link_to(request, title)
            cls = 'current'
            items.append(item % (cls, link))

        # Assemble html
        items = u''.join(items)
        html = u'''
<ul id="navibar">
%s
</ul>
''' % items
        return html

    def get_icon(self, icon):
        """ Return icon data from self.icons

        If called from [[Icon(file)]] we have a filename, not a
        key. Using filenames is deprecated, but for now, we simulate old
        behavior.

        @param icon: icon name or file name (string)
        @rtype: tuple
        @return: alt (unicode), href (string), width, height (int)
        """
        if icon in self.icons:
            alt, filename, w, h = self.icons[icon]
        else:
            # Create filenames to icon data mapping on first call, then
            # cache in class for next calls.
            if not getattr(self.__class__, 'iconsByFile', None):
                d = {}
                for data in self.icons.values():
                    d[data[1]] = data
                self.__class__.iconsByFile = d

            # Try to get icon data by file name
            filename = icon.replace('.gif','.png')
            if filename in self.iconsByFile:
                alt, filename, w, h = self.iconsByFile[filename]
            else:
                alt, filename, w, h = '', icon, '', ''
                
        return alt, self.img_url(filename), w, h
   
    def make_icon(self, icon, vars=None):
        """
        This is the central routine for making <img> tags for icons!
        All icons stuff except the top left logo, smileys and search
        field icons are handled here.
        
        @param icon: icon id (dict key)
        @param vars: ...
        @rtype: string
        @return: icon html (img tag)
        """
        if vars is None:
            vars = {}
        alt, img, w, h = self.get_icon(icon)
        try:
            alt = alt % vars
        except KeyError, err:
            alt = 'KeyError: %s' % str(err)
        if self.request:
            alt = self.request.getText(alt, formatted=False)
        try:
            tag = self.request.formatter.image(src=img, alt=alt, width=w, height=h)
        except AttributeError: # XXX FIXME if we have no formatter or no request 
            tag = '<img src="%s" alt="%s" width="%s" height="%s">' % (
                img, alt, w, h)
            import warnings
            warnings.warn("calling themes without correct request", DeprecationWarning)
        return tag

    def make_iconlink(self, which, d):
        """
        Make a link with an icon

        @param which: icon id (dictionary key)
        @param d: parameter dictionary
        @rtype: string
        @return: html link tag
        """
        page_params, title, icon = self.cfg.page_icons_table[which]
        d['title'] = title % d
        d['i18ntitle'] = self.request.getText(d['title'], formatted=False)
        img_src = self.make_icon(icon, d)
        return wikiutil.link_tag(self.request, page_params % d, img_src, title="%(i18ntitle)s" % d)

    def msg(self, d):
        """ Assemble the msg display

        Display a message with a widget or simple strings with a clear message link.
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: msg display html
        """
        _ = self.request.getText
        msg = d['msg']
        if not msg:
            return u''

        if isinstance(msg, (str, unicode)):
            # Render simple strings with a close link
            close = d['page'].link_to(self.request,
                                      text=_('Clear message'),
                                      querystr={'action': 'show'})
            html = u'<p>%s</p>\n<div class="buttons">%s</div>\n' % (msg, close) 
        else:
            # msg is a widget
            html = msg.render()

        return u'<div id="message">\n%s\n</div>\n' % html
        
    def trail(self, d):
        """ Assemble page trail
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: trail html
        """
        request = self.request
        user = request.user
        html = ''
        if user.valid and user.show_page_trail:
            trail = user.getTrail()
            if trail:
                items = []
                for pagename in trail:
                    try:
                        interwiki, page = pagename.split(":", 1)
                        # Items in trail are saved as valid interwiki
                        # links, using _ for spaces.
                        page = page.replace('_', ' ')
                        if request.cfg.interwikiname != interwiki:
                            link = (self.request.formatter.interwikilink(True, interwiki, page) +
                                    self.shortenPagename(page) +
                                    self.request.formatter.interwikilink(False, interwiki, page))
                            items.append('<li>%s</li>' % link)
                            continue
                        else:
                            pagename = page
                            
                    except ValueError:
                        pass
                    page = Page(request, pagename)
                    title = page.split_title(request)
                    title = self.shortenPagename(title)
                    link = page.link_to(request, title)
                    items.append('<li>%s</li>' % link)
                html = '''
<ul id="pagetrail">
%s
</ul>''' % ''.join(items)
        return html

    def html_stylesheets(self, d):
        """ Assemble html head stylesheet links
        
        @param d: parameter dictionary
        @rtype: string
        @return: stylesheets links
        """
        link = '<link rel="stylesheet" type="text/css" charset="%s" media="%s" href="%s">'

        # Check mode
        if d.get('print_mode'):
            media = d.get('media', 'print')
            stylesheets = getattr(self, 'stylesheets_' + media)
        else:
            stylesheets = self.stylesheets
        usercss = self.request.user.valid and self.request.user.css_url

        # Create stylesheets links
        html = []
        prefix = self.cfg.url_prefix
        csshref = '%s/%s/css' % (prefix, self.name)
        for media, basename in stylesheets:
            href = '%s/%s.css' % (csshref, basename)
            html.append(link % (self.stylesheetsCharset, media, href))

            # Don't add user css url if it matches one of ours
            if usercss and usercss == href:
                usercss = None

        # admin configurable additional css (farm or wiki level)
        for media, csshref in self.request.cfg.stylesheets:
            html.append(link % (self.stylesheetsCharset, media, csshref))

        
        # tribute to the most sucking browser...
        if self.cfg.hacks.get('ie7', False):
            html.append("""
<!-- compliance patch for microsoft browsers -->
<!--[if lt IE 7]>
   <script src="%s/common/ie7/ie7-standard-p.js" type="text/javascript"></script>
<![endif]-->
""" % prefix)

        # Add user css url (assuming that user css uses same charset)
        if usercss and usercss.lower() != "none":
            html.append(link % (self.stylesheetsCharset, 'all', usercss))
            
        return '\n'.join(html)

    def shouldShowPageinfo(self, page):
        """ Should we show page info?

        Should be implemented by actions. For now, we check here by action
        name and page.

        @param page: current page
        @rtype: bool
        @return: true if should show page info
        """
        if page.exists() and self.request.user.may.read(page.page_name):
            # These  actions show the  page content.
            # TODO: on new action, page info will not show. A better
            # solution will be if the action itself answer the question:
            # showPageInfo().
            contentActions = [u'', u'show', u'refresh', u'preview', u'diff',
                              u'subscribe', u'RenamePage', u'DeletePage',
                              u'SpellCheck', u'print']
            action = self.request.form.get('action', [''])[0]
            return action in contentActions
        return False
    
    def pageinfo(self, page):
        """ Return html fragment with page meta data

        Since page information uses translated text, it uses the ui
        language and direction. It looks strange sometimes, but
        translated text using page direction looks worse.
        
        @param page: current page
        @rtype: unicode
        @return: page last edit information
        """
        _ = self.request.getText
        html = ''
        if self.shouldShowPageinfo(page):
            info = page.lastEditInfo()
            if info:
                if info['editor']:
                    info = _("last edited %(time)s by %(editor)s") % info
                else:
                    info = _("last modified %(time)s") % info
                pagename = page.page_name
                if self.request.cfg.show_interwiki:
                    pagename = "%s: %s" % (self.request.cfg.interwikiname, pagename)
                info = "%s  (%s)" % (pagename, info)
                html = '<p id="pageinfo" class="info"%(lang)s>%(info)s</p>\n' % {
                    'lang': self.ui_lang_attr(),
                    'info': info
                    }
        return html
    
    def searchform(self, d):
        """
        assemble HTML code for the search forms
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: search form html
        """
        _ = self.request.getText
        form = self.request.form
        updates = {
            'search_label' : _('Search:'),
            'search_value': wikiutil.escape(form.get('value', [''])[0], 1),
            'search_full_label' : _('Text', formatted=False),
            'search_title_label' : _('Titles', formatted=False),
            }
        d.update(updates)

        html = u'''
<form id="searchform" method="get" action="">
<div>
<input type="hidden" name="action" value="fullsearch">
<input type="hidden" name="context" value="180">
<label for="searchinput">%(search_label)s</label>
<input id="searchinput" type="text" name="value" value="%(search_value)s" size="20"
    onfocus="searchFocus(this)" onblur="searchBlur(this)"
    onkeyup="searchChange(this)" onchange="searchChange(this)" alt="Search">
<input id="titlesearch" name="titlesearch" type="submit"
    value="%(search_title_label)s" alt="Search Titles">
<input id="fullsearch" name="fullsearch" type="submit"
    value="%(search_full_label)s" alt="Search Full Text">
</div>
</form>
<script type="text/javascript">
<!--// Initialize search form
var f = document.getElementById('searchform');
f.getElementsByTagName('label')[0].style.display = 'none';
var e = document.getElementById('searchinput');
searchChange(e);
searchBlur(e);
//-->
</script>
''' % d
        return html

    def showversion(self, d, **keywords):
        """
        assemble HTML code for copyright and version display
        
        @param d: parameter dictionary
        @rtype: string
        @return: copyright and version display html
        """
        html = ''
        if self.cfg.show_version and not keywords.get('print_mode', 0):
            html = (u'<div id="version">MoinMoin %s, Copyright 2000-2006 by '
                    'Juergen Hermann</div>') % (version.revision,)
        return html

    def headscript(self, d):
        """ Return html head script with common functions

        TODO: put these on common.js instead, so they can be downloaded
        only once.

        TODO: actionMenuInit should be called once, from body onload,
        but currently body is not written by theme.

        @param d: parameter dictionary
        @rtype: unicode
        @return: script for html head
        """
        # Don't add script for print view
        if self.request.form.get('action', [''])[0] == 'print':
            return u''
        
        _ = self.request.getText
        script = u"""
<script type=\"text/javascript\">
<!--// common functions

// We keep here the state of the search box
searchIsDisabled = false;

function searchChange(e) {
    // Update search buttons status according to search box content.
    // Ignore empty or whitespace search term.
    var value = e.value.replace(/\s+/, '');
    if (value == '' || searchIsDisabled) { 
        searchSetDisabled(true);
    } else {
        searchSetDisabled(false);
    }
}

function searchSetDisabled(flag) {
    // Enable or disable search
    document.getElementById('fullsearch').disabled = flag;
    document.getElementById('titlesearch').disabled = flag;
}

function searchFocus(e) {
    // Update search input content on focus
    if (e.value == '%(search_hint)s') {
        e.value = '';
        e.className = '';
        searchIsDisabled = false;
    }
}

function searchBlur(e) {
    // Update search input content on blur
    if (e.value == '') {
        e.value = '%(search_hint)s';
        e.className = 'disabled';
        searchIsDisabled = true;
    }
}

function actionsMenuInit(title) {
    // Initialize action menu
    for (i = 0; i < document.forms.length; i++) {
        var form = document.forms[i];
        if (form.className == 'actionsmenu') {
            // Check if this form needs update
            var div = form.getElementsByTagName('div')[0];
            var label = div.getElementsByTagName('label')[0];
            if (label) {
                // This is the first time: remove label and do buton.
                div.removeChild(label);
                var dobutton = div.getElementsByTagName('input')[0];
                div.removeChild(dobutton);
                // and add menu title
                var select = div.getElementsByTagName('select')[0];
                var item = document.createElement('option');
                item.appendChild(document.createTextNode(title));
                item.value = 'show';
                select.insertBefore(item, select.options[0]);
                select.selectedIndex = 0;
            }
        }
    }
}
//-->
</script>
""" % {
    'search_hint' : _('Search', formatted=False),
    }
        return script
    
    def shouldUseRSS(self):
        """ Return True if rss feature is available, or False

        Currently rss is broken on plain Python, and works only when
        installing PyXML. Return true if PyXML is installed.
        """
        # Stolen from wikitest.py
        try:
            import xml
            return xml.__file__.find('_xmlplus') != -1
        except ImportError:
            # This error reported on Python 2.2
            return False
        
    def rsshref(self):
        """ Create rss href, used for rss button and head link
        
        @rtype: unicode
        @return: rss href
        """
        return (u'%s/RecentChanges?action=rss_rc&amp;ddiffs=1&amp;unique=1' 
                % self.request.getScriptname())
                           
    def rsslink(self):
        """ Create rss link in head, used by FireFox

        RSS link for FireFox. This shows an rss link in the bottom of
        the page and let you subscribe to the wiki rss feed.

        @rtype: unicode
        @return: html head
        """
        link = u''
        if self.shouldUseRSS():
            link = (u'<link rel="alternate" title="%s Recent Changes" '
                    u'href="%s" type="application/rss+xml">') % (
                        self.cfg.sitename,
                        self.rsshref() )
        return link
       
    def html_head(self, d):
        """ Assemble html head
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: html head
        """
        html = [
            u'<title>%(title)s - %(sitename)s</title>' % d,
            self.externalScript('common'),
            self.headscript(d), # Should move to separate .js file
            self.guiEditorScript(d),
            self.html_stylesheets(d),
            self.rsslink(),
            ]
        return '\n'.join(html)

    def externalScript(self, name):
        """ Format external script html """
        src = '%s/common/js/%s.js' % (self.request.cfg.url_prefix, name)
        return '<script type="text/javascript" src="%s"></script>' % src

    def credits(self, d, **keywords):
        """ Create credits html from credits list """
        if isinstance(self.cfg.page_credits, (list, tuple)):
            items = ['<li>%s</li>' % i for i in self.cfg.page_credits]
            html = '<ul id="credits">\n%s\n</ul>\n' % ''.join(items)
        else:
            # Old config using string, output as is
            html = self.cfg.page_credits
        return html

    def actionsMenu(self, page):
        """ Create actions menu list and items data dict
        
        The menu will contain the same items always, but items that are
        not available will be disabled (some broken browsers will let
        you select disabled options though).

        The menu should give best user experience for javascript
        enabled browsers, and acceptable behavior for those who prefer
        not to use Javascript.

        TODO: Move actionsMenuInit() into body onload. This require
        that the theme will render body, its currently done on
        wikiutil/page.
        
        @param page: current page, Page object
        @rtype: unicode
        @return: actions menu html fragment
        """
        request = self.request
        _ = request.getText
        
        menu = [
            'raw',
            'print',
            'RenderAsDocbook',
            'refresh',
            '__separator__',
            'SpellCheck',
            'LikePages',
            'LocalSiteMap',
            '__separator__',
            'RenamePage',
            'DeletePage',
            '__separator__',
            'MyPages',
            'SubscribeUser',
            '__separator__',
            'Despam',
            'PackagePages',
            ]

        titles = {
            # action: menu title
            '__title__': _("More Actions:", formatted=False),
            # Translation may need longer or shorter separator
            '__separator__': _('------------', formatted=False),
            'raw': _('Raw Text', formatted=False),
            'print': _('Print View', formatted=False),
            'refresh': _('Delete Cache', formatted=False),
            'SpellCheck': _('Check Spelling', formatted=False), # rename action!
            'RenamePage': _('Rename Page', formatted=False),
            'DeletePage': _('Delete Page', formatted=False),
            'LikePages': _('Like Pages', formatted=False),
            'LocalSiteMap': _('Local Site Map', formatted=False),
            'MyPages': _('My Pages', formatted=False),
            'SubscribeUser': _('Subscribe User', formatted=False),
            'Despam': _('Remove Spam', formatted=False),
            'PackagePages': _('Package Pages', formatted=False),
            'RenderAsDocbook': _('Render as Docbook', formatted=False),
            }

        options = []
        option = '<option value="%(action)s"%(disabled)s>%(title)s</option>'
        # class="disabled" is a workaround for browsers that ignore
        # "disabled", e.g IE, Safari
        # for XHTML: data['disabled'] = ' disabled="disabled"'
        disabled = ' disabled class="disabled"'
        
        # Format standard actions
        available = request.getAvailableActions(page)
        for action in menu:
            data = {'action': action, 'disabled': '', 'title': titles[action]}

            # Enable delete cache only if page can use caching
            if action == 'refresh':
                if not page.canUseCache():
                    data['action'] = 'show'
                    data['disabled'] = disabled

            # Special menu items. Without javascript, executing will
            # just return to the page.
            elif action.startswith('__'):
                data['action'] = 'show'

            # Actions which are not available for this wiki, user or page
            if (action == '__separator__' or
                (action[0].isupper() and not action in available)):
                data['disabled'] = disabled               

            options.append(option % data)

        # Add custom actions not in the standard menu, except for
        # some actions like AttachFile (we have them on top level)
        more = [item for item in available if not item in titles and not item in ('AttachFile',)]
        more.sort()
        if more:
            # Add separator
            separator = option % {'action': 'show', 'disabled': disabled,
                                  'title': titles['__separator__']}
            options.append(separator)
            # Add more actions (all enabled)
            for action in more:
                data = {'action': action, 'disabled': ''}
                # Always add spaces: AttachFile -> Attach File 
                # XXX TODO do not create page just for using split_title
                title = Page(request, action).split_title(request, force=1)
                # Use translated version if available
                data['title'] = _(title, formatted=False)
                options.append(option % data)

        data = {
            'label': titles['__title__'],
            'options': '\n'.join(options),
            'do_button': _("Do")
            }

        html = '''
<form class="actionsmenu" method="get" action="">
<div>
    <label>%(label)s</label>
    <select name="action"
        onchange="if ((this.selectedIndex != 0) &&
                      (this.options[this.selectedIndex].disabled == false)) {
                this.form.submit();
            }
            this.selectedIndex = 0;">
        %(options)s
    </select>
    <input type="submit" value="%(do_button)s">
</div>
<script type="text/javascript">
<!--// Init menu
actionsMenuInit('%(label)s');
//-->
</script>
</form>
''' % data
        
        return html      
        
    def editbar(self, d):
        """ Assemble the page edit bar.

        Create html on first call, then return cached html.
                
        @param d: parameter dictionary
        @rtype: unicode
        @return: iconbar html
        """
        page = d['page']       
        if not self.shouldShowEditbar(page):
            return ''

        html = self._cache.get('editbar')
        if html is None:
            # Remove empty items and format as list
            items = ''.join(['<li>%s</li>' % item
                             for item in self.editbarItems(page) if item])
            html = u'<ul class="editbar">%s</ul>\n' % items
            self._cache['editbar'] = html
        
        return html

    def shouldShowEditbar(self, page):
        """ Should we show the editbar?

        Actions should implement this, because only the action knows if
        the edit bar makes sense. Until it goes into actions, we do the
        checking here.

        @param page: current page
        @rtype: bool
        @return: true if editbar should show
        """
        # Show editbar only for existing pages, including deleted pages,
        # that the user may read. If you may not read, you can't edit,
        # so you don't need editbar.
        if (page.exists(includeDeleted=1) and
            self.request.user.may.read(page.page_name)):
            form = self.request.form
            action = form.get('action', [''])[0]
            # Do not show editbar on edit but on save/cancel
            return not (action == 'edit' and
                        not form.has_key('button_save') and
                        not form.has_key('button_cancel'))
        return False

    def editbarItems(self, page):
        """ Return list of items to show on the editbar 

        This is separate method to make it easy to customize the
        edtibar in sub classes.
        """
        return [self.editorLink(page),
                self.infoLink(page),
                self.subscribeLink(page),
                self.quicklinkLink(page),
                self.attachmentsLink(page),
                self.actionsMenu(page),]

    def guiworks(self, page):
        """ Return whether the gui editor / converter can work for that page.

            The GUI editor currently only works for wiki format.
        """
        return page.pi_format == 'wiki'
        
    def editorLink(self, page):
        """ Return a link to the editor 
        
        If the user can't edit, return a disabled edit link.
        
        If the user want to show both editors, it will display "Edit
        (Text)", otherwise as "Edit".
        """
        if not (page.isWritable() and
                self.request.user.may.write(page.page_name)):
            return self.disabledEdit()
        
        _ = self.request.getText
        params = (wikiutil.quoteWikinameURL(page.page_name) +
                  '?action=edit&amp;editor=')
        
        guiworks = self.guiworks(page)
        if self.showBothEditLinks() and guiworks:
            text = _('Edit (Text)', formatted=False)
            params = params + 'text'
            attrs = {'name': "texteditlink"}
        else:
            text = _('Edit', formatted=False)
            if guiworks:
                # 'textonly' will be upgraded dynamically to 'guipossible' by JS
                params = params + 'textonly'
                attrs = {'name': "editlink"}
            else:
                params = params + 'text'
                attrs = {'name': "texteditlink"}
        
        return wikiutil.link_tag(self.request, params, text, **attrs)

    def showBothEditLinks(self):
        """ Return True if both edit links should be displayed """
        editor = self.request.user.editor_ui
        if editor == '<default>':
            editor = self.request.cfg.editor_ui
        return editor == 'freechoice'

    def guiEditorScript(self, d):
        """ Return a script that set the gui editor link variables
        
        The link will be created only when javascript is enabled and
        the browser is compatible with the editor.
        """
        page = d['page']
        if not (page.isWritable() and
                self.request.user.may.write(page.page_name) and
                self.showBothEditLinks() and
                self.guiworks(page)):
            return ''

        _ = self.request.getText
        return """\
<script type="text/javascript">
var gui_editor_link_href = "%(url)s?action=edit&editor=gui";
var gui_editor_link_text = "%(text)s";
</script>        
""" % {'url': page.url(self.request),
       'text': _('Edit (GUI)', formatted=False),}

    def disabledEdit(self):
        """ Return a disabled edit link """
        _ = self.request.getText
        return ('<span class="disabled">%s</span>' 
                % _('Immutable Page', formatted=False))
        
    def infoLink(self, page):
        """ Return link to page information """
        _ = self.request.getText
        return page.link_to(self.request,
                            text=_('Info', formatted=False), 
                            querystr='action=info')
    
    def subscribeLink(self, page):
        """ Return subscribe/unsubscribe link to valid users
        
        @rtype: unicode
        @return: subscribe or unsubscribe link
        """
        if not (self.cfg.mail_enabled and self.request.user.valid):
            return ''
        
        _ = self.request.getText
        if self.request.user.isSubscribedTo([page.page_name]):
            text = _("Unsubscribe", formatted=False)
        else:
            text = _("Subscribe", formatted=False)
        params = wikiutil.quoteWikinameURL(page.page_name) + '?action=subscribe'
        return wikiutil.link_tag(self.request, params, text)

    def quicklinkLink(self, page):
        """ Return add/remove quicklink link
        
        @rtype: unicode
        @return: link to add or remove a quicklink
        """
        if not self.request.user.valid:
            return ''
        
        _ = self.request.getText
        if self.request.user.isQuickLinkedTo([page.page_name]):
            text = _("Remove Link", formatted=False)
        else:
            text = _("Add Link", formatted=False)
        params = wikiutil.quoteWikinameURL(page.page_name) + '?action=quicklink'
        return wikiutil.link_tag(self.request, params, text)

    def attachmentsLink(self, page):
        """ Return link to page attachments """
        _ = self.request.getText
        return page.link_to(self.request,
                            text=_('Attachments', formatted=False), 
                            querystr='action=AttachFile')

    def startPage(self):
        """ Start page div with page language and direction
        
        @rtype: unicode
        @return: page div with language and direction attribtues
        """
        return u'<div id="page"%s>\n' % self.content_lang_attr()
            
    def endPage(self):
        """ End page div 
        
        Add an empty page bottom div to prevent floating elements to
        float out of the page bottom over the footer.
        """
        return '<div id="pagebottom"></div>\n</div>\n'        
    
    # Public functions #####################################################

    def header(self, d, **kw):
        """ Assemble page header
        
        Default behavior is to start a page div. Sub class and add
        footer items.
        
        @param d: parameter dictionary
        @rtype: string
        @return: page header html
        """
        return self.startPage()
    
    editorheader = header
        
    def footer(self, d, **keywords):
        """ Assemble page footer
        
        Default behavior is to end page div. Sub class and add
        footer items.

        @param d: parameter dictionary
        @keyword ...:...
        @rtype: string
        @return: page footer html
        """
        return self.endPage()

    # RecentChanges ######################################################

    def recentchanges_entry(self, d):
        """
        Assemble a single recentchanges entry (table row)
        
        @param d: parameter dictionary
        @rtype: string
        @return: recentchanges entry html
        """
        _ = self.request.getText
        html = []
        html.append('<tr>\n')
        
        html.append('<td class="rcicon1">%(icon_html)s</td>\n' % d)
        
        html.append('<td class="rcpagelink">%(pagelink_html)s</td>\n' % d)
        
        html.append('<td class="rctime">')
        if d['time_html']:
            html.append("%(time_html)s" % d)
        html.append('</td>\n')

        html.append('<td class="rcicon2">%(info_html)s</td>\n' % d)
        
        html.append('<td class="rceditor">')
        if d['editors']:
            html.append('<br>'.join(d['editors']))
        html.append('</td>\n')
            
        html.append('<td class="rccomment">')
        if d['comments']:
            if d['changecount'] > 1:
                notfirst = 0
                for comment in d['comments']:
                    html.append('%s<tt>#%02d</tt>&nbsp;%s' % (
                        notfirst and '<br>' or '' , comment[0], comment[1]))
                    notfirst = 1
            else:
                comment = d['comments'][0]
                html.append('%s' % comment[1])
        html.append('</td>\n')
           
        html.append('</tr>\n')
        
        return ''.join(html)
    
    def recentchanges_daybreak(self, d):
        """
        Assemble a rc daybreak indication (table row)
        
        @param d: parameter dictionary
        @rtype: string
        @return: recentchanges daybreak html
        """
        if d['bookmark_link_html']:
            set_bm = '&nbsp; %(bookmark_link_html)s' % d
        else:
            set_bm = ''
        return ('<tr class="rcdaybreak"><td colspan="%d">'
                '<strong>%s</strong>'
                '%s'
                '</td></tr>\n') % (6, d['date'], set_bm)

    def recentchanges_header(self, d):
        """
        Assemble the recentchanges header (intro + open table)
        
        @param d: parameter dictionary
        @rtype: string
        @return: recentchanges header html
        """
        _ = self.request.getText
        
        # Should use user interface language and direction
        html = '<div class="recentchanges"%s>\n' % self.ui_lang_attr()
        html += '<div>\n'
        if self.shouldUseRSS():
            link = [
                u'<div class="rcrss">',
                u'<a href="%s">' % self.rsshref(),
                self.make_icon("rss"),
                u'</a>',
                u'</div>',
                ]
            html += ''.join(link)
        html += '<p>'
        # Add day selector
        if d['rc_days']:
            days = []
            for day in d['rc_days']:
                if day == d['rc_max_days']:
                    days.append('<strong>%d</strong>' % day)
                else:
                    days.append(
                        wikiutil.link_tag(self.request,
                            '%s?max_days=%d' % (d['q_page_name'], day),
                            str(day)))
            days = ' | '.join(days)
            html += (_("Show %s days.") % (days,))
        
        if d['rc_update_bookmark']:
            html += " %(rc_update_bookmark)s %(rc_curr_bookmark)s" % d

        html += '</p>\n</div>\n'

        html += '<table>\n'
        return html

    def recentchanges_footer(self, d):
        """
        Assemble the recentchanges footer (close table)
        
        @param d: parameter dictionary
        @rtype: string
        @return: recentchanges footer html
        """
        _ = self.request.getText
        html = ''
        html += '</table>\n'
        if d['rc_msg']:
            html += "<br>%(rc_msg)s\n" % d
        html += '</div>\n'
        return html

    # Language stuff ####################################################
    
    def ui_lang_attr(self):
        """Generate language attributes for user interface elements

        User interface elements use the user language (if any), kept in
        request.lang.

        @rtype: string
        @return: lang and dir html attributes
        """
        lang = self.request.lang
        return ' lang="%s" dir="%s"' % (lang, i18n.getDirection(lang))

    def content_lang_attr(self):
        """Generate language attributes for wiki page content

        Page content uses the page language or the wiki default language.

        @rtype: string
        @return: lang and dir html attributes
        """
        lang = self.request.content_lang
        return ' lang="%s" dir="%s"' % (lang, i18n.getDirection(lang))

    # stuff moved from request.py
    def send_closing_html(self):
        """ generate timing info html and closing html tag """
        request = self.request

        # as this is the last chance to emit some html, we stop the clocks:
        request.clock.stop('run')
        request.clock.stop('total')

        # Close html code
        if not request.no_closing_html_code:
            if (request.cfg.show_timings and
                request.form.get('action', [None])[0] != 'print'):
                request.write('<ul id="timings">\n')
                for t in request.clock.dump():
                    request.write('<li>%s</li>\n' % t)
                request.write('</ul>\n')
            #request.write('<!-- auth_method == %s -->' % repr(request.user.auth_method))
            request.write('</body>\n</html>\n\n')

    # stuff from wikiutil.py
    def send_title(self, text, **keywords):
        """
        Output the page header (and title).

        TODO: check all code that call us and add page keyword for the
        current page being rendered.
        
        @param text: the title text
        @keyword link: URL for the title
        @keyword msg: additional message (after saving)
        @keyword pagename: 'PageName'
        @keyword page: the page instance that called us.
        @keyword print_mode: 1 (or 0)
        @keyword editor_mode: 1 (or 0)
        @keyword media: css media type, defaults to 'screen'
        @keyword allow_doubleclick: 1 (or 0)
        @keyword html_head: additional <head> code
        @keyword body_attr: additional <body> attributes
        @keyword body_onload: additional "onload" JavaScript code
        """
        request = self.request
        _ = request.getText
        
        if keywords.has_key('page'):
            page = keywords['page']
            pagename = page.page_name
        else:
            pagename = keywords.get('pagename', '')
            page = Page(request, pagename)
        
        scriptname = request.getScriptname()
        pagename_quoted = wikiutil.quoteWikinameURL(pagename)

        # get name of system pages
        page_front_page = wikiutil.getFrontPage(request).page_name
        page_help_contents = wikiutil.getSysPage(request, 'HelpContents').page_name
        page_title_index = wikiutil.getSysPage(request, 'TitleIndex').page_name
        page_site_navigation = wikiutil.getSysPage(request, 'SiteNavigation').page_name
        page_word_index = wikiutil.getSysPage(request, 'WordIndex').page_name
        page_user_prefs = wikiutil.getSysPage(request, 'UserPreferences').page_name
        page_help_formatting = wikiutil.getSysPage(request, 'HelpOnFormatting').page_name
        page_find_page = wikiutil.getSysPage(request, 'FindPage').page_name
        home_page = wikiutil.getInterwikiHomePage(request) # XXX sorry theme API change!!! Either None or tuple (wikiname,pagename) now.
        page_parent_page = getattr(page.getParentPage(), 'page_name', None)
        
        # Prepare the HTML <head> element
        user_head = [request.cfg.html_head]

        # include charset information - needed for moin_dump or any other case
        # when reading the html without a web server
        user_head.append('''<meta http-equiv="Content-Type" content="text/html;charset=%s">\n''' % config.charset)

        meta_keywords = request.getPragma('keywords')
        meta_desc = request.getPragma('description')
        if meta_keywords:
            user_head.append('<meta name="keywords" content="%s">\n' % escape(meta_keywords, 1))
        if meta_desc:
            user_head.append('<meta name="description" content="%s">\n' % escape(meta_desc, 1))

        # search engine precautions / optimization:
        # if it is an action or edit/search, send query headers (noindex,nofollow):
        if request.query_string:
            user_head.append(request.cfg.html_head_queries)
        elif request.request_method == 'POST':
            user_head.append(request.cfg.html_head_posts)
        # if it is a special page, index it and follow the links - we do it
        # for the original, English pages as well as for (the possibly
        # modified) frontpage:
        elif pagename in [page_front_page, request.cfg.page_front_page,
                          page_title_index, 'TitleIndex',
                          page_find_page, 'FindPage',
                          page_site_navigation, 'SiteNavigation',
                          'RecentChanges',]:
            user_head.append(request.cfg.html_head_index)
        # if it is a normal page, index it, but do not follow the links, because
        # there are a lot of illegal links (like actions) or duplicates:
        else:
            user_head.append(request.cfg.html_head_normal)

        if keywords.has_key('pi_refresh') and keywords['pi_refresh']:
            user_head.append('<meta http-equiv="refresh" content="%(delay)d;URL=%(url)s">' % keywords['pi_refresh'])
        
        # output buffering increases latency but increases throughput as well
        output = []
        # later: <html xmlns=\"http://www.w3.org/1999/xhtml\">
        output.append("""\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
%s
%s
%s
""" % (
            ''.join(user_head),
            self.html_head({
                'page': page,
                'title': wikiutil.escape(text),
                'sitename': wikiutil.escape(request.cfg.html_pagetitle or request.cfg.sitename),
                'print_mode': keywords.get('print_mode', False),
                'media': keywords.get('media', 'screen'),
            }),
            keywords.get('html_head', ''),
        ))

        # Links
        output.append('<link rel="Start" href="%s/%s">\n' % (scriptname, wikiutil.quoteWikinameURL(page_front_page)))
        if pagename:
            output.append('<link rel="Alternate" title="%s" href="%s/%s?action=raw">\n' % (
                _('Wiki Markup'), scriptname, pagename_quoted,))
            output.append('<link rel="Alternate" media="print" title="%s" href="%s/%s?action=print">\n' % (
                _('Print View'), scriptname, pagename_quoted,))

            # !!! currently disabled due to Mozilla link prefetching, see
            # http://www.mozilla.org/projects/netlib/Link_Prefetching_FAQ.html
            #~ all_pages = request.getPageList()
            #~ if all_pages:
            #~     try:
            #~         pos = all_pages.index(pagename)
            #~     except ValueError:
            #~         # this shopuld never happend in theory, but let's be sure
            #~         pass
            #~     else:
            #~         request.write('<link rel="First" href="%s/%s">\n' % (request.getScriptname(), quoteWikinameURL(all_pages[0]))
            #~         if pos > 0:
            #~             request.write('<link rel="Previous" href="%s/%s">\n' % (request.getScriptname(), quoteWikinameURL(all_pages[pos-1])))
            #~         if pos+1 < len(all_pages):
            #~             request.write('<link rel="Next" href="%s/%s">\n' % (request.getScriptname(), quoteWikinameURL(all_pages[pos+1])))
            #~         request.write('<link rel="Last" href="%s/%s">\n' % (request.getScriptname(), quoteWikinameURL(all_pages[-1])))

            if page_parent_page:
                output.append('<link rel="Up" href="%s/%s">\n' % (scriptname, wikiutil.quoteWikinameURL(page_parent_page)))

        # write buffer because we call AttachFile
        request.write(''.join(output))
        output = []

        if pagename:
            from MoinMoin.action import AttachFile
            AttachFile.send_link_rel(request, pagename)

        output.extend([
            '<link rel="Search" href="%s/%s">\n' % (scriptname, wikiutil.quoteWikinameURL(page_find_page)),
            '<link rel="Index" href="%s/%s">\n' % (scriptname, wikiutil.quoteWikinameURL(page_title_index)),
            '<link rel="Glossary" href="%s/%s">\n' % (scriptname, wikiutil.quoteWikinameURL(page_word_index)),
            '<link rel="Help" href="%s/%s">\n' % (scriptname, wikiutil.quoteWikinameURL(page_help_formatting)),
                      ])
        
        output.append("</head>\n")
        request.write(''.join(output))
        output = []
        request.flush()

        # start the <body>
        bodyattr = []
        if keywords.has_key('body_attr'):
            bodyattr.append(' ')
            bodyattr.append(keywords['body_attr'])

        # Add doubleclick edit action
        if (pagename and keywords.get('allow_doubleclick', 0) and
            not keywords.get('print_mode', 0) and
            request.user.edit_on_doubleclick):
            if request.user.may.write(pagename): # separating this gains speed
                querystr = wikiutil.escape(makeQueryString({'action': 'edit'}))
                # TODO: remove escape=0 in 2.0
                url = page.url(request, querystr, escape=0)
                bodyattr.append(''' ondblclick="location.href='%s'" ''' % url)

        # Set body to the user interface language and direction
        bodyattr.append(' %s' % self.ui_lang_attr())
        
        body_onload = keywords.get('body_onload', '')
        if body_onload:
            bodyattr.append(''' onload="%s"''' % body_onload)
        output.append('\n<body%s>\n' % ''.join(bodyattr))

        # Output -----------------------------------------------------------

        # If in print mode, start page div and emit the title
        if keywords.get('print_mode', 0):
            d = {'title_text': text, 'title_link': None, 'page': page,}
            request.themedict = d
            output.append(self.startPage())
            output.append(self.interwiki(d))      
            output.append(self.title(d))      

        # In standard mode, emit theme.header
        else:
            # prepare dict for theme code:
            d = {
                'theme': self.name,
                'script_name': scriptname,
                'title_text': text,
                'title_link': keywords.get('link', ''),
                'logo_string': request.cfg.logo_string,
                'site_name': request.cfg.sitename,
                'page': page,
                'pagesize': pagename and page.size() or 0,
                'last_edit_info': pagename and page.lastEditInfo() or '',
                'page_name': pagename or '',
                'page_find_page': page_find_page,
                'page_front_page': page_front_page,
                'home_page': home_page,
                'page_help_contents': page_help_contents,
                'page_help_formatting': page_help_formatting,
                'page_parent_page': page_parent_page,
                'page_title_index': page_title_index,
                'page_word_index': page_word_index,
                'page_user_prefs': page_user_prefs,
                'user_name': request.user.name,
                'user_valid': request.user.valid,
                'user_prefs': (page_user_prefs, request.user.name)[request.user.valid],
                'msg': keywords.get('msg', ''),
                'trail': keywords.get('trail', None),
                # Discontinued keys, keep for a while for 3rd party theme developers
                'titlesearch': 'use self.searchform(d)',
                'textsearch': 'use self.searchform(d)',
                'navibar': ['use self.navibar(d)'],
                'available_actions': ['use self.request.availableActions(page)'],
            }

            # add quoted versions of pagenames
            newdict = {}
            for key in d:
                if key.startswith('page_'):
                    if not d[key] is None:
                        newdict['q_'+key] = wikiutil.quoteWikinameURL(d[key])
                    else:
                        newdict['q_'+key] = None
            d.update(newdict)
            request.themedict = d

            # now call the theming code to do the rendering
            if keywords.get('editor_mode', 0):
                output.append(self.editorheader(d))
            else:
                output.append(self.header(d))
        
        # emit it
        request.write(''.join(output))
        output = []
        request.flush()

    def send_footer(self, pagename, **keywords):
        """
        Output the page footer.

        @param pagename: WikiName of the page
        @keyword print_mode: true, when page is displayed in Print mode
        """
        request = self.request
        d = request.themedict

        # Emit end of page in print mode, or complete footer in standard mode
        if keywords.get('print_mode', 0):
            request.write(self.pageinfo(d['page']))
            request.write(self.endPage())
        else:
            request.write(self.footer(d, **keywords))


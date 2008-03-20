# -*- coding: iso-8859-1 -*-
"""
MoinMoin - page contents writer

    @copyright: 2007 MoinMoin:JohannesBerg
    @license: GNU GPL, see COPYING for details.
"""

import xmlrpclib
import sys

from MoinMoin.script import MoinScript
from MoinMoin.support.multicall import MultiCall

class PluginScript(MoinScript):
    """\
Purpose:
========
This tool allows you to edit a page with xmlrpc. It is more of a commented
example than an actual script.

Detailed Instructions:
======================
General syntax: moin [options] xmlrpc write [write-options]

[options] usually should be:
    --config-dir=/path/to/my/cfg/ --wiki-url=wiki.example.org/

[write-options] see below:
    0. To edit the page 'FrontPage' on '192.168.0.1' using the username
       'JohnSmith' and the password 'MyPass', changing the page contents
       to 'This will be the new contents of the page!'
       moin ... xmlrpc write 192.168.0.1 JohnSmith MyPass FrontPage
       This will be the new contents of the page!
       ^D
"""

    def __init__(self, argv, def_values):
        MoinScript.__init__(self, argv, def_values)
        self.argv = argv

    # script entrypoint
    def mainloop(self):
        # grab parameters
        url = self.argv[0]
        user = self.argv[1]
        passwd = self.argv[2]
        pagename = self.argv[3]

        # get auth token from server giving username/password
        s = xmlrpclib.ServerProxy(url)
        token = s.getAuthToken(user, passwd)

        if token == '':
            print 'Invalid username/password'
            return

        # Verify that the token is valid by using it
        # and checking that the result is 'SUCCESS'.
        # The token should be valid for 15 minutes.
        assert s.applyAuthToken(token) == 'SUCCESS'

        try:
            # read new page contents
            content = sys.stdin.read()

            # build a multicall object that
            mcall = MultiCall(s)
            # first applies the token and
            mcall.applyAuthToken(token)
            # then edits the page
            mcall.putPage(pagename, content)

            # now execute the multicall
            results = mcall()

            # everything should have worked
            # instead of the asserts you can have anything else
            # but you should definitely access all the results
            # once so that faults are checked and raised
            assert results[0] == 'SUCCESS'
            assert results[1] is True

        finally:
            # be nice to the server and clean up the token
            # regardless of what happened
            assert s.deleteAuthToken(token) == 'SUCCESS'


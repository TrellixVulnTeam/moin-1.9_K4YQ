# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - MoinMoin.wikiutil Tests

    @copyright: 2003-2004 by Juergen Hermann <jh@web.de>
    @license: GNU GPL, see COPYING for details.
"""

import py
import unittest # LEGACY UNITTEST, PLEASE DO NOT IMPORT unittest IN NEW TESTS, PLEASE CONSULT THE py.test DOCS
from MoinMoin import wikiutil


class TestSystemPagesGroup:
    def testSystemPagesGroupNotEmpty(self):
        assert self.request.dicts.members('SystemPagesGroup')

class TestSystemPage(unittest.TestCase):
    systemPages = (
        # First level, on SystemPagesGroup
        'SystemPagesInEnglishGroup',
        # Second level, on one of the pages above
        'RecentChanges',
        'TitleIndex',
        )
    notSystemPages = (
        'NoSuchPageYetAndWillNeverBe',
        )

    def testSystemPage(self):
        """wikiutil: good system page names accepted, bad rejected"""
        for name in self.systemPages:
            self.assert_(wikiutil.isSystemPage(self.request, name),
                '"%(name)s" is a system page' % locals())
        for name in self.notSystemPages:
            self.failIf(wikiutil.isSystemPage(self.request, name),
                '"%(name)s" is NOT a system page' % locals())


class TestTemplatePage(unittest.TestCase):
    good = (
        'aTemplate',
        'MyTemplate',
    )
    bad = (
        'Template',
        'ATemplate',
        'TemplateInFront',
        'xTemplateInFront',
        'XTemplateInFront',
    )

    # require default page_template_regex config
    def setUp(self):
        self.config = self.TestConfig(defaults=['page_template_regex'])
    def tearDown(self):
        self.config.restore()

    def testTemplatePage(self):
        """wikiutil: good template names accepted, bad rejected"""
        for name in self.good:
            self.assert_(wikiutil.isTemplatePage(self.request, name),
                '"%(name)s" is a valid template name' % locals())
        for name in self.bad:
            self.failIf(wikiutil.isTemplatePage(self.request, name),
                '"%(name)s" is NOT a valid template name' % locals())


class TestParmeterParser(unittest.TestCase):

    def testNoWantedArguments(self):
        args = ''
        argParser = wikiutil.ParameterParser('')
        self.arg_list, self.arg_dict = argParser.parse_parameters(args)
        result = len(self.arg_dict)
        expected = 0
        self.assert_(result == expected,
                     'Expected "%(expected)s" but got "%(result)s"' % locals())

    def testWantedArguments(self):
        test_args = ('',
                     'width=100',
                     'width=100, height=200', )

        argParser = wikiutil.ParameterParser("%(width)s%(height)s")
        for args in test_args:
            self.arg_list, self.arg_dict = argParser.parse_parameters(args)
            result = len(self.arg_dict)
            expected = 2
            self.assert_(result == expected,
                         'Expected "%(expected)s" but got "%(result)s"' % locals())

    def testTooMuchWantedArguments(self):
        py.test.skip("fails because of unfinished wikiutil.ParameterParser code crashing")
        args = 'width=100, height=200, alt=Example'
        argParser = wikiutil.ParameterParser("%(width)s%(height)s")
        self.arg_list, self.arg_dict = argParser.parse_parameters(args)
        result = len(self.arg_dict)
        expected = 2
        self.assert_(result == expected,
                     'Expected "%(expected)s" but got "%(result)s"' % locals())


# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members
# Copyright Manba Team

import calendar

from twisted.internet.defer import inlineCallbacks
from twisted.trial import unittest

import buildbot.status.web.change_hook as change_hook

from buildbot.test.fake.web import FakeRequest
from buildbot.test.util import compat


gitJsonPayload = """{
    "canon_url": "https://bitbucket.org",
    "commits": [
        {
            "author": "marcus",
            "branch": "master",
            "files": [
                {
                    "file": "somefile.py",
                    "type": "modified"
                }
            ],
            "message": "Added some more things to somefile.py",
            "node": "620ade18607a",
            "parents": [
                "702c70160afc"
            ],
            "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
            "raw_node": "620ade18607ac42d872b568bb92acaa9a28620e9",
            "revision": null,
            "size": -1,
            "timestamp": "2012-05-30 05:58:56",
            "utctimestamp": "2012-05-30 03:58:56+00:00"
        }
    ],
    "repository": {
        "absolute_url": "/marcus/project-x/",
        "fork": false,
        "is_private": true,
        "name": "Project X",
        "owner": "marcus",
        "scm": "git",
        "slug": "project-x",
        "website": "https://atlassian.com/"
    },
    "user": "marcus"
}"""

mercurialJsonPayload = """{
    "canon_url": "https://bitbucket.org",
    "commits": [
        {
            "author": "marcus",
            "branch": "master",
            "files": [
                {
                    "file": "somefile.py",
                    "type": "modified"
                }
            ],
            "message": "Added some more things to somefile.py",
            "node": "620ade18607a",
            "parents": [
                "702c70160afc"
            ],
            "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
            "raw_node": "620ade18607ac42d872b568bb92acaa9a28620e9",
            "revision": null,
            "size": -1,
            "timestamp": "2012-05-30 05:58:56",
            "utctimestamp": "2012-05-30 03:58:56+00:00"
        }
    ],
    "repository": {
        "absolute_url": "/marcus/project-x/",
        "fork": false,
        "is_private": true,
        "name": "Project X",
        "owner": "marcus",
        "scm": "hg",
        "slug": "project-x",
        "website": "https://atlassian.com/"
    },
    "user": "marcus"
}"""

gitJsonNoCommitsPayload = """{
    "canon_url": "https://bitbucket.org",
    "commits": [
    ],
    "repository": {
        "absolute_url": "/marcus/project-x/",
        "fork": false,
        "is_private": true,
        "name": "Project X",
        "owner": "marcus",
        "scm": "git",
        "slug": "project-x",
        "website": "https://atlassian.com/"
    },
    "user": "marcus"
}"""

mercurialJsonNoCommitsPayload = """{
    "canon_url": "https://bitbucket.org",
    "commits": [
    ],
    "repository": {
        "absolute_url": "/marcus/project-x/",
        "fork": false,
        "is_private": true,
        "name": "Project X",
        "owner": "marcus",
        "scm": "hg",
        "slug": "project-x",
        "website": "https://atlassian.com/"
    },
    "user": "marcus"
}"""


class TestChangeHookConfiguredWithBitbucketChange(unittest.TestCase):

    """Unit tests for BitBucket Change Hook
    """

    def setUp(self):
        self.change_hook = change_hook.ChangeHookResource(
            dialects={'bitbucket': True})

    @inlineCallbacks
    def testGitWithChange(self):
        change_dict = {'payload': [gitJsonPayload]}

        request = FakeRequest(change_dict)
        request.uri = '/change_hook/bitbucket'
        request.method = 'POST'

        yield request.test_render(self.change_hook)

        self.assertEqual(len(request.addedChanges), 1)
        commit = request.addedChanges[0]

        self.assertEqual(commit['files'], ['somefile.py'])
        self.assertEqual(
            commit['repository'], 'git@bitbucket.org:marcus/project-x.git')
        self.assertEqual(
            calendar.timegm(commit['when_timestamp'].utctimetuple()),
            1338350336
        )
        self.assertEqual(
            commit['author'], 'Marcus Bertrand <marcus@somedomain.com>')
        self.assertEqual(
            commit['revision'], '620ade18607ac42d872b568bb92acaa9a28620e9')
        self.assertEqual(
            commit['comments'], 'Added some more things to somefile.py')
        self.assertEqual(commit['branch'], 'master')
        self.assertEqual(
            commit['revlink'],
            'https://bitbucket.org/marcus/project-x/commits/'
            '620ade18607ac42d872b568bb92acaa9a28620e9'
        )

    @inlineCallbacks
    def testGitWithNoCommitsPayload(self):
        change_dict = {'payload': [gitJsonNoCommitsPayload]}

        request = FakeRequest(change_dict)
        request.uri = '/change_hook/bitbucket'
        request.method = 'POST'

        yield request.test_render(self.change_hook)

        self.assertEqual(len(request.addedChanges), 0)
        self.assertEqual(request.written, 'no changes found')

    @inlineCallbacks
    def testMercurialWithChange(self):
        change_dict = {'payload': [mercurialJsonPayload]}

        request = FakeRequest(change_dict)
        request.uri = '/change_hook/bitbucket'
        request.method = 'POST'

        yield request.test_render(self.change_hook)

        self.assertEqual(len(request.addedChanges), 1)
        commit = request.addedChanges[0]

        self.assertEqual(commit['files'], ['somefile.py'])
        self.assertEqual(
            commit['repository'], 'https://bitbucket.org/marcus/project-x/')
        self.assertEqual(
            calendar.timegm(commit['when_timestamp'].utctimetuple()),
            1338350336
        )
        self.assertEqual(
            commit['author'], 'Marcus Bertrand <marcus@somedomain.com>')
        self.assertEqual(
            commit['revision'], '620ade18607ac42d872b568bb92acaa9a28620e9')
        self.assertEqual(
            commit['comments'], 'Added some more things to somefile.py')
        self.assertEqual(commit['branch'], 'master')
        self.assertEqual(
            commit['revlink'],
            'https://bitbucket.org/marcus/project-x/commits/'
            '620ade18607ac42d872b568bb92acaa9a28620e9'
        )

    @inlineCallbacks
    def testMercurialWithNoCommitsPayload(self):
        change_dict = {'payload': [mercurialJsonNoCommitsPayload]}

        request = FakeRequest(change_dict)
        request.uri = '/change_hook/bitbucket'
        request.method = 'POST'

        yield request.test_render(self.change_hook)

        self.assertEqual(len(request.addedChanges), 0)
        self.assertEqual(request.written, 'no changes found')

    @inlineCallbacks
    @compat.usesFlushLoggedErrors
    def testWithNoJson(self):
        request = FakeRequest()
        request.uri = '/change_hook/bitbucket'
        request.method = 'POST'

        yield request.test_render(self.change_hook)
        self.assertEqual(len(request.addedChanges), 0)
        self.assertEqual(request.written, 'Error processing changes.')
        request.setResponseCode.assert_called_with(
            500, 'Error processing changes.')
        self.assertEqual(len(self.flushLoggedErrors()), 1)

    @inlineCallbacks
    def testGitWithChangeAndProject(self):
        change_dict = {
            'payload': [gitJsonPayload],
            'project': ['project-name']}

        request = FakeRequest(change_dict)
        request.uri = '/change_hook/bitbucket'
        request.method = 'POST'

        yield request.test_render(self.change_hook)

        self.assertEqual(len(request.addedChanges), 1)
        commit = request.addedChanges[0]

        self.assertEqual(commit['project'], 'project-name')

    @inlineCallbacks
    def testGitWithMultipleCommits(self):
        ## 3 commits, all on master
        ## * 2efbe72 (HEAD, origin/master, master) 3rd commit; pushing this and the first 2 <==
        ## * 2ebca08 2nd commit 
        ## * 38b7a54 initial commit 
        payload  = """{
            "repository": {
                "website": "",
                "fork": false,
                "name": "push_test",
                "scm": "git",
                "owner": "marcus",
                "absolute_url": "/marcus/project-x/",
                "slug": "push_test",
                "is_private": true
            },
            "truncated": false,
            "commits": [
                {
                    "node": "38b7a5407d93",
                    "files": [
                        {
                            "type": "added",
                            "file": "foo"
                        }
                    ],
                    "branches": [],
                    "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
                    "utctimestamp": "2015-03-09 11:33:42+00:00",
                    "author": "marcus",
                    "timestamp": "2015-03-09 12:33:42",
                    "raw_node": "38b7a5407d93087a789ba9c318ddc979e825e2a3",
                    "parents": [],
                    "branch": null,
                    "message": "initial commit\\n",
                    "revision": null,
                    "size": -1
                },
                {
                    "node": "2ebca08692b4",
                    "files": [
                        {
                            "type": "modified",
                            "file": "foo"
                        }
                    ],
                    "branches": [],
                    "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
                    "utctimestamp": "2015-03-09 11:34:14+00:00",
                    "author": "marcus",
                    "timestamp": "2015-03-09 12:34:14",
                    "raw_node": "2ebca08692b406f99cdf858539f72135c34cde43",
                    "parents": [
                        "38b7a5407d93"
                    ],
                    "branch": null,
                    "message": "2nd commit\\n",
                    "revision": null,
                    "size": -1
                },
                {
                    "node": "2efbe7294727",
                    "files": [
                        {
                            "type": "modified",
                            "file": "foo"
                        }
                    ],
                    "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
                    "utctimestamp": "2015-03-09 11:34:31+00:00",
                    "author": "marcus",
                    "timestamp": "2015-03-09 12:34:31",
                    "raw_node": "2efbe7294727a8db7a1fd1e54b14fe5a267e1175",
                    "parents": [
                        "2ebca08692b4"
                    ],
                    "branch": "master",
                    "message": "3rd commit; pushing this and the first 2\\n",
                    "revision": null,
                    "size": -1
                }
            ],
            "canon_url": "https://bitbucket.org",
            "user": "marcus"
        }"""


        change_dict = {
            'payload': [payload],
            'project': ['project-name']}

        request = FakeRequest(change_dict)
        request.uri = '/change_hook/bitbucket'
        request.method = 'POST'

        yield request.test_render(self.change_hook)
        self.assertEqual(len(request.addedChanges), 3)
        
        assertions = [
            {
                'revision': '38b7a5407d93087a789ba9c318ddc979e825e2a3',
                'branch': 'master'},
            {
                'revision': '2ebca08692b406f99cdf858539f72135c34cde43',
                'branch': 'master'},
            {
                'revision': '2efbe7294727a8db7a1fd1e54b14fe5a267e1175',
                'branch': 'master'},
        ]
        
        for ind in range(0, len(request.addedChanges)):
            commit = request.addedChanges[ind]
            assertion = assertions[ind]
            
            for key in assertion.keys():
                self.assertEqual(commit[key], assertion[key])

    @inlineCallbacks
    def testGitWithMultipleCommitsOnDifferentBranches(self):
        ## 2 new branches, branch2, branch3, pushed for the first time together
        ## * b1d2d2c (HEAD, origin/branch3, branch3) 2nd commit on branch3 <==
        ## * bf8ec28 1st commit on branch3
        ## | * 5054d21 (origin/branch2, branch2) 2nd commit on branch2 <==
        ## | * 2f12b0a 1st commit on branch2
        ## |/  
        ## * 8cc5191 (origin/new-branch, origin/master, new-branch, master) 2nd commit on new-branch; pushing
        ## * f671eff 1st commit on new-branch
        ## * 2efbe72 3rd commit; pushing this and the first 2
        ## * 2ebca08 2nd commit
        ## * 38b7a54 initial commit
        payload  = """{
            "repository": {
                "website": "",
                "fork": false,
                "name": "push_test",
                "scm": "git",
                "owner": "marcus",
                "absolute_url": "/marcus/project-x/",
                "slug": "push_test",
                "is_private": true
            },
            "truncated": false,
            "commits": [
                {
                    "node": "2f12b0a59135",
                    "files": [
                        {
                            "type": "modified",
                            "file": "foo"
                        }
                    ],
                    "branches": [],
                    "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
                    "utctimestamp": "2015-03-09 11:41:32+00:00",
                    "author": "marcus",
                    "timestamp": "2015-03-09 12:41:32",
                    "raw_node": "2f12b0a59135108f59d8181d7547ffe83a779a12",
                    "parents": [
                        "8cc519128142"
                    ],
                    "branch": null,
                    "message": "1st commit on branch2\\n",
                    "revision": null,
                    "size": -1
                },
                {
                    "node": "5054d2141dd9",
                    "files": [
                        {
                            "type": "modified",
                            "file": "foo"
                        }
                    ],
                    "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
                    "utctimestamp": "2015-03-09 11:42:00+00:00",
                    "author": "marcus",
                    "timestamp": "2015-03-09 12:42:00",
                    "raw_node": "5054d2141dd9320cecc3c7acf5910c01783bd379",
                    "parents": [
                        "2f12b0a59135"
                    ],
                    "branch": "branch2",
                    "message": "2nd commit on branch2\\n",
                    "revision": null,
                    "size": -1
                },
                {
                    "node": "bf8ec28661d9",
                    "files": [
                        {
                            "type": "modified",
                            "file": "foo"
                        }
                    ],
                    "branches": [],
                    "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
                    "utctimestamp": "2015-03-09 11:42:20+00:00",
                    "author": "marcus",
                    "timestamp": "2015-03-09 12:42:20",
                    "raw_node": "bf8ec28661d9247e22e986fbfae30823d9a671a3",
                    "parents": [
                        "8cc519128142"
                    ],
                    "branch": null,
                    "message": "1st commit on branch3\\n",
                    "revision": null,
                    "size": -1
                },
                {
                    "node": "b1d2d2c8e636",
                    "files": [
                        {
                            "type": "modified",
                            "file": "foo"
                        }
                    ],
                    "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
                    "utctimestamp": "2015-03-09 11:42:23+00:00",
                    "author": "marcus",
                    "timestamp": "2015-03-09 12:42:23",
                    "raw_node": "b1d2d2c8e636154fe1f0e2ee1820a64c4cd2fe24",
                    "parents": [
                        "bf8ec28661d9"
                    ],
                    "branch": "branch3",
                    "message": "2nd commit on branch3\\n",
                    "revision": null,
                    "size": -1
                }
            ],
            "canon_url": "https://bitbucket.org",
            "user": "marcus"
        }"""


        change_dict = {
            'payload': [payload],
            'project': ['project-name']}

        request = FakeRequest(change_dict)
        request.uri = '/change_hook/bitbucket'
        request.method = 'POST'

        yield request.test_render(self.change_hook)
        self.assertEqual(len(request.addedChanges), 4)
        
        assertions = [
            {
                'revision': '2f12b0a59135108f59d8181d7547ffe83a779a12',
                'branch': 'branch2'},
            {
                'revision': '5054d2141dd9320cecc3c7acf5910c01783bd379',
                'branch': 'branch2'},
            {
                'revision': 'bf8ec28661d9247e22e986fbfae30823d9a671a3',
                'branch': 'branch3'},
            {
                'revision': 'b1d2d2c8e636154fe1f0e2ee1820a64c4cd2fe24',
                'branch': 'branch3'},
        ]
        
        for ind in range(0, len(request.addedChanges)):
            commit = request.addedChanges[ind]
            assertion = assertions[ind]
            
            for key in assertion.keys():
                self.assertEqual(commit[key], assertion[key])

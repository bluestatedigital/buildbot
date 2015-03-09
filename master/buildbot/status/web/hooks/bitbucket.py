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
# Copyright 2013 (c) Mamba Team

try:
    import json
    assert json
except ImportError:
    import simplejson as json

from dateutil.parser import parse as dateparse

from twisted.python import log

## tease out branch names from commit.  only commit on tip of branch has a
## valid "branch" attribute. for each commit that *does* have a branch, fill
## in the branch name on all of its parents.
def populateBranches(commits):
    commit_order = [ c['node'] for c in commits ]
    commit_map = dict([ (c['node'], c) for c in commits ])
    
    # >>> pprint(commit_map)
    # {u'38b7a5407d93': {u'author': u'marcus',
    #                    u'branch': None,
    #                    u'branches': [],
    #                    u'files': [{u'file': u'foo', u'type': u'added'}],
    #                    u'message': u'initial commit\n',
    #                    u'node': u'38b7a5407d93',
    #                    u'parents': [],
    #                    u'raw_author': u'Marcus Bertrand <marcus@somedomain.com>',
    #                    u'raw_node': u'38b7a5407d93087a789ba9c318ddc979e825e2a3',
    #                    u'revision': None,
    #                    u'size': -1,
    #                    u'timestamp': u'2015-03-09 12:33:42',
    #                    u'utctimestamp': u'2015-03-09 11:33:42+00:00'},
    # u'2ebca08692b4': {u'author': u'marcus',
    #                    u'branch': None,
    #                    u'branches': [],
    #                    u'files': [{u'file': u'foo', u'type': u'modified'}],
    #                    u'message': u'2nd commit\n',
    #                    u'node': u'2ebca08692b4',
    #                    u'parents': [u'38b7a5407d93'],
    #                    u'raw_author': u'Marcus Bertrand <marcus@somedomain.com>',
    #                    u'raw_node': u'2ebca08692b406f99cdf858539f72135c34cde43',
    #                    u'revision': None,
    #                    u'size': -1,
    #                    u'timestamp': u'2015-03-09 12:34:14',
    #                    u'utctimestamp': u'2015-03-09 11:34:14+00:00'},
    #  u'2efbe7294727': {u'author': u'marcus',
    #                    u'branch': u'master',
    #                    u'files': [{u'file': u'foo', u'type': u'modified'}],
    #                    u'message': u'3rd commit; pushing this and the first 2\n',
    #                    u'node': u'2efbe7294727',
    #                    u'parents': [u'2ebca08692b4'],
    #                    u'raw_author': u'Marcus Bertrand <marcus@somedomain.com>',
    #                    u'raw_node': u'2efbe7294727a8db7a1fd1e54b14fe5a267e1175',
    #                    u'revision': None,
    #                    u'size': -1,
    #                    u'timestamp': u'2015-03-09 12:34:31',
    #                    u'utctimestamp': u'2015-03-09 11:34:31+00:00'}}

    def set_branch(node, branch_name):
        if not node in commit_map or commit_map[node]['branch']:
            return
        
        commit_map[node]['branch'] = branch_name
        
        for parent_node in commit_map[node]['parents']:
            set_branch(parent_node, branch_name)
    
    ## walk commits with a branch
    for tip in [ c for c in commit_map.values() if c['branch'] ]:
        branch_name = tip['branch']
        
        for parent_node in tip['parents']:
            set_branch(parent_node, branch_name)
    
    return [ commit_map[c] for c in commit_order ]

def getChanges(request, options=None):
    """Catch a POST request from BitBucket and start a build process

    Check the URL below if you require more information about payload
    https://confluence.atlassian.com/display/BITBUCKET/POST+hook+management

    :param request: the http request Twisted object
    :param options: additional options
    """

    payload = json.loads(request.args['payload'][0])
    repo_url = '%s%s' % (
        payload['canon_url'], payload['repository']['absolute_url'])
    project = request.args.get('project', [''])[0]
    
    ## https://confluence.atlassian.com/display/BITBUCKET/Clone+a+repository
    scm = payload['repository']['scm'] # git, hg
    
    ## repo url should match that of the associated step for use with a change
    ## filter.  The repo_url appears to be appropriate for an public hg repo,
    ## but won't work with a private git repo.
    if scm == "git":
        clone_url = 'git@bitbucket.org:%s.git' % payload['repository']['absolute_url'][1:-1]
    elif scm == "hg":
        clone_url = repo_url
    
    changes = []
    for commit in populateBranches(payload['commits']):
        changes.append({
            'author': commit['raw_author'],
            'files': [f['file'] for f in commit['files']],
            'comments': commit['message'],
            'revision': commit['raw_node'],
            'when_timestamp': dateparse(commit['utctimestamp']),
            'branch': commit['branch'],
            'revlink': '%scommits/%s' % (repo_url, commit['raw_node']),
            'repository': clone_url,
            'project': project
        })
        log.msg('New revision: %s' % (commit['node'],))

    log.msg('Received %s changes from bitbucket' % (len(changes),))
    return (changes, scm)

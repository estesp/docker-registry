# -*- coding: utf-8 -*-
import re

from . import toolkit
from .app import app
from .lib import config
from .lib import index
from .lib import mirroring
import flask

cfg = config.load()

# Enable the search index
INDEX = index.load(cfg.search_backend.lower())

RE_USER_AGENT = re.compile('([^\s/]+)/([^\s/]+)')


@app.route('/v1/search', methods=['GET'])
@mirroring.source_lookup(index_route=True, merge_results=True)
def get_search():
    # default to standard 64-bit linux, then check UA for
    # specific arch/os (if coming from a docker host)
    arch = 'amd64'
    os = 'linux'
    user_agent = flask.request.headers.get('user-agent', '')
    ua = dict(RE_USER_AGENT.findall(user_agent))
    if 'arch' in ua:
        arch = ua['arch']
    if 'os' in ua:
        os = ua['os']

    search_term = flask.request.args.get('q', '')
    results = INDEX.results(search_term=search_term, arch=arch, os=os)
    return toolkit.response({
        'query': search_term,
        'num_results': len(results),
        'results': results,
    })

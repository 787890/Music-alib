# -*- coding: utf-8 -*-

import aiohttp_jinja2 as aiohttp_jinja2
import jinja2
from aiohttp import web

from src.Enums import Source
from src.Filter import SongFilter
from src.engine.SearchEngineFactory import SearchEngineFactory

app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))


@aiohttp_jinja2.template('index.html')
async def index(request):
    return {
        'title': 'Search'
    }


@aiohttp_jinja2.template('query_result.html')
async def query(request):
    data = await request.post()
    q = data['query']
    min_bitrate = int(data['min_bitrate'])

    ret = []

    for source in Source:
        fltr = SongFilter(min_bitrate=min_bitrate)
        engine = SearchEngineFactory.get_search_engine(source)(q, song_filter=fltr)
        engine.search()
        ret.append(engine.get_search_result())

    return {
        'title': 'Search by query',
        'results': ret
    }


@aiohttp_jinja2.template('netease_result.html')
async def netease(request):
    return {
        'title': 'Search by NetEase',
    }


app.add_routes([
    web.get('/', index),
    web.post('/query', query),
    web.put('/netease', netease),
    ])


if __name__ == '__main__':
    web.run_app(app)

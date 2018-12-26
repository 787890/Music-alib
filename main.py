# -*- coding: utf-8 -*-

import asyncio
import aiohttp_jinja2 as aiohttp_jinja2
import jinja2
from aiohttp import web

from src.Enums import Source
from src.Filter import SongFilter
from src.engine.SearchEngineFactory import SearchEngineFactory

app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))


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

    fltr = SongFilter(min_bitrate=min_bitrate)
    engines = [SearchEngineFactory.get_search_engine(s)(q, song_filter=fltr) for s in Source]

    tasks = [e.search() for e in engines]
    await asyncio.gather(*tasks)

    ret = [e.get_search_result() for e in engines]

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
    web.post('/netease', netease),
])

app.add_routes([
    web.static('/static/icon', './static/icon')
])


if __name__ == '__main__':
    web.run_app(app)

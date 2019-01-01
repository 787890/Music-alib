# -*- coding: utf-8 -*-

import asyncio
# import random
import math

import aiohttp_jinja2 as aiohttp_jinja2
import jinja2
from aiohttp import web

from src.Enums import SourceEnum, QualityOrAccuracy, QualityToBitrateEnums
from src.Filter import SongFilter
from src.engine.SearchEngineFactory import SearchEngineFactory
from src import NeteaseMusicListParser
from src import Logger
from src.Recommender import Recommender

app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))
log = Logger.get_logger()


@aiohttp_jinja2.template('index.html')
async def index(request):
    return {
        'title': 'Search',
        'priorities': [k.name for k in QualityOrAccuracy],
        'qualities': [k.name for k in QualityToBitrateEnums]
    }


@aiohttp_jinja2.template('query_result.html')
async def query(request):
    data = await request.post()
    q = data['query']
    quality_query = data.getall('quality_query')

    fltr = SongFilter(qualities=[QualityToBitrateEnums.__getitem__(q) for q in quality_query])
    results = await __search(q, fltr)

    return {
        'title': 'Search by query',
        'results': results
    }


async def __search(q, fltr):
    engines = [SearchEngineFactory.get_search_engine(s)(q, song_filter=fltr) for s in SourceEnum]

    tasks = [e.search() for e in engines]
    await asyncio.gather(*tasks)

    return [e.get_search_result() for e in engines]


@aiohttp_jinja2.template('netease_result.html')
async def netease(request):
    data = await request.post()
    list_id = data['netease']
    quality_netease = data.getall('quality_netease')
    min_similarity = float(data['min_similarity'])
    priority = data['priority']

    fltr = SongFilter(
        qualities=[QualityToBitrateEnums.__getitem__(q) for q in quality_netease],
        min_similarity=min_similarity)
    search_queries = NeteaseMusicListParser.get_song_infos(list_id)
    total = search_queries.__len__()
    page_limit = 20
    total_page = math.ceil(total/page_limit)

    count_in_page, count_in_total, page_count = 1, 1, 1

    tasks = []
    search_results = []

    for q in search_queries:
        log.debug("[page (%d/%d)] coroutine %d start" % (page_count, total_page, count_in_page))

        tasks.append(__search(q, fltr))
        # rand = random.random()*3
        # tasks.append(__mock_search("[(%d/%d)] query: %s, time: %f" % (count_in_total, total, q, rand), rand))

        count_in_page += 1
        count_in_total += 1

        if count_in_page > page_limit or count_in_total > total:
            search_results = search_results + await asyncio.gather(*tasks)
            log.debug("[page (%d/%d)] end" % (page_count, total_page))
            await asyncio.sleep(1)

            # reset page
            tasks = []
            count_in_page = 1
            page_count += 1

    results = []

    for search_result in search_results:
        file_infos = []
        q = ''
        for source_search_result in search_result:
            q = source_search_result['query']
            if not source_search_result['files']:
                continue
            for file_info in source_search_result['files']:
                file_info['source'] = source_search_result['source']
                file_info['track_name'] = source_search_result['track_name']
                file_info['artists'] = source_search_result['artists']
                file_info['similarity_ratio'] = source_search_result['similarity_ratio']
                file_info['query'] = source_search_result['query']
                file_infos.append(file_info)
        if not file_infos:
            results.append({'query': q})
            continue

        log.debug(Logger.json_format(file_infos))
        r = Recommender(quality_or_accuracy=QualityOrAccuracy.__getitem__(priority))
        results.append(r.get_recommended(file_infos))

    return {
        'title': 'Search by NetEase',
        'results': results
    }


async def __mock_search(msg, delay=1):
    await asyncio.sleep(delay)
    log.debug(msg)

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

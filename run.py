# -*- coding: utf-8 -*-

from flask import Flask, request, render_template    # 記得要import render_template
from engine.SearchEngineFactory import SearchEngineFactory
from Enums import Source
from Filter import SongFilter

import json

app = Flask(__name__)


@app.route('/', methods=['GET'])
def getdata():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def submit():
    query = request.form.get('query')
    return __query_serach(query)


def __query_serach(query):
    ret = {}

    for source in Source:
        fltr = SongFilter(min_bitrate=320, min_similarity=0.5)
        engine = SearchEngineFactory().get_search_engine(source)(query, song_filter=fltr)
        engine.search()
        info = engine.get_search_result()
        if info:
            ret[engine.SOURCE_NAME] = info

    return json.dumps(ret, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)

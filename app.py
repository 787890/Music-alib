# -*- coding: utf-8 -*-

from flask import Flask, request, render_template    # 記得要import render_template
from src.engine.SearchEngineFactory import SearchEngineFactory
from src.Enums import Source
from src.Filter import SongFilter

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", title='Search')


@app.route('/query', methods=['POST'])
def query():
    q = request.form.get('query')
    min_bitrate = int(request.form.get('min_bitrate'))
    return render_template(
        "query_result.html",
        title="Search by query",
        results=__query_serach(q, min_bitrate))


@app.route('/netease', methods=['POST'])
def netease():
    return render_template(
        "netease_result.html",
        title="Search by NetEase")


def __query_serach(q, min_bitrate):
    ret = []

    for source in Source:
        fltr = SongFilter(min_bitrate=min_bitrate)
        engine = SearchEngineFactory.get_search_engine(source)(q, song_filter=fltr)
        engine.search()
        ret.append(engine.get_search_result())

    return ret


if __name__ == '__main__':
    app.run(debug=True)

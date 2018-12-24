# -*- coding: utf-8 -*-

from src import HttpRequest, Logger

log = Logger.get_logger()

# this service is unreliable, please set up your own netease music api
# ref: https://github.com/Binaryify/NeteaseCloudMusicApi
NETEASE_CLOUD_MUSIC_API = 'http://35.234.26.198:3000/playlist/detail'


# get song list info from NETEASE_CLOUD_MUSIC_API
# @https://github.com/Binaryify/NeteaseCloudMusicApi
# @param: list_id (int) - netease song list id
# @return: song_infos (list of dict) - track name & artist name
def get_song_infos(listid):
    song_infos = []

    log.info("Fetching Netease song list id %s..." % listid)

    payload = {'id': listid}
    response_data = HttpRequest.request('GET', NETEASE_CLOUD_MUSIC_API, payload)

    if ('playlist' not in response_data) or ('tracks' not in response_data['playlist']):
        log.error("CANNOT fetch song list info with id %s!" % listid)
        return song_infos

    tracks = response_data['playlist']['tracks']
    for track in tracks:
        tname = track['name']
        aname = []
        ars = track['ar']
        for ar in ars:
            aname.append(ar['name'])
        song_info = {'track_name': tname, 'artists': ' '.join(aname)}
        song_infos.append(song_info)

    log.info("Successfully fetching Netease song list id %s." % listid)
    log.info("Total song number: %d\n" % len(song_infos))

    return song_infos

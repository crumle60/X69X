'''
    Ultimate Whitecream
    Copyright (C) 2018 holisticdioxide

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re

import xbmcplugin
from resources.lib import utils

addon = utils.addon

header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Encoding': 'gzip',
          'Accept-Language': 'en-US,en;q=0.5'}

def create_header_for_source(source_id):
    hdr = dict(header)
    hdr['Cookie'] = 'defaultSourceID=' + str(source_id)
    return hdr

@utils.url_dispatcher.register('620')
def pl_main():
    utils.addDir('[COLOR hotpink]Categories[/COLOR]','https://porns.land/video-categories', 623, '', '')
    utils.addDir('[COLOR hotpink]Channels[/COLOR]','https://porns.land/video-channels', 624, '', '')
    utils.addDir('[COLOR hotpink]Search[/COLOR]','https://porns.land/search?q=', 625, '', '')
    pl_list('https://porns.land/recent-porns')


@utils.url_dispatcher.register('621', ['url'])
def pl_list(url):
    try:
        listhtml = utils.getHtml(url)
    except Exception as e:
        return None
    content = re.compile('<div id="content"(.*?)<footer>', re.DOTALL | re.IGNORECASE).findall(listhtml)[0]
    match = re.compile('<div class="images">.*?href="([^"]+)".*?data-original="([^"]+)".*?alt="([^"]+)".*?</i>([^<]+)<(.*?)</a>', re.DOTALL | re.IGNORECASE).findall(content)
    for video, img, name, duration, hd in match:
        hd = ' [COLOR orange]HD[/COLOR] ' if 'HD' in hd else ' '
        name = utils.cleantext(name) + hd + duration.strip()
        utils.addDownLink(name, video, 622, img, '')
    try:
        next_page = re.compile('<a href="([^"]+)" data-ci-pagination-page="([^"]+)" rel="next"', re.DOTALL | re.IGNORECASE).findall(content)[0]
        utils.addDir('Next Page (' + next_page[1] + ')' , next_page[0], 621, '')
    except:
        pass
    xbmcplugin.endOfDirectory(utils.addon_handle)

@utils.url_dispatcher.register('623', ['url']) 
def pl_cat(url):
    listhtml = utils.getHtml(url, 'https://porns.land/')
    match = re.compile('<div class="category".*?href="([^"]+)".*?data-original="([^"]+)".*?alt="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(listhtml)
    for catpage, img, name in match:
        name = utils.cleantext(name)
        utils.addDir(name, catpage, 621, img, 1)
    xbmcplugin.endOfDirectory(utils.addon_handle)

@utils.url_dispatcher.register('624', ['url']) 
def pl_channels(url):
    listhtml = utils.getHtml(url, 'https://porns.land/')
    match = re.compile('<div class="serie".*?href="([^"]+)".*?data-original="([^"]+)".*?<h2>([^<]+)<', re.DOTALL | re.IGNORECASE).findall(listhtml)
    for catpage, img, name in match:
        name = utils.cleantext(name)
        utils.addDir(name, catpage, 621, img, 1)
    xbmcplugin.endOfDirectory(utils.addon_handle)

@utils.url_dispatcher.register('625', ['url'], ['keyword'])
def pl_search(url, keyword=None):
    if not keyword:
        utils.searchDir(url, 625)
    else:
        title = keyword.replace(' ','+')
        url += title
        pl_list(url)

@utils.url_dispatcher.register('622', ['url', 'name'], ['download'])
def pl_play(url, name, download=None):
    vp = utils.VideoPlayer(name, download=download, regex='''src\s*=\s*["']([^'"]+)''')
    vp.progress.update(5, "", "Loading video page 1", "")
    response = utils.getHtml(url)
    video_players = re.compile('class="embed-sites"(.*?)class="video-detail"', re.DOTALL | re.IGNORECASE).findall(response)[0]
    source_ids = re.compile('changeDefaultSourceID[(](.?)[)]', re.DOTALL | re.IGNORECASE).findall(video_players)
    for idx, source_id in enumerate(source_ids):
        vp.progress.update( 5 + (15 * idx / len(source_ids)), "", "Loading video page {}".format(idx + 2), "" )
        response = utils.getHtml(url, hdr=create_header_for_source(source_id))
        video_players += re.compile('class="embed-sites"(.*?)class="video-detail"', re.DOTALL | re.IGNORECASE).findall(response)[0]
    vp.play_from_html(video_players)

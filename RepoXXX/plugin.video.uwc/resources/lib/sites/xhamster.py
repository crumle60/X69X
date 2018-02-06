'''
    Ultimate Whitecream
    Copyright (C) 2016 Whitecream, hdgdl
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

import urllib2
import os
import re
import sys

import xbmc
import xbmcplugin
import xbmcgui
from resources.lib import utils

cookie = {'Cookie': 'lang=en; search_video=%7B%22sort%22%3A%22da%22%2C%22duration%22%3A%22%22%2C%22channels%22%3A%22%3B0.1.2%22%2C%22quality%22%3A0%2C%22date%22%3A%22%22%7D;'}

header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Encoding': 'gzip, deflate, br',
       'Accept-Language': 'en-US,en;q=0.5'}

@utils.url_dispatcher.register('505')
def Main():
    utils.addDir('[COLOR hotpink]Categories - Straight[/COLOR]','https://xhamster.com/categories',508,'','')
    utils.addDir('[COLOR hotpink]Categories - Gay[/COLOR]','https://xhamster.com/gay/categories',508,'','')
    utils.addDir('[COLOR hotpink]Categories - Shemale[/COLOR]','https://xhamster.com/shemale/categories',508,'','')
    utils.addDir('[COLOR hotpink]Search[/COLOR]','https://xhamster.com/search.php?q=',509,'','')
    List('https://xhamster.com/')
    xbmcplugin.endOfDirectory(utils.addon_handle)

	
@utils.url_dispatcher.register('506', ['url'])
def List(url):
    try:
        response = utils.getHtml(url, '', header)
    except:
        return None
    match0 = re.compile('<head>(.*?)</head>.*?index-videos.*?>(.*?)<footer>', re.DOTALL | re.IGNORECASE).findall(response)
    header_block = match0[0][0]
    main_block = match0[0][1]
    match = re.compile('thumb-image-container" href="([^"]+)".*?<i class="thumb-image-container__icon([^>]+)>.*?src="([^"]+)".*?alt="([^"]+)".*?duration">([^<]+)</div', re.DOTALL | re.IGNORECASE).findall(main_block)
    for video, hd, img, name, length in match:
        hd = ' [COLOR orange]HD[/COLOR]' if 'hd' in hd else ''
        name = utils.cleantext(name) + hd + ' [COLOR hotpink]' + length + '[/COLOR]'
        utils.addDownLink(name, video, 507, img, '')
    try:
        next_page = re.compile('<link rel="next" href="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(header_block)[0]
        utils.addDir('Next Page', next_page, 506, '')
    except:
        pass
    xbmcplugin.endOfDirectory(utils.addon_handle)


@utils.url_dispatcher.register('507', ['url', 'name'], ['download'])
def Playvid(url, name, download=None):
    response = utils.getHtml(url)
    match = re.compile("file: '(http[^']+)", re.DOTALL | re.IGNORECASE).findall(response)
    if match:
        utils.playvid(match[0], name, download)
    else:
        utils.notify('Oh oh','Couldn\'t find a video')

@utils.url_dispatcher.register('508', ['url'])
def Categories(url):
    cathtml = utils.getHtml(url, '', header)
    match0 = re.compile('<div class="letter-blocks page">(.*?)<footer>', re.DOTALL | re.IGNORECASE).findall(cathtml)
    match = re.compile('<a href="(.+?)" >([^<]+)<').findall(match0[0])
    for url, name in match:
        utils.addDir(name, url, 506, '')
    xbmcplugin.endOfDirectory(utils.addon_handle)
    
@utils.url_dispatcher.register('509', ['url'], ['keyword'])
def Search(url, keyword=None):
    searchUrl = url
    xbmc.log("Search: " + searchUrl)
    if not keyword:
        utils.searchDir(url, 509)
    else:
        title = keyword.replace(' ','_')
        searchUrl = searchUrl + title
        xbmc.log("Search: " + searchUrl)
        List(searchUrl)

# -*- coding: UTF-8 -*-
#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Exodus
# Addon id: plugin.video.exodus
# Addon Provider: Exodus

import re,traceback,urllib,urlparse,json,base64,time

from resources.lib.modules import cleantitle
from resources.lib.modules import dom_parser2
from resources.lib.modules import client

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['movieshd.tv', 'movieshd.is', 'movieshd.watch', 'flixanity.is', 'flixanity.me','istream.is','flixanity.online','flixanity.cc','123movies.it']
        self.base_link = 'http://123movieser.com'
        self.search_link = '/watch/%s-%s-online-free-123movies.html'
        
    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            url = urlparse.urljoin(self.base_link, (self.search_link %(clean_title,year)))
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('Flixanity - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('Flixanity - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            clean_title = cleantitle.geturl(url['tvshowtitle'])+'-s%02d' % int(season)
            url = urlparse.urljoin(self.base_link, (self.search_link %(clean_title,url['year'])))
            r = client.request(url)
            r = dom_parser2.parse_dom(r, 'div', {'id': 'ip_episode'})
            r = [dom_parser2.parse_dom(i, 'a', req=['href']) for i in r if i]
            for i in r[0]:
                if i.content == 'Episode %s'%episode:
                    url = i.attrs['href']
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('Flixanity - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            
            r = client.request(url)
            quality = re.findall(">(\w+)<\/p",r)
            if quality[0] == "HD":
                quality = "720p"
            else:
                quality = "SD"
            r = dom_parser2.parse_dom(r, 'div', {'id': 'servers-list'})
            r = [dom_parser2.parse_dom(i, 'a', req=['href']) for i in r if i]

            for i in r[0]:
                url = {'url': i.attrs['href'], 'data-film': i.attrs['data-film'], 'data-server': i.attrs['data-server'], 'data-name' : i.attrs['data-name']}
                url = urllib.urlencode(url)
                sources.append({'source': i.content, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
            return sources
        except:
            failure = traceback.format_exc()
            log_utils.log('Flixanity - Exception: \n' + str(failure))
            return

    def resolve(self, url):
        try:
            urldata = urlparse.parse_qs(url)
            urldata = dict((i, urldata[i][0]) for i in urldata)
            post = {'ipplugins': 1,'ip_film': urldata['data-film'], 'ip_server': urldata['data-server'], 'ip_name': urldata['data-name'],'fix': "0"}
            p1 = client.request('http://123movieser.com/ip.file/swf/plugins/ipplugins.php', post=post, referer=urldata['url'], XHR=True)
            p1 = json.loads(p1)
            p2 = client.request('http://123movieser.com/ip.file/swf/ipplayer/ipplayer.php?u=%s&s=%s&n=0' %(p1['s'],urldata['data-server']))
            p2 = json.loads(p2)
            p3 = client.request('http://123movieser.com/ip.file/swf/ipplayer/api.php?hash=%s' %(p2['hash']))
            p3 = json.loads(p3)
            n = p3['status']
            if n == False:
                p2 = client.request('http://123movieser.com/ip.file/swf/ipplayer/ipplayer.php?u=%s&s=%s&n=1' %(p1['s'],urldata['data-server']))
                p2 = json.loads(p2)
            url =  "https:%s" %p2["data"].replace("\/","/")
            return url
        except:
            failure = traceback.format_exc()
            log_utils.log('Flixanity - Exception: \n' + str(failure))
            return
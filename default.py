import urllib,urllib2,re,xbmcplugin,xbmcgui

pluginhandle = int(sys.argv[1])

REMOTE_DBG = True 

# append pydev remote debugger
if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd
    # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)

##################GameOne.de Addon for xbmc##################################
#About:  This addon plays the episodes from the german tv series gameone    #
#Author: Bri                                                                #
#Email:  mail at briareos dot de                                            #
#Date:   2012-02-25                                                         #
#Known issues: In the current state it only plays the episodes from 102+    #
#############################################################################
def CATEGORIES():
        addDir('TV Folgen','http://gameone.de/tv',1,'http://assets.gameone.de/images/element_bg/logo-game-one.png')

def INDEX_TV(url):#mode1
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    match=re.compile('<a href="/tv/(.+?)" class="image_link"><img alt=".+?" src="(.+?)" /></a>\n<h5>\n<a href=\'.+?\' title=\'(.+?)\'>').findall(link)
    #Example: <a href="/tv/198" class="image_link"><img alt="640x" src="http://asset.gameone.de/gameone/assets/video_metas/teaser_images/000/630/323/big/640x.jpg?1329836184" /></a>
    #          <h5><a href="..." title="...">
    for ep,thumbnail,title in match:
        addLink(ep+' - '+title,'http://gameone.de/tv/'+ep,2,thumbnail)

def VIDEOLINKS_TV(url):#mode2
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    
    gameoneurl = "http://gameone.de/tv/"
    feedurl = "http://www.gameone.de/api/mrss/"
    episodeurl = "http://cdn.riptide-mtvn.com"
    episode = url.replace(gameoneurl,"")
    print "Folge: "+str(episode)
    match_feed = re.compile('SWFObject\("http://media.mtvnservices.com/(.+?)","embeddedPlayer"').findall(link)
    #Example: var so = new SWFObject("http://media.mtvnservices.com/mgid:gameone:video:mtvnn.com:tv_show-198","embeddedPlayer", "566", "424", "9.0.28.0", "#cccccc");
    feed = ''
    for feeds in match_feed: #there can be several feeds with same content so we go through all and pick the last one to work with
        feed = feeds
    print str(feed)
    #Now we can fetch the show feed quality selection with the following URL (for more information look at http://briareos.de: http://www.gameone.de/api/mrss/
    feed = feedurl + feed
    
    print str(feed)
    
    req = urllib2.Request(feed)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    
    #There are several links with different "start" and "end" values but i have not found out the differences they all show the same content nothing is skipped
    #So we take the one with start=0 and ignore the rest until there further changes
    match_media = re.compile('<media:content duration=\'.+?\' type=\'text/xml\' url=\'(.+?)\?start=0.+?\'></media:content>').findall(link)
    for media in match_media:
        match_rtmpselect = media
        print str(match_rtmpselect)
    req = urllib2.Request(match_rtmpselect)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    #Highest bitrate selection
    #_(\d{2,})\.mp4
    match_episode = re.compile('<src>(.+?)</src>').findall(link)
    episode_maxbitrate = ''
    for episode in match_episode:
        print str(episode)
        episode_maxbitrate = episode
    
    #Example: 'rtmp://cp8619.edgefcs.net/ondemand/riptide/r2/production/2012/02/21/29d51f926d76842cc9c88d8ac023be3e/mp4_640px_1296k_m31_seg0_642x360_1140000.mp4'
    #The rtmp stream URL contains the path for the real mp4 file
    episode_maxbitrate = episode_maxbitrate[episode_maxbitrate.find("/r2"):]
    print "Video: " + str(episode_maxbitrate)
    episode_maxbitrate = episodeurl + episode_maxbitrate
    #'http://cdn.riptide-mtvn.com'
    item = xbmcgui.ListItem(path=episode_maxbitrate)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def addLink(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty('IsPlayable', 'true')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
    return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
       
elif mode==1:
        print ""+url
        INDEX_TV(url)
        
elif mode==2:
        print ""+url
        VIDEOLINKS_TV(url)
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))

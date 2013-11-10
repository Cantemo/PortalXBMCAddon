import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import sys
import os.path
import urlparse
import urllib2
import base64
import simplejson
import CommonFunctions as common

def getThumbnail(item):
    uri = None
    try:
        uri = item['thumbnail_uri']
        if uri:
            if not uri.startswith("http"):
                uri = "http://" + HOST + uri
    except:
        xbmc.log("Failed getting thumbail for item %s" % item['id'])

    xbmc.log("Found uri " + uri)
    
    if uri:
        return uri
    else:
        return ICON


def showOverview():
    item = xbmcgui.ListItem(ADDON.getLocalizedString(201))
    xbmcplugin.addDirectoryItem(HANDLE, PATH + "?menu=searchlist", item, True)

#    item = xbmcgui.ListItem(ADDON.getLocalizedString(202))
#    xbmcplugin.addDirectoryItem(HANDLE, PATH + "?menu=savedsearched", item, True)

#    item = xbmcgui.ListItem(ADDON.getLocalizedString(203))
#    xbmcplugin.addDirectoryItem(HANDLE, PATH + "?menu=collections", item, True)

    xbmcplugin.endOfDirectory(HANDLE)

def getLatestSearchesPath():
    datapath = os.path.join(FS_PATH, "resources", "data")
    if not os.path.exists(datapath):
        os.mkdirs(datapath)
    return os.path.join(datapath, "lastsearches.json")

def saveLatestSearch(query):
    if query:
        latestSearches = getLatestSearches()
        if query in latestSearches:
            latestSearches.remove(query)
        latestSearches.insert(0, query)
        settings.setSetting("latest_searches", simplejson.dumps(latestSearches[0:9]))

def getLatestSearches():
    r = settings.getSetting("latest_searches")
    if r:
        return simplejson.loads(r)
    else:
        return []

def searchList():

    latest = getLatestSearches()

    for q in latest:
        item = xbmcgui.ListItem(q)
        xbmcplugin.addDirectoryItem(HANDLE, PATH + "?menu=search&query=" + q, item, True)
        

#    searches = settings.getSetting("searches")
#    if searches:
#        xbmc.log("SEARCHES:" + searches)
    
    item = xbmcgui.ListItem(ADDON.getLocalizedString(200))
    xbmcplugin.addDirectoryItem(HANDLE, PATH + "?menu=search", item, True)

    xbmcplugin.endOfDirectory(HANDLE)

def showResults(result):
    items = []
    if 'objects' in result:
        for p_item in result['objects']:
            item = xbmcgui.ListItem(unicode(p_item['title']), iconImage = getThumbnail(p_item))
            xbmcplugin.addDirectoryItem(HANDLE, PATH + "?item=" + p_item['id'], item, True)

    xbmcplugin.endOfDirectory(HANDLE)
 

def request(url):
    xbmc.log("CANTEMO: Getting url " + url)
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (USERNAME, PASSWORD)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    result = urllib2.urlopen(request).read()
    xbmc.log("CANTEMO: Result " + result)
    return simplejson.loads(result)

def playItem(itemid):
    baseurl = "http://%s" % HOST

    shapes_url = "%s/vs/item/%s/shape/" % (baseurl, itemid)
    
    resp = request(shapes_url)
    url = None

    auth_baseurl = "http://%s:%s@%s" % (USERNAME, PASSWORD, HOST)

    for o in resp:
        if 'name' in o and o['name'] == 'Original':
            url = auth_baseurl + o['download_uri']

    if url:
        li = xbmcgui.ListItem(itemid)
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.add(url=url, listitem=li)
        xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(playlist)

def search():
#    try:
        keyboard = xbmc.Keyboard('', ADDON.getLocalizedString(200))
        keyboard.doModal()
        if keyboard.isConfirmed():
            query = keyboard.getText()
            baseurl = "http://%s/API/v1/item/search/?searchquery=%s&crit_mediatypechooser=video" % (HOST, query)
            try:
                response = request(baseurl)
            except:
                response = []
    

            saveLatestSearch(query)

#            searches = settings.getSetting("searches")
#            xmbc.log("CANTEMO SEARCH: got setting" + searches)
#            if searches:
#                searches.append(query)
#            else:
#                searches = [query]
#            settings.setSetting("searches")
                
            showResults(response)
#    except:
#        xbmc.log("")
#        showResults([])


if __name__ == '__main__':
    xbmc.log("CANTEMO CALLED WITH: " + str(sys.argv))

    settings = xbmcaddon.Addon(id='plugin.video.cantemo.portal')

    FS_PATH = settings.getAddonInfo("path")

    xbmc.log("CANTEMO FS_PATH=" + FS_PATH)

    HOST = settings.getSetting("hostname")
    USERNAME = settings.getSetting("username")
    PASSWORD = settings.getSetting("user_password")

    ADDON = xbmcaddon.Addon()
    PATH = sys.argv[0]
    HANDLE = int(sys.argv[1])
    PARAMS = common.getParameters(sys.argv[2])


    if PARAMS.has_key('content_type'):
        content_type = PARAMS['content_type']
    else:
        content_type = None

    xbmc.log("CANTEMO PARAMS: " + str(PARAMS))

    ICON = os.path.join(ADDON.getAddonInfo('path'), 'icon.png')
    FANART = os.path.join(ADDON.getAddonInfo('path'), 'fanart.jpg')

    if not HOST:
        ADDON.openSettings()
    elif 'item' in PARAMS:
        playItem(PARAMS['item'])
    elif 'menu' in PARAMS:
        menu = PARAMS['menu']
        if menu == "searchlist":
            searchList()
        elif menu == "collection":
            pass
        elif menu == "savedseraches":
            pass
        elif menu=="search":
            search()
    else:
        searchList()

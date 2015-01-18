#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import bottle
import beaker.middleware
import urllib
import cStringIO

from bottle import route, redirect, post, run, request, hook, static_file, install, template
from bottle.ext import sqlite
from instagram import client, subscriptions

bottle.debug(True)

session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}

app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)

#plugin = sqlite.Plugin(dbfile='/path/to/file/test.db')
#app.install(plugin)

#@app.route('/show/:item')
#def show(item, db):
#    row = db.execute('SELECT * from items where name=?', item).fetchone()

#    if row:
#        return template('showitem', page=row)

#    return HTTPError(404, "Page not found")



CONFIG = {
    'client_id': '756dbfdfa85647faa31de8c59d72ed09',
    'client_secret': '7a5de0bb5f3b4edda84d60718d393f91',
    'redirect_uri': 'http://localhost:8515/oauth_callback'
}

bw_latitude = "40.6962141"
bw_longitude = "-73.9178114"

unauthenticated_api = client.InstagramAPI(**CONFIG)



@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']

def process_tag_update(update):
    print(update)

reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)


@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static/')


@route('/')
def home():
    try:
        url = unauthenticated_api.get_authorize_url(scope=["basic","likes","comments","relationships"])

        return '<body><a href="%s">Connect with Instagram</a>' % url
    except Exception as e:
        print(e)


@route('/shout')
def shout_home():
    access_token = request.session['access_token']

    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        tag_search, next_tag = api.tag_search(q="videohack")
        tag_recent_media, next = api.tag_recent_media(tag_name=tag_search[0].name)
        videos = []
        hashtags = []
        locations = []

        for media in tag_recent_media:
            print media

            if(media.type == 'video'):
                videos.append(media.get_link())
                hashtags.append(media.get_tags())
                locations.append(media.get_geo())
            else:
                print 'not video'

    except Exception as e:
        print(e)

    return template("shout/index",videos=videos,hashtags=hashtags,locations=locations)

def get_nav():
    nav_menu = ("<body><h1>Instagram Menu</h1>"
                "<ol>"
                    "<li><a href='/recent'>User Recent Media</a> Calls user_recent_media - Get a list of a user's most recent media</li>"
                    "<li><a href='/user_media_feed'>User Media Feed</a> Calls user_media_feed - Get the currently authenticated user's media feed uses pagination</li>"
                    "<li><a href='/location_recent_media'>Location Recent Media</a> Calls location_recent_media - Get a list of recent media at a given location, in this case, Bushwick</li>"
                    "<li><a href='/media_search'>Lat / Long Search</a></li>"
                    "<li><a href='/media_popular'>Popular Media</a> Calls media_popular - Get a list of the overall most popular media items</li>"
                    "<li><a href='/user_search'>User Search</a> Calls user_search - Search for users on instagram, by name or username</li>"
                    "<li><a href='/user_follows'>User Follows</a> Get the followers of @instagram uses pagination</li>"
                    "<li><a href='/location_search'>Location Search</a> Calls location_search - Search for a location by lat/lng</li>"
                    "<li><a href='/tag_search'>Tag Search</a></li>"
                "</ol>")

    return nav_menu


@route('/oauth_callback')
def on_callback():
    code = request.GET.get("code")

    if not code:
        return 'Missing code'

    try:
        access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)

        if not access_token:
            return 'Could not get access token'

        api = client.InstagramAPI(access_token=access_token)

        request.session['access_token'] = access_token

        print ("access token=" + access_token)
    except Exception as e:
        print(e)

    return get_nav()


@route('/recent')
def on_recent():
    content = "<h2>User Recent Media</h2>"
    access_token = request.session['access_token']

    if not access_token:
        return 'Missing Access Token'
    try:
        api = client.InstagramAPI(access_token=access_token)
        recent_media, next = api.user_recent_media()
        photos = []

        for media in recent_media:
            photos.append('<div style="float:left;">')

            if(media.type == 'video'):
                photos.append('<video controls width height="150"><source type="video/mp4" src="%s"/></video>' % (media.get_standard_resolution_url()))
            else:
                photos.append('<img src="%s"/>' % (media.get_low_resolution_url()))

            print(media)
            photos.append("<br/> <a href='/media_like/%s'>Like</a> <a href='/media_unlike/%s'>Un-Like</a> LikesCount=%s</div>" % (media.id, media.id, media.like_count))

        content += ''.join(photos)
    except Exception as e:
        print(e)

    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/media_like/<id>')
def media_like(id):
    access_token = request.session['access_token']
    api = client.InstagramAPI(access_token=access_token)
    api.like_media(media_id=id)
    redirect("/recent")


@route('/media_unlike/<id>')
def media_unlike(id):
    access_token = request.session['access_token']
    api = client.InstagramAPI(access_token=access_token)
    api.unlike_media(media_id=id)
    redirect("/recent")


@route('/user_media_feed')
def on_user_media_feed():
    access_token = request.session['access_token']
    content = "<h2>User Media Feed</h2>"

    if not access_token:
        return 'Missing Access Token'

    try:
        api = client.InstagramAPI(access_token=access_token)
        media_feed, next = api.user_media_feed()
        photos = []

        for media in media_feed:
            photos.append('<img src="%s"/>' % media.get_standard_resolution_url())

        counter = 1

        while next and counter < 3:
            media_feed, next = api.user_media_feed(with_next_url=next)

            for media in media_feed:
                photos.append('<img src="%s"/>' % media.get_standard_resolution_url())

            counter += 1
        content += ''.join(photos)
    except Exception as e:
        print(e)

    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/location_recent_media')
def location_recent_media():
    access_token = request.session['access_token']
    content = "<h2>Location Recent Media</h2>"

    if not access_token:
        return 'Missing Access Token'

    try:
        api = client.InstagramAPI(access_token=access_token)
        recent_media, next = api.location_recent_media(location_id=514276)
        photos = []

        for media in recent_media:
            photos.append('<img src="%s"/>' % media.get_standard_resolution_url())

        content += ''.join(photos)
    except Exception as e:
        print(e)

    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/media_search')
def media_search():
    access_token = request.session['access_token']
    content = "<h2>Media Search</h2>"

    if not access_token:
        return 'Missing Access Token'

    try:
        api = client.InstagramAPI(access_token=access_token)
        media_search = api.media_search(lat=bw_latitude, lng=bw_longitude, distance=1000)
        videos = []

        for media in media_search:
            # Fetch only actual videos
            if (media.get_standard_resolution_url().endswith(".mp4")):
                video_file = cStringIO.StringIO(urllib.urlopen(media.get_standard_resolution_url()).read())

                videos.append(video_file)
            else:
                continue

        content += '<br />'.join(videos)
    except Exception as e:
        print(e)

    return "%s %s <br />Remaining API Calls = %s/%s" % (get_nav(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/media_popular')
def media_popular():
    access_token = request.session['access_token']
    content = "<h2>Popular Media</h2>"

    if not access_token:
        return 'Missing Access Token'

    try:
        api = client.InstagramAPI(access_token=access_token)
        media_search = api.media_popular()
        photos = []

        for media in media_search:
            photos.append('<img src="%s"/>' % media.get_standard_resolution_url())

        content += ''.join(photos)
    except Exception as e:
        print(e)

    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/user_search')
def user_search():
    access_token = request.session['access_token']
    content = "<h2>User Search</h2>"

    if not access_token:
        return 'Missing Access Token'

    try:
        api = client.InstagramAPI(access_token=access_token)
        user_search = api.user_search(q="Instagram")
        users = []

        for user in user_search:
            users.append('<li><img src="%s">%s</li>' % (user.profile_picture, user.username))

        content += ''.join(users)
    except Exception as e:
        print(e)

    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/user_follows')
def user_follows():
    access_token = request.session['access_token']
    content = "<h2>User Follows</h2>"

    if not access_token:
        return 'Missing Access Token'

    try:
        api = client.InstagramAPI(access_token=access_token)

        # 25025320 is http://instagram.com/instagram
        user_follows, next = api.user_follows('25025320')
        users = []

        for user in user_follows:
            users.append('<li><img src="%s">%s</li>' % (user.profile_picture, user.username))

        while next:
            user_follows, next = api.user_follows(with_next_url=next)

            for user in user_follows:
                users.append('<li><img src="%s">%s</li>' % (user.profile_picture, user.username))

        content += ''.join(users)
    except Exception as e:
        print(e)

    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/location_search')
def location_search():
    access_token = request.session['access_token']
    content = "<h2>Location Search</h2>"

    if not access_token:
        return 'Missing Access Token'

    try:
        api = client.InstagramAPI(access_token=access_token)
        location_search = api.location_search(lat=bw_latitude, lng=bw_longitude, distance=1000)
        locations = []

        for location in location_search:
            locations.append('<li>%s <a href="https://www.google.com/maps/preview/@%s,%s,19z">Map</a> </li>' % (location.name, location.point.latitude, location.point.longitude))

        content += ''.join(locations)
    except Exception as e:
        print(e)

    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/tag_search')
def tag_search():
    access_token = request.session['access_token']
    content = "<h2>Tag Search</h2>"

    if not access_token:
        return 'Missing Access Token'

    try:
        api = client.InstagramAPI(access_token=access_token)
        tag_search, next_tag = api.tag_search(q="bushwick")
        tag_recent_media, next = api.tag_recent_media(tag_name=tag_search[0].name)

        ascii_photos = []

        for tag_media in tag_recent_media:
            # Fetch the actual image
            if (tag_media.get_standard_resolution_url().endswith(".mp4")):
                continue
            else:
                image_file = cStringIO.StringIO(urllib.urlopen(tag_media.get_standard_resolution_url()).read())

                ascii_photos.append(image_file)

        content += '<br/>'.join(ascii_photos)
    except Exception as e:
        print(e)

    return "%s %s <br/>Remaining API Calls = %s/%s" % (get_nav(), content, api.x_ratelimit_remaining, api.x_ratelimit)


@route('/realtime_callback')
@post('/realtime_callback')
def on_realtime_callback():
    mode = request.GET.get("hub.mode")
    challenge = request.GET.get("hub.challenge")
    verify_token = request.GET.get("hub.verify_token")

    if challenge:
        return challenge
    else:
        x_hub_signature = request.header.get('X-Hub-Signature')
        raw_response = request.body.read()

        try:
            reactor.process(CONFIG['client_secret'], raw_response, x_hub_signature)
        except subscriptions.SubscriptionVerifyError:
            print("Signature mismatch")

bottle.run(app=app, host='localhost', port=8515, reloader=True)

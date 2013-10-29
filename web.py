from flask import Flask, render_template, abort
import listsdotmd
import os
from dropbox.rest import ErrorResponse
from markdown2 import MarkdownError
import redis
from datetime import datetime as dt
import json


HEROKU = os.environ.get('HEROKU', False)

app = Flask(__name__)

if not HEROKU:
    app.debug = True
    r = redis.StrictRedis(host='localhost',
                          port=6379,
                          db=0)
else:
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    r = redis.from_url(redis_url)

DROPBOX_ACCESS_TOKEN = os.environ.get('DROPBOX_TOKEN')
DROPBOX_LIST_FOLDER = os.environ.get('DROPBOX_LIST_FOLDER')

# Dropbox date format
date_fmt = '%a, %d %b %Y %H:%M:%S +0000'

db_client = listsdotmd.connect_to_dropbox(
    token=DROPBOX_ACCESS_TOKEN)


@app.route('/')
def list_lists():
    """Displays a list of the lists contained in DROPBOX_LIST_FOLDER"""
    try:
        new_hash = listsdotmd.get_folder_hash(db_client, DROPBOX_LIST_FOLDER)
    except ErrorResponse:
        abort(404)
        app.logger.error("Couldn't get index hash from Dropbox")
    index_in_redis = r.get('index')
    if index_in_redis:
        index_in_redis = json.loads(index_in_redis)
    if not index_in_redis or 'hash' not in index_in_redis or (
        new_hash != index_in_redis['hash']):
        all_lists = listsdotmd.index_lists(db_client,
            DROPBOX_LIST_FOLDER)
        r.set('index', json.dumps({'data': all_lists, 'hash': new_hash}))
    else:
        all_lists = index_in_redis['data']
    return render_template('index.html', lists=all_lists)


@app.route('/<list_name>/')
def show_list(list_name):
    """Renders the markdown file corresponding to list_name"""
    list_path = os.path.join(DROPBOX_LIST_FOLDER,
        list_name + '.md')
    try:
        new_rev = listsdotmd.get_file_rev(db_client, list_path)
    except ErrorResponse:
        abort(404)
        app.logger.error("Couldn't get file rev for: %s", list_name)
    list_in_redis = r.get(list_name)
    if list_in_redis:
        list_in_redis = json.loads(list_in_redis)
    if not list_in_redis or 'rev' not in list_in_redis or (
        new_rev != list_in_redis['rev']):
        try:
            list_str = listsdotmd.load_list_as_string(db_client, list_path)
        except ErrorResponse:
            abort(404)
            app.logger.error("Couldn't load list from Dropbox: %s", list_name)
        r.set(list_name, json.dumps({'data': list_str, 'rev': new_rev}))
    else:
        list_str = list_in_redis['data']
        print "List %s loaded from redis" % list_name
    try:
        list_html = listsdotmd.convert_list_to_html(list_str)
    except MarkdownError:
        abort(404)
        app.logger.error("Couldn't convert markdown file to HTML: %s", list_name)
    return render_template('list.html', list_markup=list_html)


if __name__ == '__main__':
    app.run()

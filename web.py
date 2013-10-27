from flask import Flask, render_template, abort
import listsdotmd
import os
from dropbox.rest import ErrorResponse
from markdown2 import MarkdownError
import redis
from datetime import datetime as dt


HEROKU = os.environ.get('HEROKU', False)

app = Flask(__name__)

if not HEROKU:
    app.debug = True
    r = redis.StrictRedis(host='localhost',
                          port=6379,
                          db=0)

DROPBOX_ACCESS_TOKEN = os.environ.get('DROPBOX_TOKEN')
DROPBOX_LIST_FOLDER = os.environ.get('DROPBOX_LIST_FOLDER')

# Dropbox date format
date_fmt = '%a, %d %b %Y %H:%M:%S +0000'

db_client = listsdotmd.connect_to_dropbox(
    token=DROPBOX_ACCESS_TOKEN)


@app.route('/')
def list_lists():
    folder_info = r.get('index', None)
    folder_update_time = listsdotmd.last_update_time(db_client,
        DROPBOX_LIST_FOLDER)
    if folder_info and (
        dt.strptime(folder_info.last_update, date_fmt) >= dt.strptime(folder_update_time, date_fmt)):
        all_lists = folder_info.data
    else:
        all_lists = listsdotmd.index_lists(db_client,
            DROPBOX_LIST_FOLDER)
        r.set('index', {'data': all_lists, 'last_update': folder_update_time})
    return render_template('index.html', lists=all_lists)


@app.route('/<list_name>/')
def show_list(list_name):
    list_path = os.path.join(DROPBOX_LIST_FOLDER,
        list_name + '.md')
    list_info = r.get(list_name, None)
    try:
        list_update_time = listsdotmd.last_update_time(db_client, list_path)
    except ErrorResponse:
        abort(404)
    if list_info and (
        dt.strptime(list_info.last_update, date_fmt) >= dt.strptime(list_update_time, date_fmt)):
        list_str = list_info.data
    else:
        try:
            list_str = listsdotmd.load_list_as_string(db_client, list_path)
        except ErrorResponse:
            abort(404)
        r.set(list_name, {'data': list_str, 'last_update': list_update_time})
    try:
        list_html = listsdotmd.convert_list_to_html(list_str)
    except MarkdownError:
        abort(404)
    return render_template('list.html', list_markup=list_html)


if __name__ == '__main__':
    app.run()

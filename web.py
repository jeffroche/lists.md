from flask import Flask, render_template, abort
import listsdotmd
import os
from dropbox.rest import ErrorResponse
from markdown2 import MarkdownError


HEROKU = os.environ.get('DROPBOX_TOKEN', False)

app = Flask(__name__)

if not HEROKU:
    app.debug = True

DROPBOX_ACCESS_TOKEN = os.environ.get('DROPBOX_TOKEN')
DROPBOX_LIST_FOLDER = os.environ.get('DROPBOX_LIST_FOLDER')

db_client = listsdotmd.connect_to_dropbox(
    token=DROPBOX_ACCESS_TOKEN)


@app.route('/')
def list_lists():
    all_lists = listsdotmd.index_lists(db_client,
        DROPBOX_LIST_FOLDER)
    return render_template('index.html', lists=all_lists)


@app.route('/<list_name>/')
def show_list(list_name):
    list_path = os.path.join(DROPBOX_LIST_FOLDER,
        list_name + '.md')
    try:
        list_str = listsdotmd.load_list_as_string(db_client,
            list_path)
    except ErrorResponse:
        abort(404)
    try:
        list_html = listsdotmd.convert_list_to_html(list_str)
    except MarkdownError:
        abort(404)
    return render_template('list.html', list_markup=list_html)


if __name__ == '__main__':
    app.run()

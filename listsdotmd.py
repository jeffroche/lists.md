import os
import dropbox
import markdown2


DROPBOX_TOKEN = os.environ.get('DROPBOX_TOKEN', None)


def connect_to_dropbox(token=DROPBOX_TOKEN):
    """Returns an instance of DropboxClient"""
    return dropbox.client.DropboxClient(token)


def index_lists(dropbox_client, folder):
    """Returns list of .md files in folder"""
    folder_metadata = dropbox_client.metadata(folder)
    md_files = []
    for item in folder_metadata['contents']:
        if not item['is_dir']:
            file_path = item['path']
            base_file = os.path.basename(file_path)
            file_name, file_ext = os.path.splitext(base_file)
            if file_ext == '.md':
                md_files.append({
                    'path': file_path,
                    'name': file_name,
                    'updated': item['modified'],
                    })
    return md_files


def load_list_as_string(dropbox_client, list_path):
    """Returns the list file text
    If the file doesn't exist, Dropbox throws an _ Exception
    """
    f, metadata = dropbox_client.get_file_and_metadata(list_path)
    return f.read()


def convert_list_to_html(list_text):
    """Returns the HTML of the markdown list
    markdown2 returns a _ exception if it fails
    """
    return markdown2.markdown(list_text)

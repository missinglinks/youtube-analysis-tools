import os
import sys
import requests
from .zip_archive import ZipArchive
from pyg.reader import YoutubeArchiveReader

def api_call(url):
    rsp = requests.get(url)
    return rsp.json()


def build_commenter_dataset(archive_filepath, out_dir, filename):

    if not os.path.exists(archive_filepath):
        print("youtube archive {} does not exist".format(archive_filepath))
        sys.exit(1)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_filepath = os.path.join(out_dir, filename)
    out_archive = ZipArchive(out_filepath)

    archive = YoutubeArchiveReader(archive_filepath)
    user_ids = set()
    for video in archive:
        user_ids.update([ c["author_id"] for c in video.comments ])

    print(len(user_ids))

    for i, user_id in enumerate(user_ids):
        print("{}/{}".format(i,len(user_ids)))

        filepath = "{}.json".format(user_id)
        if not out_archive.contains(filepath):

            metadata = api_call("http://localhost:5000/channel/{}".format(user_id))
            related_channels = api_call("http://localhost:5000/channel/{}/related".format(user_id))
            
            
            data = {
                "metadata": metadata,
                "related_channels": related_channels
            }
            out_archive.add(filepath, data)    
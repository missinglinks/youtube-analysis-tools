import requests
from .zip_archive import ZipArchive
from .config import YAC_BASE
from .helpers import slug_to_channel_id

MAX_ITER = 3

def slug_to_filename(slug):
    return "{}.json".format(slug.replace("/", "__"))

def filename_to_slug(filename):
    return filename.replace("__", "/").replace(".json", "")


class ChannelNetworkFetcher:

    def __init__(self, seeds, out_file, max_iter=MAX_ITER):
        self.seeds = seeds
        self.archive = ZipArchive(out_file)
        self.max_iter = max_iter

        self.fetch_channel_relations(seeds, 0)

    def fetch_channel_relations(self, slugs, iteration):

        if iteration == self.max_iter:
            return

        for slug in slugs:

            channel_id = slug_to_channel_id(slug)

            print(" ")
            print("{} fetch {}".format(iteration, slug))

            filename = slug_to_filename(slug)

            if not self.archive.contains(filename):
                url = YAC_BASE+"/channel/{}/related".format(channel_id)
                rsp = requests.get(url)
                channel = rsp.json()

                self.archive.add(filename, channel["data"])

                related_channels = channel["data"]["related_channels"]+channel["data"]["featured_channels"]+channel["data"]["subscribed_channels"]
                channel_slugs = [x[1] for x in related_channels]    
            else:
                channel = self.archive.get(filename)
                channel_list = channel["featured_channels"] + channel["related_channels"] + channel["subscribed_channels"]
                channel_slugs = [ x[1] for x in channel_list ]
            
            print("\t Related Channels: {}".format(len(channel_slugs)))
            self.fetch_channel_relations(list(set(channel_slugs)), iteration+1)

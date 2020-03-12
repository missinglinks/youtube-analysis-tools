import requests
import networkx as nx
from collections import Counter
from tqdm import tqdm
from .zip_archive import ZipArchive
from .config import YAC_BASE
from .helpers import slug_to_channel_id

def slug_to_filename(slug):
    return "{}.json".format(slug.replace("/", "__"))

def filename_to_slug(filename):
    return filename.replace("__", "/").replace(".json", "")

class ChannelNetworkDataset:

    def __init__(self, seeds, outpath, iterations):
        self.seeds = seeds
        self.archive = ZipArchive(outpath)
        self.max_iter = iterations

        self.fetch_channel_relations(seeds, 0)


    def fetch_related_videos(self, video_id):
        url = YAC_BASE+"/video/{}/related".format(video_id)
        done = []
        rel_videos= []
        for i in range(3):
            rsp = requests.get(url)

            videos = rsp.json()["related_videos"]
            for video in videos:
                if video["video_id"] not in done:
                    rel_videos.append(video)
                    done.append(video["video_id"])

        return rel_videos


    def fetch_channel_relations(self, seeds, iteration):

        if iteration == self.max_iter:
            return

        for seed in seeds:

            if seed:

                filename = "{}.json".format(seed)

                url = YAC_BASE+"/channel/{}".format(seed)
                rsp = requests.get(url)

                if not rsp.json()["data"]:
                    continue
                        

                channel_title = rsp.json()["data"]["snippet"]["title"]

                print("\t"*iteration+"fetch {}".format(channel_title))

                if not self.archive.contains(filename):
                    url = YAC_BASE+"/channel/{}/uploads".format(seed)
                    rsp = requests.get(url)
                    uploads = rsp.json()

                    rel_videos = []

                    for i, video in enumerate(uploads["uploads"][:30]):
                        print("\t"*iteration+"\tvideo {}".format(i))
                        video_id = video["snippet"]["resourceId"]["videoId"]

                        rel_videos += self.fetch_related_videos(video_id)
                    
                    rel_channels = set([x["channel_id"] for x in rel_videos])
                    
                    self.archive.add(filename, {
                        "channel_title": channel_title,
                        "channel_id": seed,
                        "related_videos": rel_videos,
                        "rel_channels": list(rel_channels)
                    })
                else:
                    data = self.archive.get(filename)
                    rel_channels = data["rel_channels"]

                self.fetch_channel_relations(rel_channels, iteration+1)


def build_network_file(archive, output):

    archive = ZipArchive(archive)

    g = nx.DiGraph()


    channel_ids = {}
    link_count = Counter()

    print("building network ...")
    for i, filename in tqdm(enumerate(archive)):
        channel_id = filename.replace(".json","")
        
        data = archive.get(filename)

        source = data["channel_title"]
        channel_ids[source] = channel_id


        for video in data["related_videos"]:
            target = video["channel"]
            channel_ids[target] = video["channel_id"]
            if source and target and source != target:    
                link_count.update([source+"<--->"+target])
                g.add_edge(source, target)        

    print("adding node and edge data ...")

    for node in g.nodes:
        try:
            g.nodes[node]["url"] = "https://www.youtube.com/channel/"+channel_ids[node]
        except:
            print("-> no channel id for: "+node)
            g.nodes[node]["url"] = ""

    for link, count in link_count.items():
        source, target = link.split("<--->")
        g[source][target]["weight"] = count


    print("writing graph file ...")
    nx.write_graphml(g, output)
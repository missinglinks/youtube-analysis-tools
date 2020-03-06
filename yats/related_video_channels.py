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

class RelatedVideoChannelsDataset:

    def __init__(self, seeds, outpath, iterations):
        self.seeds = seeds
        self.archive = ZipArchive(outpath)
        self.max_iter = iterations

        self.fetch_channel_relations(seeds)

    def fetch_related_videos(self, channel_title, video_id, iteration):
        if iteration == self.max_iter:
            return

        print("\t"*iteration + video_id)

        filename = "{}.json".format(video_id)

        if not self.archive.contains(filename):

            url = YAC_BASE+"/video/{}/related".format(video_id)
            rsp = requests.get(url)

            try:
                vids = rsp.json()["related_videos"]
            except:
                print(video_id)
                print(rsp.json())
                raise

            rel_videos = {
                "channel_title": channel_title,
                "related_videos": rsp.json()["related_videos"]
            }

            self.archive.add(filename, rel_videos)
        else:
            rel_videos = self.archive.get(filename)



        for video in rel_videos["related_videos"]:
            self.fetch_related_videos(
                video["channel"],
                video["video_id"],
                iteration+1
            )





    def fetch_channel_relations(self, seeds):

        for seed in seeds:


            url = YAC_BASE+"/channel/{}".format(seed)
            rsp = requests.get(url)
            channel_title = rsp.json()["data"]["snippet"]["title"]
            print(" ")
            print("fetch {}".format(channel_title))

        
            url = YAC_BASE+"/channel/{}/uploads".format(seed)
            rsp = requests.get(url)
            uploads = rsp.json()

            for video in uploads["uploads"]:
                video_id = video["snippet"]["resourceId"]["videoId"]

                self.fetch_related_videos(channel_title, video_id, 0)



def build_network_file(archive, output):

    archive = ZipArchive(archive)

    g = nx.DiGraph()


    done_videos = set()
    video_count = Counter()
    link_count = Counter()

    print("building network ...")
    for i, filename in tqdm(enumerate(archive)):
        vid_id = filename.replace(".json","")
        
        data = archive.get(filename)

        source = data["channel_title"]

        if vid_id not in done_videos:
            video_count.update([source])
            done_videos.add(vid_id)

        for target_data in data["related_videos"]:
            target = target_data["channel"]
            if source and target:
                link_count.update([source+"<--->"+target])

                if target_data["video_id"] not in done_videos:
                    video_count.update([target])
                    done_videos.add(target_data["video_id"])

                g.add_edge(source, target)        

    print("adding node and edge data ...")
    for node, count in video_count.items():
        print(node, count)    
        g.nodes[node]["video_count"] = count
    
    max_count = max(link_count.values())
    for link, count in link_count.items():
        source, target = link.split("<--->")
        g[source][target]["weight"] = count/max_count



    print("writing graph file ...")
    nx.write_graphml(g, output)
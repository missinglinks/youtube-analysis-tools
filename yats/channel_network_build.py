import os
import networkx as nx
from .zip_archive import ZipArchive
from .helpers import slug_to_channel_id, fetch_channel_data



def _get_channel_id(channel_ids, slug):
    if slug not in channel_ids:
        channel_ids[slug] = slug_to_channel_id(slug)
    return channel_ids[slug]

def build_network(archive, output):

    archive = ZipArchive(archive)

    g = nx.DiGraph()

    titles = {}
    channel_ids = {}

    print("building network ...")
    for i, filename in enumerate(archive):
        print("\t", i)
        channel = archive.get(filename)

        source = _get_channel_id(channel_ids, channel["slug"])
        for target_data in channel["related_channels"]:
            target = _get_channel_id(channel_ids, target_data[1])
            type_ = "related"
            if source and target:
                g.add_edge(source, target, type=type_)
        for target_data in channel["featured_channels"]:
            target = _get_channel_id(channel_ids, target_data[1])
            type_ = "featured"
            if source and target:
                g.add_edge(source, target, type=type_)
        for target_data in channel["subscribed_channels"]:
            target = _get_channel_id(channel_ids, target_data[1])
            type_ = "subscribed"
            if source and target:
                g.add_edge(source, target, type=type_)
             

    print("fetching node data ...")
    for i, node in enumerate(g.nodes):
        print("{}/{}".format(i, len(g.nodes)))
        if node not in titles:
            try:
                channel_info = fetch_channel_data(node)
                channel_title = channel_info["snippet"]["title"]
                if channel_title:
                    titles[node] = channel_title
                else:
                    titles[node] = "no label"
            except: 
                print(" No channel info for {}".format(node))
                titles[node] = node
    
        g.node[node]["label"] = titles[node]
        #print(channel_info)

    print("writing graph file ...")
    nx.write_graphml(g, output)
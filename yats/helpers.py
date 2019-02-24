import requests
from .config import YAC_BASE

def slug_to_channel_id(slug):
    if slug.startswith("channel"):
        return slug.replace("channel/", "")
    rsp = requests.get(YAC_BASE+"/channelId?slug={}".format(slug))
    data = rsp.json()
    return data["channel_id"]

def fetch_channel_data(channel_id):
    rsp = requests.get(YAC_BASE+"/channel/{}".format(channel_id))
    data = rsp.json()
    return data["data"]
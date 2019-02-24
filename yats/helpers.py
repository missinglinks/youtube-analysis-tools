import requests
from .config import YAC_BASE

def slug_to_channel_id(slug):
    rsp = requests.get(YAC_BASE+"/channelId?slug={}".format(slug))
    data = rsp.json()
    return data["channel_id"]
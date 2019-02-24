import click
import os
from yats.channel_network_dataset import ChannelNetworkFetcher
from yats.channel_network_build import build_network

@click.group()
def channel_network():
    pass

@channel_network.command()
@click.option("--seed", "-s", multiple=True)
@click.option("--out_dir", "-o", default="data")
@click.option("--name", "-n", default="channel_network")
@click.option("--iterations", "-i", default=3)
def fetch(seed, out_dir, name, iterations):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_filepath = os.path.join(out_dir, name)
    print("start fetching")
    fetcher = ChannelNetworkFetcher(seed, out_filepath, iterations)
    print("finished fetching")

@channel_network.command()
@click.argument("dataset")
@click.option("--out_file", "-o", default="data/channel_network.graphml")
@click.option("--related/--no-related", default=True)
@click.option("--featured/--no-featured", default=True)
@click.option("--subscribed/--no-subscribed", default=True)
def build(dataset, out_file, related, featured, subscribed):
    build_network(dataset, out_file)

if __name__ == "__main__":
    channel_network()

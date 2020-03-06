import click
import os
from yats.related_video_channels import RelatedVideoChannelsDataset, build_network_file


network = click.Group()


@network.command()
@click.option("--seed", "-s", multiple=True)
@click.option("--out_dir", "-o", default="data")
@click.option("--name", "-n", default="channel_network.zip")
@click.option("--iterations", "-i", default=3)
def build_dataset(seed, out_dir, name, iterations):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_filepath = os.path.join(out_dir, name)
    print("start fetching")
    fetcher = RelatedVideoChannelsDataset(seed, out_filepath, iterations)
    print("finished fetching")

@network.command()
@click.argument("dataset")
@click.option("--out_file", "-o", default="data/channel_network.graphml")
def build_network(dataset, out_file):
    build_network_file(dataset, out_file)

if __name__ == '__main__':
    network()
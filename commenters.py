import click
import os

from yats.commenter_dataset import build_commenter_dataset


@click.command()
@click.option("--archive", "-a", multiple=True)
@click.option("--directory", "-d")
@click.option("--out_dir", "-o", default="data")
@click.option("--filename", "-f", default="commentor_dataset")
def build_dataset(archive, directory, out_dir, filename):
    if directory:
        files = os.listdir(directory)
        archive = [ os.path.join(directory, x) for x in files if x.endswith(".zip") ] 


    build_commenter_dataset(archive, out_dir, filename)

if __name__ == '__main__':
    build_dataset()
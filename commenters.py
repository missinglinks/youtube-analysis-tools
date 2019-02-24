import click

from yats.commenter_dataset import build_commenter_dataset


@click.command()
@click.argument("archive_filepath")
@click.option("--out_dir", "-o", default="data")
@click.option("--filename", "-f", default="commentor_dataset")
def build_dataset(archive_filepath, out_dir, filename):
    build_commenter_dataset(archive_filepath, out_dir, filename)

if __name__ == '__main__':
    build_dataset()
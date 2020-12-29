from fedora.mods import MODSScraper
from fedora.risearch import TuplesSearch
from iiif.manifest import Manifest
import argparse
import json


def cleanup_server_name(server_uri):
    if server_uri.endswith("/"):
        server_uri = server_uri[:-1]
    return server_uri.replace("/collections", "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Manifest from a UTK Book")
    parser.add_argument(
        "-b",
        "--book",
        dest="book_pid",
        help="Specify the pid of the book you want to base your manifest on.",
        required=True,
    )
    parser.add_argument(
        "-f",
        "--filename",
        dest="filename",
        help="Specify a filename. Defaults to manifest.json.",
        default="manifest.json",
    )
    parser.add_argument(
        "-s",
        "--server",
        dest="server",
        help="Specify a server.  This is the value that will be used for harvesting metadata and writing id values in the manifest.",
        default="https://digital.lib.utk.edu",
    )
    args = parser.parse_args()
    book_pages = TuplesSearch(language="sparql").get_pages_and_page_numbers(
        args.book_pid
    )
    collection_pid = TuplesSearch(language="sparql").get_parent_collection(
        args.book_pid
    )
    metadata = MODSScraper(
        args.book_pid,
        islandora_frontend=f"{cleanup_server_name(args.server)}/collections/",
    ).build_iiif_descriptive_metadata()
    manifest_object = Manifest(
        metadata,
        book_pages,
        collection_pid,
        server_uri=cleanup_server_name(args.server),
    )
    with open(args.filename, "w") as manifest:
        manifest.write(json.dumps(manifest_object.manifest, indent=4))

from fedora.mods import MODSScraper
from fedora.risearch import TuplesSearch
from iiif.manifest import Manifest
import argparse
import json

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
    args = parser.parse_args()
    book_pages = TuplesSearch(language="sparql").get_pages_and_page_numbers(
        args.book_pid
    )
    collection_pid = TuplesSearch(language="sparql").get_parent_collection(
        args.book_pid
    )
    metadata = MODSScraper(args.book_pid).build_iiif_descriptive_metadata()
    manifest_object = Manifest(metadata, book_pages, collection_pid)
    with open(args.filename, "w") as manifest:
        manifest.write(json.dumps(manifest_object.manifest, indent=4))

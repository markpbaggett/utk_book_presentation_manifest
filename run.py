from fedora.mods import MODSScraper
from fedora.risearch import TuplesSearch
from iiif.manifest import Manifest
from iiif.presentation3 import Manifest3
import argparse
import json


def cleanup_server_name(server_uri):
    if server_uri.endswith("/"):
        server_uri = server_uri[:-1]
    return server_uri.replace("/collections", "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Manifest from a UTK Book")
    parser.add_argument(
        "-p",
        "--pid",
        dest="pid",
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
    parser.add_argument(
        "-r",
        "--risearch",
        dest="risearch",
        help="Specify the uri to your risearch interface.  Defaults to http://localhost:8080/fedora/risearch.",
        default="http://localhost:8080/fedora/risearch",
    )
    args = parser.parse_args()
    collection_and_model = TuplesSearch(
        language="sparql", ri_endpoint=args.risearch
    ).get_collection_and_content_model(args.pid)
    supported_content_models: ("islandora:bookCModel", "islandora:sp-audioCModel")
    if collection_and_model[1] == "islandora:bookCModel":
        book_pages = TuplesSearch(
            language="sparql", ri_endpoint=args.risearch
        ).get_pages_and_page_numbers(args.pid)
        metadata = MODSScraper(
            args.pid,
            islandora_frontend=f"{cleanup_server_name(args.server)}/collections/",
        ).build_iiif_descriptive_metadata_v2()
        manifest_object = Manifest(
            metadata,
            book_pages,
            collection_and_model[0],
            server_uri=f"{cleanup_server_name(args.server)}/",
        )
        with open(args.filename, "w") as manifest:
            manifest.write(json.dumps(manifest_object.manifest, indent=4))
    elif collection_and_model[1] == "islandora:sp-audioCModel":
        metadata = MODSScraper(
            args.pid,
            islandora_frontend=f"{cleanup_server_name(args.server)}/collections/",
        ).build_iiif_descriptive_metadata_v3()
        manifest_object = Manifest3(
            metadata, server_uri=f"{cleanup_server_name(args.server)}/"
        ).build_audio_manifest()
        with open(args.filename, "w") as manifest:
            manifest.write(manifest_object)
    else:
        raise Exception(
            f"Cannot generate manifests for {collection_and_model[1]} yet. Supported content models include: {supported_content_models}."
        )

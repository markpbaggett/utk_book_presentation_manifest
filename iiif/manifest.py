from uuid import uuid4
from tqdm import tqdm
import requests
import json


class Manifest:
    """A class to represent a IIIF manifest according to 2.1.1 specification.

    Note:  this class was initially inspired by the metadata generated by the Bodelian Manifest editor. Odd structural
    things that differ from the specification can be explained by this.
    """

    def __init__(
        self,
        descriptive_metadata,
        pages,
        collection_pid="",
        server_uri="https://digital.lib.utk.edu/",
        viewing_hint="paged",
        viewing_direction="left-to-right",
    ):
        self.identifier = f"http://{uuid4()}"
        self.label = descriptive_metadata["label"]
        self.related = (
            f'{server_uri}/collections/islandora/object/{descriptive_metadata["pid"]}'
        )
        self.description = descriptive_metadata["description"]
        self.license = descriptive_metadata["license"]
        self.attribution = descriptive_metadata["attribution"]
        self.metadata = descriptive_metadata["metadata"]
        self.navigation_date = self.__check_for_navigation_date(descriptive_metadata)
        self.collection = self.__process_within_value(collection_pid, server_uri)
        self.canvases = self.__get_canvases(pages, server_uri)
        self.viewing_hint = self.__validate_viewing_hint(viewing_hint)
        self.viewing_direction = self.__validate_viewing_direction(viewing_direction)
        self.manifest = self.__build_manifest()
        self.manifest_json = json.dumps(self.manifest, indent=4)

    def __build_manifest(self):
        manifest_metadata = {
            "@context": "http://iiif.io/api/presentation/2/context.json",
            "@id": self.identifier,
            "@type": "sc:Manifest",
            "label": self.label,
            "metadata": self.metadata,
            "description": [{"@value": self.description, "@language": "en"}],
            "license": self.license,
            "attribution": self.attribution,
            "related": {
                "@id": self.related,
                "format": "text/html",
            },
            "seeAlso": [
                {
                    "@id": f"{self.related}/datastream/MODS",
                    "format": "application/xml",
                    "profile": "http://www.loc.gov/standards/mods/v3/mods-3-5.xsd",
                },
                {
                    "@id": f"{self.related}/datastream/RELS-EXT",
                    "format": "application/rdf+xml",
                    "profile": "https://fedora.info/definitions/1/0/fedora-relsext-ontology.rdfs",
                },
            ],
            "sequences": [
                {
                    "@id": f"http://{uuid4()}",
                    "@type": "sc:Sequence",
                    "viewingHint": self.viewing_hint,
                    "viewingDirection": self.viewing_direction,
                    "label": [{"@value": "Normal Sequence", "@language": "en"}],
                    "canvases": self.canvases,
                }
            ],
            "structures": [],
            "thumbnail": self.__build_thumbnail_section(),
        }
        if self.navigation_date != "":
            manifest_metadata["navDate"] = self.navigation_date
        if self.collection != "":
            manifest_metadata["within"] = self.collection
        return manifest_metadata

    @staticmethod
    def __validate_viewing_hint(value):
        valid = ("individuals", "paged", "continuous")
        if value not in valid:
            raise Exception(
                f"{value} is not a valid viewingHint for manifests.  For more information, see: "
                f"https://iiif.io/api/presentation/2.1/#viewinghint"
            )
        else:
            return value

    @staticmethod
    def __validate_viewing_direction(value):
        valid = ("left-to-right", "right-to-left", "top-to-bottom", "bottom-to-top")
        if value not in valid:
            raise Exception(
                f"{value} is not a valid viewingDirection for sequences.  For more information, see: "
                f"https://iiif.io/api/presentation/2.1/#viewingdirection"
            )
        else:
            return value

    @staticmethod
    def __get_canvases(list_of_pages, server):
        return [
            Canvas(
                page[0],
                f"{server}iiif/2/collections%7Eislandora%7Eobject%7E{page[0]}%7Edatastream%7EJP2/info.json",
            ).build_canvas()
            for page in tqdm(list_of_pages)
        ]

    def __build_thumbnail_section(self):
        return {
            "@id": self.canvases[0]["images"][0]["resource"]["@id"].replace(
                "full/full", "full/,150"
            ),
            "service": {
                "@context": self.canvases[0]["images"][0]["resource"]["service"][
                    "@context"
                ],
                "@id": self.canvases[0]["images"][0]["resource"]["@id"].split(
                    "full/full"
                )[0],
                "profile": self.canvases[0]["images"][0]["resource"]["service"][
                    "profile"
                ][0],
            },
        }

    @staticmethod
    def __check_for_navigation_date(descriptive_metadata):
        if "navDate" in descriptive_metadata:
            return descriptive_metadata["navDate"]
        else:
            return ""

    @staticmethod
    def __process_within_value(value, server_details):
        if value != "":
            return f"{server_details}/collections/islandora/object/{value}"
        else:
            return ""


class Canvas:
    """A class to represent a IIIF Canvas according to the 2.1.1 presentation specification.

    Note:  this class was initially inspired by the metadata generated by the Bodelian Manifest editor. Odd structural
    things that differ from the specification can be explained by this.
    """

    def __init__(self, label, info_json):
        self.info = self.__read_info_json(info_json)
        self.identifier = f"http://{uuid4()}"
        self.label = label
        self.height = self.info["height"]
        self.width = self.info["width"]

    @staticmethod
    def __read_info_json(uri):
        return requests.get(uri).json()

    def __build_images(self):
        return {
            "@context": "http://iiif.io/api/presentation/2/context.json",
            "@id": f"http://{uuid4()}",
            "@type": "oa:Annotation",
            "motivation": "sc:painting",
            "resource": {
                "@id": f"{self.info['@id']}/full/full/0/default.jpg",
                "@type": "dctypes:Image",
                "format": "image/jpeg",
                "service": {
                    "@context": self.info["@context"],
                    "@id": self.info["@id"],
                    "profile": self.info["profile"],
                },
                "height": self.height,
                "width": self.width,
            },
            "on": self.identifier,
        }

    def build_canvas(self):
        """Method to generate a canvas for the canvases portion of sequences in a 2.1.1 Manifest."""
        return {
            "@id": self.identifier,
            "@type": "sc:Canvas",
            "label": self.label,
            "height": self.height,
            "width": self.width,
            "images": [self.__build_images()],
        }


if __name__ == "__main__":
    book = "agrtfhs:2275"
    book_pages = [
        ("agrtfhs:2279", 1),
        ("agrtfhs:2278", 2),
        ("agrtfhs:2291", 3),
        ("agrtfhs:2290", 4),
        ("agrtfhs:2289", 5),
        ("agrtfhs:2288", 6),
        ("agrtfhs:2287", 7),
        ("agrtfhs:2286", 8),
        ("agrtfhs:2285", 9),
        ("agrtfhs:2284", 10),
        ("agrtfhs:2283", 11),
        ("agrtfhs:2282", 12),
        ("agrtfhs:2281", 13),
        ("agrtfhs:2280", 14),
        ("agrtfhs:2277", 15),
        ("agrtfhs:2276", 16),
    ]
    within = "collections:agrtfhs"
    metadata = {
        "label": "Tennessee farm and home science, progress report 46, April - June 1963",
        "pid": "agrtfhs:2275",
        "description": "Quarterly newsletter from Knoxville, Tennessee, covering farming and home economics.",
        "license": "http://rightsstatements.org/vocab/NoC-US/1.0/",
        "attribution": "No Copyright - United States",
        "navDate": "1963-01-01T00:00:00Z",
        "metadata": [
            {
                "label": "Topics",
                "value": [
                    "Agriculture--Tennessee",
                    "Farm management",
                    "Livestock",
                    "Agricultural chemicals",
                    "Agricultural experiment stations",
                ],
            },
            {
                "label": "Table of Contents",
                "value": 'Examining beef cows for pregnancies - Personnel summary - Systemics increase wheat forage - Predict apple yields with leaf blade analysis? - Cows need a "milk break" - Growing corn on the plateau - Tests with phosphorus for pigs - Farm credit shifts, 1950 to 1962 - Costs of making whole-hog sausage - New bulletins',
            },
        ],
    }
    manifest_object = Manifest(metadata, book_pages, within)
    y = manifest_object.manifest
    j = json.dumps(y, indent=4)
    with open("sample_manifest.json", "w") as manifest:
        manifest.write(j)
    # print(manifest_object.build_thumbnail_section())

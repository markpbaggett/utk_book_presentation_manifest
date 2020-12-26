from uuid import uuid4
import requests
import json


class Manifest:
    def __init__(
        self,
        descriptive_metadata,
        pages,
        server_uri="https://digital.lib.utk.edu/",
        viewing_hint="paged",
    ):
        self.identifier = f"http://{uuid4()}"
        self.label = descriptive_metadata["label"]
        self.description = descriptive_metadata["description"]
        self.license = descriptive_metadata["license"]
        self.attribution = descriptive_metadata["attribution"]
        self.metadata = descriptive_metadata["metadata"]
        self.canvases = self.__get_canvases(pages, server_uri)
        self.viewing_hint = self.__validate_viewing_hint(viewing_hint)
        self.manifest = self.__build_manifest()
        self.manifest_json = json.dumps(self.manifest, indent=4)

    def __build_manifest(self):
        return {
            "@context": "http://iiif.io/api/presentation/2/context.json",
            "@id": self.identifier,
            "@type": "sc:Manifest",
            "label": self.label,
            "metadata": self.metadata,
            "description": [{"@value": self.description, "@language": "en"}],
            "license": self.license,
            "attribution": self.attribution,
            "sequences": [
                {
                    "@id": f"http://{uuid4()}",
                    "@type": "sc:Sequence",
                    "viewingHint": self.viewing_hint,
                    "label": [{"@value": "Normal Sequence", "@language": "en"}],
                    "canvases": self.canvases,
                }
            ],
            "structures": [],
            "thumbnail": self.__build_thumbnail_section(),
        }

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
    def __get_canvases(list_of_pages, server):
        return [
            Canvas(
                page[0],
                f"{server}iiif/2/collections%7Eislandora%7Eobject%7E{page[0]}%7Edatastream%7EJP2/info.json",
            ).build_canvas()
            for page in list_of_pages
        ]

    def __build_thumbnail_section(self):
        """
        @todo: Mirador doesn't display a thumbnail for some reason when this is set according to docs. What's expected?
        """
        return {
            "@id": self.canvases[0]["images"][0]["resource"]["@id"].replace(
                "full/full", "full/,150"
            ),
            "service": {
                "@context": self.canvases[0]["images"][0]["resource"]["service"][
                    "@context"
                ],
                "@id": f"http://{uuid4()}",
                "profile": self.canvases[0]["images"][0]["resource"]["service"][
                    "profile"
                ][0],
            },
        }


class Canvas:
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
    metadata = {
        "label": "Tennessee farm and home science, progress report 46, April - June 1963",
        "description": "Quarterly newsletter from Knoxville, Tennessee, covering farming and home economics.",
        "license": "http://rightsstatements.org/vocab/NoC-US/1.0/",
        "attribution": "No Copyright - United States",
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
    manifest_object = Manifest(metadata, book_pages)
    y = manifest_object.manifest
    j = json.dumps(y, indent=4)
    with open("sample_manifest.json", "w") as manifest:
        manifest.write(j)
    # print(manifest_object.build_thumbnail_section())

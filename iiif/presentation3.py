from fedora.mods import MODSScraper
from fedora.techmd import TechnicalMetadataScraper
import json
import requests


class Presentation3:
    def __init__(self, server, pid):
        self.server_uri = server
        self.pid = pid

    @staticmethod
    def __read_info_json(uri):
        return requests.get(uri).json()

    def generate_thumbnail(self):
        info = self.__read_info_json(
            f"{self.server_uri}iiif/2/collections%7Eislandora%7Eobject%7E{self.pid}%7Edatastream%7ETN/info.json"
        )
        return [
            {
                "id": f"{info['@id']}/full/full/1/default.png",
                "type": "Image",
                "format": "image/png",
                "height": info["sizes"][1]["height"],
                "width": info["sizes"][1]["width"],
            }
        ]


class Manifest3(Presentation3):
    def __init__(
        self,
        descriptive_metadata,
        server_uri="https://digital.lib.utk.edu/",
        id_prefix="https://raw.githubusercontent.com/utkdigitalinitiatives/utk_iiif_recipes/main/raw_manifests",
    ):
        self.id = f'{id_prefix}/{descriptive_metadata["pid"]}.json'
        self.id_prefix = id_prefix
        self.descriptive_metadata = descriptive_metadata
        self.server_uri = server_uri
        Presentation3.__init__(self, server_uri, self.descriptive_metadata["pid"])
        self.manifest = self.initialize_manifest()

    def initialize_manifest(self):
        initial_manifest = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": self.id,
            "type": "Manifest",
            "label": self.descriptive_metadata["label"],
            "rights": self.descriptive_metadata["rights"],
            "metadata": self.descriptive_metadata["metadata"],
            "thumbnail": self.generate_thumbnail(),
        }
        if "summary" in self.descriptive_metadata:
            initial_manifest["summary"] = self.descriptive_metadata["summary"]
        return initial_manifest

    def build_audio_manifest(self):
        self.manifest["items"] = [
            AudioCanvas(
                self.descriptive_metadata["pid"], self.server_uri, self.id_prefix
            ).build_canvas()
        ]
        return json.dumps(self.manifest, indent=4)


class AudioCanvas(Presentation3):
    def __init__(
        self,
        fedora_pid,
        server_uri="https://digital.lib.utk.edu/",
        id_prefix="https://raw.githubusercontent.com/utkdigitalinitiatives/utk_iiif_recipes/main/raw_manifests",
    ):
        self.id = f"{id_prefix}/{fedora_pid}/canvas"
        self.pid = fedora_pid
        self.audio_uri = f"{server_uri}/collections/islandora/object/{fedora_pid}/datastream/PROXY_MP3/view"
        Presentation3.__init__(self, server_uri, fedora_pid)
        self.duration = TechnicalMetadataScraper(self.pid).get_nlnz_duration()

    def build_canvas(self):
        return {
            "id": self.id,
            "type": "Canvas",
            "duration": self.duration,
            "thumbnail": self.generate_thumbnail(),
            "accompanyingCanvas": ImageCanvas(self.pid, "TN").build_canvas(),
            "items": [
                {
                    "id": f"{self.id}/page",
                    "type": "AnnotationPage",
                    "items": [
                        {
                            "id": f"{self.id}/page/annotation",
                            "type": "Annotation",
                            "motivation": "painting",
                            "body": {
                                "id": self.audio_uri,
                                "type": "Sound",
                                "format": "audio/mpeg",
                                "duration": self.duration,
                            },
                            "target": f"{self.id}/page",
                        }
                    ],
                }
            ],
        }


class ImageCanvas(Presentation3):
    """@todo: This was built originally for supporting accompanying canvases so this may need to be heavily overhauled for use by other canvas types.py

    Also, as far as I can tell Mirador doesn't actually support accompanyingCanvases.  Ask about this to IIIF community.
    """

    def __init__(
        self,
        fedora_pid,
        datastream="TN",
        server_uri="https://digital.lib.utk.edu/",
        id_prefix="https://raw.githubusercontent.com/utkdigitalinitiatives/utk_iiif_recipes/main/raw_manifests",
    ):
        self.id = f"{id_prefix}/{fedora_pid}/{datastream}/canvas"
        self.pid = fedora_pid
        self.datastream = datastream
        self.server = server_uri
        self.info = self.__get_info_json()
        self.height = self.info["height"]
        self.width = self.info["width"]
        Presentation3.__init__(self, server_uri, fedora_pid)

    def build_canvas(self):
        return {
            "id": self.id,
            "type": "Canvas",
            "label": self.__get_label(),
            "height": self.height,
            "width": self.width,
            "items": [self.__get_items()],
        }

    def __get_label(self):
        return {
            "en": [
                f"Image representing the {self.datastream} datastream for {self.pid} at {self.server}"
            ]
        }

    def __get_info_json(self):
        return requests.get(
            f"{self.server}iiif/2/collections~islandora~object~{self.pid}~datastream~{self.datastream}/info.json"
        ).json()

    def __get_items(self):
        return [
            {
                "id": f"{self.id}/canvas/annotation/page",
                "type": "AnnotationPage",
                "items": [
                    {
                        "id": f"{self.id}/canvas/annotation/image",
                        "type": "Annotation",
                        "motivation": "painting",
                        "body": {
                            "id": f"{self.server}iiif/2/collections~islandora~object~{self.pid}~datastream~{self.datastream}/full/full/0/default.png",
                            "type": "Image",
                            "format": "image/png",
                            "height": self.height,
                            "width": self.width,
                            "service": [
                                {
                                    "@id": self.info["@id"],
                                    "@type": "ImageService2",
                                    "profile": "http://iiif.io/api/image/2/level2.json",
                                }
                            ],
                        },
                        "target": f"{self.id}/canvas/annotation/page",
                    }
                ],
            }
        ]


if __name__ == "__main__":
    # x = MODSScraper("wwiioh:2001").build_iiif_descriptive_metadata_v3()
    # test = Manifest3(x).build_audio_manifest()
    # with open("sample_manifest.json", "w") as manifest:
    #     manifest.write(test)

    img = ImageCanvas("wwiioh:2001").build_canvas()
    print(json.dumps(img))

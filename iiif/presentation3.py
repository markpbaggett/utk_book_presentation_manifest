from fedora.mods import MODSScraper
from fedora.techmd import TechnicalMetadataScraper
import json


class Manifest3:
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
        self.manifest = self.initialize_manifest()

    def initialize_manifest(self):
        initial_manifest = {
            "@context": "http://iiif.io/api/presentation/3/context.json",
            "id": self.id,
            "type": "Manifest",
            "label": self.descriptive_metadata["label"],
            "rights": self.descriptive_metadata["rights"],
            "metadata": self.descriptive_metadata["metadata"],
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


class AudioCanvas:
    def __init__(
        self,
        fedora_pid,
        server_uri="https://digital.lib.utk.edu/",
        id_prefix="https://raw.githubusercontent.com/utkdigitalinitiatives/utk_iiif_recipes/main/raw_manifests",
    ):
        self.id = f"{id_prefix}/{fedora_pid}/canvas"
        self.pid = fedora_pid
        self.audio_uri = f"{server_uri}/collections/islandora/object/{fedora_pid}/datastream/PROXY_MP3/view"
        self.duration = TechnicalMetadataScraper(self.pid).get_nlnz_duration()

    def build_canvas(self):
        return {
            "id": self.id,
            "type": "Canvas",
            "duration": self.duration,
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


if __name__ == "__main__":
    x = MODSScraper("wwiioh:2001").build_iiif_descriptive_metadata_v3()
    test = Manifest3(x).build_audio_manifest()
    with open("sample_manifest.json", "w") as manifest:
        manifest.write(test)

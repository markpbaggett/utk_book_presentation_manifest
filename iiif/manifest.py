from uuid import uuid4
import requests


class Manifest:
    def __init__(self, viewing_hint: "paged"):
        self.identifier = f"http://{uuid4()}"
        self.viewing_hint = viewing_hint


class Canvas:
    def __init__(self, label, info_json, pid):
        self.info = self.__read_info_json(info_json)
        self.pid = pid
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
    sample_info_uri = (
        f"https://digital.lib.utk.edu/iiif/2/collections%7Eislandora%7Eobject%7E{book_pages[1][0]}"
        f"%7Edatastream%7EJP2/info.json"
    )
    x = Canvas(book_pages[1][0], sample_info_uri, book_pages[1][0])
    print(x.build_canvas())

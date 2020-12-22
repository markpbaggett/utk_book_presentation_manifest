from uuid import uuid4
import requests


class Manifest:
    def __init__(self, viewing_hint: "paged"):
        self.identifier = f"http://{uuid4()}"
        self.viewing_hint = viewing_hint


class Canvas:
    def __init__(self, label, info_json):
        self.identifier = f"http://{uuid4()}"
        self.label = label
        self.info = self.__read_info_json(info_json)

    @staticmethod
    def __read_info_json(uri):
        return requests.get(uri).json()


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
    x = Canvas(book_pages[1][0], sample_info_uri)
    print(x.info)

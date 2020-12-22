import requests
import xmltodict


class MODSScraper:
    def __init__(
        self, book_pid, islandora_frontend="https://digital.lib.utk.edu/collections/"
    ):
        self.mods_dict = self.__get_mods(
            f"{islandora_frontend}/islandora/object/{book_pid}/datastream/MODS"
        )
        self.label = self.get_title()

    @staticmethod
    def __get_mods(uri):
        r = requests.get(uri).content.decode("utf-8")
        return xmltodict.parse(r)

    def get_title(self):
        return self.mods_dict["mods"]["titleInfo"]["title"]


if __name__ == "__main__":
    x = MODSScraper("agrtfhs:2275")
    print(x.label)

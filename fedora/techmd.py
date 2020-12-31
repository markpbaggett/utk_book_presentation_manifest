import requests
import xmltodict


class TechnicalMetadataScraper:
    def __init__(
        self, fedora_pid, islandora_frontend="https://digital.lib.utk.edu/collections/"
    ):
        self.pid = fedora_pid
        self.tech_md = (
            f"{islandora_frontend}/islandora/object/{fedora_pid}/datastream/TECHMD"
        )
        self.tech_md_dict = self.__get_techmd(self.tech_md)

    @staticmethod
    def __get_techmd(uri):
        return xmltodict.parse(requests.get(uri).content.decode("utf-8"))

    def get_nlnz_duration(self):
        duration = [
            duration["#text"]
            for duration in self.tech_md_dict["fits"]["metadata"]["audio"]["duration"]
            if duration["@toolname"] == "NLNZ Metadata Extractor"
        ][0]
        duration_split = duration.split(":")
        hours = int(duration_split[0]) * 60 * 60
        minutes = int(duration_split[1]) * 60
        milliseconds = int(duration_split[3]) * 0.001
        return str(hours + minutes + int(duration_split[2]) + milliseconds)


if __name__ == "__main__":
    print(TechnicalMetadataScraper("wwiioh:2001").get_nlnz_duration())

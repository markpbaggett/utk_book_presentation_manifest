import requests


class ResourceIndexSearch:
    def __init__(self):
        self.risearch_endpoint = "http://localhost:8080/fedora/risearch"

    @staticmethod
    def escape_query(query):
        return (
            query.replace("*", "%2A")
            .replace(" ", "%20")
            .replace("<", "%3C")
            .replace(":", "%3A")
            .replace(">", "%3E")
            .replace("#", "%23")
        )


class TriplesSearch(ResourceIndexSearch):
    def __init__(self, language="spo", riformat="Turtle"):
        ResourceIndexSearch.__init__(self)
        self.language = self.__validate_language(language)
        self.format = self.__validate_format(riformat)
        self.base_url = (
            f"{self.risearch_endpoint}?type=triples"
            f"&lang={self.language}&format={self.format}"
        )

    @staticmethod
    def __validate_format(user_format):
        valid_formats = ("N-Triples", "Notation 3", "RDF/XML", "Turtle")
        if user_format in valid_formats:
            return user_format
        else:
            raise Exception(
                f"Supplied format is not valid: {user_format}. Must be one of {valid_formats}."
            )

    @staticmethod
    def __validate_language(language):
        valid_languages = ("spo", "itql", "sparql")
        if language in valid_languages:
            return language
        else:
            raise Exception(
                f"Supplied language is not valid: {language}. Must be one of {valid_languages}."
            )

    def get_pages_from_a_book(self, book_pid):
        if self.language != "spo":
            raise Exception(
                f"You must use spo as language for this method.  You used {self.language}."
            )
        spo_query = self.escape_query(
            f"* <info:fedora/fedora-system:def/relations-external#isMemberOf> <info:fedora/{book_pid}>"
        )
        r = requests.get(f"{self.base_url}&query={spo_query}")
        return r.content.decode("utf-8")


if __name__ == "__main__":
    x = TriplesSearch().get_pages_from_a_book("test:1")

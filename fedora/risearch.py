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
            .replace("\n", "")
            .replace("?", "%3F")
            .replace("{", "%7B")
            .replace("}", "%7D")
            .replace("/", "%2F")
        )

    def validate_language(self, language):
        if language in self.valid_languages:
            return language
        else:
            raise Exception(
                f"Supplied language is not valid: {language}. Must be one of {self.valid_languages}."
            )

    def validate_format(self, user_format):
        if user_format in self.valid_formats:
            return user_format
        else:
            raise Exception(
                f"Supplied format is not valid: {user_format}. Must be one of {self.valid_formats}."
            )


class TriplesSearch(ResourceIndexSearch):
    def __init__(self, language="spo", riformat="Turtle"):
        ResourceIndexSearch.__init__(self)
        self.valid_languages = ("spo", "itql", "sparql")
        self.valid_formats = ("N-Triples", "Notation 3", "RDF/XML", "Turtle")
        self.language = self.validate_language(language)
        self.format = self.validate_format(riformat)
        self.base_url = (
            f"{self.risearch_endpoint}?type=triples"
            f"&lang={self.language}&format={self.format}"
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

    def get_pages_and_page_numbers(self, book_pid):
        if self.language != "sparql":
            raise Exception(
                f"You must use sparql as the language for this method.  You used {self.language}."
            )
        sparql_query = self.escape_query(
            f"SELECT ?page ?pagenumber FROM <#ri> WHERE {{ ?page "
            f"<info:fedora/fedora-system:def/relations-external#isMemberOf> <info:fedora/{book_pid}>. ?page "
            f"<http://islandora.ca/ontology/relsext#isPageNumber> ?pagenumber. }} LIMIT 10"
        )
        return requests.get(f"{self.base_url}&query={sparql_query}").content.decode(
            "utf-8"
        )


class TuplesSearch(ResourceIndexSearch):
    def __init__(self, language="sparql", riformat="CSV"):
        ResourceIndexSearch.__init__(self)
        self.valid_languages = ("itql", "sparql")
        self.valid_formats = ("CSV", "Simple", "Sparql", "TSV")
        self.language = self.validate_language(language)
        self.format = self.validate_format(riformat)
        self.base_url = (
            f"{self.risearch_endpoint}?type=tuples"
            f"&lang={self.language}&format={self.format}"
        )

    def get_pages_and_page_numbers(self, book_pid):
        if self.language != "sparql":
            raise Exception(
                f"You must use sparql as the language for this method.  You used {self.language}."
            )
        sparql_query = self.escape_query(
            f"PREFIX fedora-model: <info:fedora/fedora-system:def/model#> PREFIX fedora-rels-ext: "
            f"<info:fedora/fedora-system:def/relations-external#> PREFIX isl-rels-ext: "
            f"<http://islandora.ca/ontology/relsext#> SELECT $page $numbers FROM <#ri> WHERE {{ $page "
            f"fedora-rels-ext:isMemberOf <info:fedora/{book_pid}> ; isl-rels-ext:isPageNumber $numbers .}}"
        )
        return requests.get(f"{self.base_url}&query={sparql_query}").content.decode(
            "utf-8"
        )


if __name__ == "__main__":
    x = TuplesSearch(language="sparql").get_pages_and_page_numbers("agrtfhs:2275")
    # x = TriplesSearch(language="sparql").get_pages_and_page_numbers("agrtfhs:2275")
    print(x)

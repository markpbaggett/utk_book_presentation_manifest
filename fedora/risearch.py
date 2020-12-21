class ResourceIndexSearch:
    def __init__(self):
        self.risearch_endpoint = "http://localhost:8080/fedora/risearch"


class TriplesSearch(ResourceIndexSearch):
    def __init__(self, language="spo", riformat="Turtle"):
        ResourceIndexSearch.__init__(self)
        self.base_url = (
            f"{self.risearch_endpoint}?type=triples"
            f"&lang={self.__validate_language(language)}&format={self.__validate_format(riformat)}"
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

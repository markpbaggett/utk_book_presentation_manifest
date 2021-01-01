import requests


class ResourceIndexSearch:
    def __init__(self, risearch_endpoint="http://localhost:8080/fedora/risearch"):
        self.risearch_endpoint = risearch_endpoint

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
        """
        @TODO Returns a 500 Internal Server Error: org.mulgara.query.rdf.LiteralImpl cannot be cast to org.jrdf.graph.PredicateNode

        """
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
    def __init__(
        self,
        language="sparql",
        riformat="CSV",
        ri_endpoint="http://localhost:8080/fedora/risearch",
    ):
        super().__init__(ri_endpoint)
        ResourceIndexSearch.__init__(self)
        self.valid_languages = ("itql", "sparql")
        self.valid_formats = ("CSV", "Simple", "Sparql", "TSV")
        self.language = self.validate_language(language)
        self.format = self.validate_format(riformat)
        self.base_url = (
            f"{self.risearch_endpoint}?type=tuples"
            f"&lang={self.language}&format={self.format}"
        )

    @staticmethod
    def __clean_csv_results(split_results, uri_prefix):
        results = []
        for result in split_results:
            if result.startswith(uri_prefix):
                new_result = result.split(",")
                results.append(
                    (new_result[0].replace(uri_prefix, ""), int(new_result[1]))
                )
        return sorted(results, key=lambda x: x[1])

    def get_pages_and_page_numbers(self, pid):
        """
        Returns a sorted list of tuples with the page and page number for the book.

        Args:
            pid (str): The PID of the book.

        Returns:
            list: A sorted list of tuples with the pid of the page and the corresponding page number.

        Example:
            >>> TuplesSearch(language="sparql").get_pages_and_page_numbers("agrtfhs:2275")
            [('agrtfhs:2279', 1), ('agrtfhs:2278', 2), ('agrtfhs:2291', 3), ('agrtfhs:2290', 4), ('agrtfhs:2289', 5),
            ('agrtfhs:2288', 6), ('agrtfhs:2287', 7), ('agrtfhs:2286', 8), ('agrtfhs:2285', 9), ('agrtfhs:2284', 10),
            ('agrtfhs:2283', 11), ('agrtfhs:2282', 12), ('agrtfhs:2281', 13), ('agrtfhs:2280', 14),
            ('agrtfhs:2277', 15), ('agrtfhs:2276', 16)]

        """
        if self.language != "sparql":
            raise Exception(
                f"You must use sparql as the language for this method.  You used {self.language}."
            )
        sparql_query = self.escape_query(
            f"PREFIX fedora-model: <info:fedora/fedora-system:def/model#> PREFIX fedora-rels-ext: "
            f"<info:fedora/fedora-system:def/relations-external#> PREFIX isl-rels-ext: "
            f"<http://islandora.ca/ontology/relsext#> SELECT $page $numbers FROM <#ri> WHERE {{ $page "
            f"fedora-rels-ext:isMemberOf <info:fedora/{pid}> ; isl-rels-ext:isPageNumber $numbers .}}"
        )
        results = (
            requests.get(f"{self.base_url}&query={sparql_query}")
            .content.decode("utf-8")
            .split("\n")
        )
        return self.__clean_csv_results(results, "info:fedora/")

    def get_parent_collection(self, pid):
        if self.language != "sparql":
            raise Exception(
                f"You must use sparql as the language for this method.  You used {self.language}."
            )
        sparql_query = self.escape_query(
            f"PREFIX fedora-model: <info:fedora/fedora-system:def/model#> PREFIX fedora-rels-ext: "
            f"<info:fedora/fedora-system:def/relations-external#> PREFIX isl-rels-ext: "
            f"<http://islandora.ca/ontology/relsext#> SELECT $collection FROM <#ri> WHERE {{ <info:fedora/{pid}> "
            f"fedora-rels-ext:isMemberOfCollection $collection . }}"
        )
        results = (
            requests.get(f"{self.base_url}&query={sparql_query}")
            .content.decode("utf-8")
            .split("\n")
        )
        return [
            result.replace("info:fedora/", "")
            for result in results
            if result.startswith("info:fedora")
        ][0]

    def get_collection_and_content_model(self, pid):
        """
        Gets the collection a pid belongs to and its content model.

        Args:
            pid (str): the pid that you want to determine.
        Returns:
            list: A list with the collection pid in index 0 and the content model in index 1.

        @todo: This assumes a pid only belongs to one collection.  This is naive and needs to be addressed.

        Example:
            >>> TuplesSearch(language="sparql").get_collection_and_content_model("agrtfhs:2275")
            ['collections:agrtfhs', 'islandora:bookCModel']
        """
        if self.language != "sparql":
            raise Exception(
                f"You must use sparql as the language for this method.  You used {self.language}."
            )
        sparql_query = self.escape_query(
            f"PREFIX fedora-model: <info:fedora/fedora-system:def/model#> PREFIX fedora-rels-ext: "
            f"<info:fedora/fedora-system:def/relations-external#> PREFIX isl-rels-ext: "
            f"<http://islandora.ca/ontology/relsext#> SELECT $collection $model FROM <#ri> WHERE {{ <info:fedora/{pid}> "
            f"fedora-rels-ext:isMemberOfCollection $collection ; fedora-model:hasModel $model . }}"
        )
        results = (
            [
                pair
                for pair in requests.get(f"{self.base_url}&query={sparql_query}")
                .content.decode("utf-8")
                .split("\n")
            ][2]
            .replace("info:fedora/", "")
            .split(",")
        )
        return results


if __name__ == "__main__":
    # x = TuplesSearch(language="sparql").get_pages_and_page_numbers("agrtfhs:2275")
    # x = TriplesSearch(language="sparql").get_pages_and_page_numbers("agrtfhs:2275")
    x = TuplesSearch(language="sparql").get_collection_and_content_model("agrtfhs:2275")
    print(x)
    print(type(x))

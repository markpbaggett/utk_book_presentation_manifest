import requests
import xmltodict
import arrow


class MODSScraper:
    def __init__(
        self,
        fedora_pid,
        islandora_frontend="https://digital.lib.utk.edu/collections/",
        presentation_api_version=2,
    ):
        self.pid = fedora_pid
        self.mods_xml = self.__get_mods(
            f"{islandora_frontend}/islandora/object/{fedora_pid}/datastream/MODS"
        )
        self.mods_dict = xmltodict.parse(self.mods_xml)
        self.label = self.get_title()
        self.description = self.get_abstract()
        self.navigation_date = self.get_navigation_date()

    @staticmethod
    def __get_mods(uri):
        return requests.get(uri).content.decode("utf-8")

    def get_title(self):
        """
        Gets the label of the presentation manifest

        Note: The 2.1 docs state this is "a human readable label, name or title for the resource. This property is
        intended to be displayed as a short, textual surrogate for the resource if a human needs to make a distinction
        between it and similar resources, for example between pages or between a choice of images to display.

        @todo: This needs refinement.  Grabs first title value in a messy way that wasn't thought out very much.
        """
        if type(self.mods_dict["mods"]["titleInfo"]) is list:
            titles = [title["title"] for title in self.mods_dict["mods"]["titleInfo"]]
            return titles[0]
        else:
            return self.mods_dict["mods"]["titleInfo"]["title"]

    def get_abstract(self):
        """
        Gets the value of the description element.

        Note: The 2.1 docs state this is "a longer-form prose description of the object or resource that the property
        is attached to, intended to be conveyed to the user as a full text description, rather than a simple label and
        value. It may be in simple HTML or plain text. It can duplicate any of the information from the metadata
        fields, along with additional information required to understand what is being displayed. Clients should have
        a way to display the descriptions of manifests and canvases, and may have a way to view the information about
        other resources.

        A manifest must have at least one label, such as the name of the object or title of the intellectual work that
        it embodies.
        """
        try:
            return self.mods_dict["mods"]["abstract"]
        except KeyError:
            return ""

    def __get_abstract_v3(self):
        if self.get_abstract() != "":
            return {
                "label": {"en": ["Abstract"]},
                "value": {"en": [self.get_abstract()]},
            }
        else:
            return ""

    def get_license_or_rights(self):
        """
        Gets the value of accessCondition/@xlink:href

        v2.1.1 Note: The 2.1 docs state this is, "a link to an external resource that describes the license or rights
        statement under which the resource may be used. The rationale for this being a URI and not a human readable
        label is that typically there is one license for many resources, and the text is too long to be displayed to
        the user along with the object. If displaying the text is a requirement, then it is recommended to include the
        information using the attribution property instead.

        v3.0.0 Note: A string that identifies a license or rights statement that applies to the content of the resource,
        such as the JSON of a Manifest or the pixels of an image. The value must be drawn from the set of Creative
        Commons license URIs, the RightsStatements.org rights statement URIs, or those added via the extension
        mechanism. The inclusion of this property is informative, and for example could be used to display an icon
        representing the rights assertions. If displaying rights information directly to the user is the desired
        interaction, or a publisher-defined label is needed, then it is recommended to include the information using
        the requiredStatement property or in the metadata property. The value must be a string. If the value is drawn
        from Creative Commons or RightsStatements.org, then the string must be a URI defined by that specification.
        """
        try:
            return self.mods_dict["mods"]["accessCondition"]["@xlink:href"]
        except KeyError:
            return ""

    def get_attribution(self):
        """
        Gets the attribution element.

        Note: The 2.1 docs state that this is the "text that must be shown when the resource it is associated with is
        displayed or used. For example, this could be used to present copyright or ownership statements, or simply an
        acknowledgement of the owning and/or publishing institution. Clients should try to match the language preferred
        by the user, and if the preferred language is unknown or unavailable, then the client may choose which value to
        display. If there are multiple values of the same or unspecified language, then all of those values must be
        displayed.
        """
        try:
            return self.mods_dict["mods"]["accessCondition"]["#text"]
        except KeyError:
            return ""

    def get_other_metadata(self):
        """
        Gets other metadata elements.

        Note: The 2.1 docs state this is a list of short descriptive entries, given as pairs of human readable label
        and value to be displayed to the user. The value should be either simple HTML, including links and text markup,
        or plain text, and the label should be plain text. There are no semantics conveyed by this information, and
        clients should not use it for discovery or other purposes. This list of descriptive pairs should be able to be
        displayed in a tabular form in the user interface. Clients should have a way to display the information about
        manifests and canvases, and may have a way to view the information about other resources. The client should
        display the pairs in the order provided by the description. A pair might be used to convey the author of the
        work, information about its creation, a brief physical description, or ownership information, amongst other
        use cases. The client is not expected to take any action on this information beyond displaying the label and
        value. An example pair of label and value might be a label of “Author” and a value of “Jehan Froissart”.

        A manifest should have one or more metadata pairs associated with it describing the object or work.
        """
        return [
            {"label": "Topics", "value": self.get_topics()},
            {"label": "Table of Contents", "value": self.get_table_of_contents()},
            {"label": "Publisher", "value": self.get_publisher()},
        ]

    def get_topics(self):
        """
        Gets topics from a MODS record.

        @todo: This code is somewhat problematic.  It assumes that there is more than one subject.  If there was only
        one subject, this would throw an exception.

        """
        if "subject" in self.mods_dict["mods"]:
            return [
                subject["topic"]
                for subject in self.mods_dict["mods"]["subject"]
                if "topic" in subject
            ]
        else:
            return []

    def __get_topics_v3(self):
        if len(self.get_topics()) != 0:
            return {"label": {"en": ["Topics"]}, "value": {"en": self.get_topics()}}
        else:
            return ""

    def get_publisher(self):
        """
        Gets the publisher of a book if one exists.

        """
        try:
            if "publisher" in self.mods_dict["mods"]["originInfo"]:
                return self.mods_dict["mods"]["originInfo"]["publisher"]
        except KeyError:
            return ""

    def __get_publisher_v3(self):
        if self.get_publisher() != "":
            return {
                "label": {"en": ["Publisher"]},
                "value": {"en": [self.get_publisher()]},
            }
        else:
            return ""

    def get_table_of_contents(self):
        """
        Gets the table of contents if one exists.
        """
        if "tableOfContents" in self.mods_dict["mods"]:
            return self.mods_dict["mods"]["tableOfContents"]

    def get_navigation_date(self):
        """
        Attempts to get a navigation date for the presentation manifest based on the MODS record and converts it to an
        xsd:dateTime literal in UTC in the format of “YYYY-MM-DDThh:mm:ssZ.”

        The 2.1 docs define this as, "a date that the client can use for navigation purposes when presenting the
        resource to the user in a time-based user interface, such as a calendar or timeline. The value must be an
        xsd:dateTime literal in UTC, expressed in the form “YYYY-MM-DDThh:mm:ssZ”. If the exact time is not known,
        then “00:00:00” should be used. Similarly, the month or day should be 01 if not known. There must be at most
        one navDate associated with any given resource. More descriptive date ranges, intended for display directly to
        the user, should be included in the metadata property for human consumption. A collection or manifest may have
        exactly one navigation date associated with it."

        This is messy.  First, it looks for dateIssued only because we have complex data for dates.  Ideally, this would
        look for other things, but I don't know where to look for an exhaustive list for this.

        Another possible issue: this looks for two types: dict and list.  If dateIssue is only one value, is it a dict
        or an OrderedDict?
        @todo: What does xmltodict do with single values? Should it be OrderedDict instead?
        @todo: What other dates should this look for?

        Returns:
            Tuple: A tuple with a boolean of whether there is a date and a string of the xsd formatted date.

        """
        try:
            if "dateIssued" in self.mods_dict["mods"]["originInfo"]:
                if type(self.mods_dict["mods"]["originInfo"]["dateIssued"]) is dict:
                    return (
                        True,
                        f"{str(arrow.get(self.mods_dict['mods']['originInfo']['dateIssued']['#text']).format('YYYY-MM-DD'))}T00:00:00Z",
                    )
                elif type(self.mods_dict["mods"]["originInfo"]["dateIssued"]) is list:
                    for date in self.mods_dict["mods"]["originInfo"]["dateIssued"]:
                        if "@encoding" in date:
                            return (
                                True,
                                f"{str(arrow.get(date['#text']).format('YYYY-MM-DD'))}T00:00:00Z",
                            )
            if "dateCreated" in self.mods_dict["mods"]["originInfo"]:
                if (
                    type(self.mods_dict["mods"]["originInfo"]["dateCreated"]) is dict
                    and "@encoding"
                    in self.mods_dict["mods"]["originInfo"]["dateCreated"]
                ):
                    return (
                        True,
                        f"{str(arrow.get(self.mods_dict['mods']['originInfo']['dateCreated']['#text']).format('YYYY-MM-DD'))}T00:00:00Z",
                    )
                elif type(self.mods_dict["mods"]["originInfo"]["dateCreated"]) is list:
                    for date in self.mods_dict["mods"]["originInfo"]["dateCreated"]:
                        if "@encoding" in date:
                            return (
                                True,
                                f"{str(arrow.get(date['#text']).format('YYYY-MM-DD'))}T00:00:00Z",
                            )
            else:
                return False, ""
        except KeyError:
            return False, ""

    def build_iiif_descriptive_metadata_v2(self):
        metadata = {
            "label": self.label,
            "pid": self.pid,
            "description": self.description,
            "license": self.get_license_or_rights(),
            "attribution": self.get_attribution(),
            "metadata": self.get_other_metadata(),
        }
        if self.navigation_date[0] is True:
            metadata["navDate"] = self.navigation_date[1]
        return metadata

    def build_iiif_descriptive_metadata_v3(self):
        metadata = {
            "label": {"en": [self.label]},
            "pid": self.pid,
            "rights": self.get_license_or_rights(),
            "metadata": self.build_iiif_v3_metadata_section(),
        }
        if self.get_abstract() != "":
            metadata["summary"] = {"en": [self.get_abstract()]}
        if self.navigation_date[0] is True:
            metadata["navDate"] = self.navigation_date[1]
        return metadata

    def build_iiif_v3_metadata_section(self):
        metadata_methods = (
            self.__get_abstract_v3(),
            self.__get_publisher_v3(),
            self.__get_topics_v3(),
        )
        return [method for method in metadata_methods if method != ""]


class MODSParser:
    def __init__(
        self,
        fedora_pid,
        fedora_url="http://localhost:8080",
        auth=("fedoraAdmin", "fedoraAdmin"),
    ):
        self.pid = fedora_pid
        self.url = fedora_url
        self.auth = (auth,)
        self.mods_xml = self.__get_mods(
            f"{fedora_url}/fedora/objects/{fedora_pid}/datastreams/MODS/content", auth
        )
        self.mods_dict = xmltodict.parse(self.mods_xml)

    @staticmethod
    def __get_mods(uri, auth):
        return requests.get(uri, auth=auth).content.decode("utf-8")

    def get_label(self):
        """Find a label for the object based on this xpath: mods:titleInfo[not(@type="alternative")]/mods:title"""
        if type(self.mods_dict["mods"]["titleInfo"]) is list:
            titles = [
                title["title"]
                for title in self.mods_dict["mods"]["titleInfo"]
                if "@type" not in title
            ]
            return titles[0]
        else:
            return self.mods_dict["mods"]["titleInfo"]["title"]


if __name__ == "__main__":
    x = MODSParser("test:42")
    print(x.get_label())

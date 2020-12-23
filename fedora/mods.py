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
        self.description = self.get_abstract()

    @staticmethod
    def __get_mods(uri):
        r = requests.get(uri).content.decode("utf-8")
        return xmltodict.parse(r)

    def get_title(self):
        """
        Gets the label of the presentation manifest

        Note: The 2.1 docs state this is "a human readable label, name or title for the resource. This property is
        intended to be displayed as a short, textual surrogate for the resource if a human needs to make a distinction
        between it and similar resources, for example between pages or between a choice of images to display.
        """
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
        return self.mods_dict["mods"]["abstract"]

    def get_license_or_rights(self):
        """
        Gets the value of accessCondition/@xlink:href

        Note: The 2.1 docs state this is, "a link to an external resource that describes the license or rights
        statement under which the resource may be used. The rationale for this being a URI and not a human readable
        label is that typically there is one license for many resources, and the text is too long to be displayed to
        the user along with the object. If displaying the text is a requirement, then it is recommended to include the
        information using the attribution property instead.
        """
        return self.mods_dict["mods"]["accessCondition"]["@xlink:href"]

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
        return self.mods_dict["mods"]["accessCondition"]["#text"]

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
        return []


if __name__ == "__main__":
    x = MODSScraper("agrtfhs:2275")
    print(x.label)

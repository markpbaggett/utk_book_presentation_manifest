from fedora.mods import MODSScraper
from iiif.manifest import Manifest
from tripoli import IIIFValidator
import unittest


class PresentationManifestTester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(PresentationManifestTester, self).__init__(*args, **kwargs)
        self.book_pages = [
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
        self.metadata = MODSScraper("agrtfhs:2275").build_iiif_descriptive_metadata()
        self.collection = "collections:agrtfhs"
        self.validator = IIIFValidator(debug=True, collect_warnings=False)

    def test_presentation_manifest(self):
        manifest = Manifest(self.metadata, self.book_pages, self.collection)
        self.validator.validate(manifest.manifest_json)
        self.assertTrue(self.validator.is_valid)

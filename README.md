# UTK Book to IIIF Presentation Manifest

![Run Tests](https://github.com/markpbaggett/utk_book_presentation_manifest/workflows/Run%20Tests/badge.svg)

Generates a 2.1.1 presentation manifest for a book from a UTK Islandora 7 object and serializes it to disk.
3.0.0 coming soon.

This isn't intended for public use, but rather exploration.

## Requirements

1. **RISEARCH**: Must be installed on a machine with access to the Resource Index of the Fedora instance in question.
This allows the application to get information about the book's relationship to other resources. No credentials are
required, but you will need to have HTTP access to the ResourceIndex search interface.
2. **MODS**: The MODS record of the object must be publicly accessible via HTTP.
3. **Drupal Installation Assumption**: Currently this makes the assumption that drupal is installed at a path like,
`http://somewhere/collections`.  This is due to an oversight that can be easily addressed.
4. **Python**: Python 3.6 or higher.

## Installing

With Pipenv:

```shell script
pipenv install
```

## Running

```shell script
pipenv shell
python run.py -b agrtfhs:2275 -f manifest.json
```

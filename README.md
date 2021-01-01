# UTK Islandora 7 Presentation Manifest Generator

![Run Tests](https://github.com/markpbaggett/utk_book_presentation_manifest/workflows/Run%20Tests/badge.svg)

Generates presentation manifests for objects from UTK Islandora 7 repositories.

This isn't intended for public use, but rather thinking about future recipes for delivering UTK content models.

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
python run.py -p agrtfhs:2275 -f manifest.json
```

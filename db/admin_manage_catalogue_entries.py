"""
This script is for admins to bulk manage the catalogue entries
run:
    python3 manage.py shell
then use the script
"""
from catalogue.models import CatalogueEntries, GraphEntries
from django.conf import settings

from pathlib import Path

import os
import xml.etree.ElementTree

all_entries_name = set(str(e) for e in CatalogueEntries.objects.all())

published_catalogue_path = settings.PUBLISHED_CATALOGUE_DIR


def _is_duplicate(concept_name):
    if concept_name in all_entries_name:
        return True
    else:
        return False


def _get_basename(file_path):
    return os.path.basename(file_path)


def _get_subdir(file):
    subdir = os.path.relpath(Path(file).resolve().parent, published_catalogue_path)
    if subdir == '.':
        return ''
    return subdir


def _get_catalogue_info(file):
    tree = xml.etree.ElementTree.parse(file)
    concept = tree.getroot().find("concept")
    if concept:
        info = concept.find("info").attrib
        return {
            "id": info["id"],
            "name": info["name"],
            "version": info["version"],
        }
    else:
        return {
            "id": "None",
            "name": "None",
            "version": "None"
        }


def bulk_addition():
    """
    Update the published catalogue in the database, given that the directory is already updated.
    Excluded all duplicates
    """
    for root, dirs, files in os.walk(published_catalogue_path):
        for file in files:
            if _is_duplicate(os.path.basename(file)):
                continue
            else:
                file_path = os.path.join(root, file)
                basename = os.path.basename(file_path)
                info = _get_catalogue_info(file_path)
                CatalogueEntries.objects.create(entry_path=file_path,
                                                entry_name=basename,
                                                entry_version=info['version'],
                                                belongs_to_sub_directory=_get_subdir(file_path))
                GraphEntries.objects.create(entry_path=file_path,
                                            entry_id=info["id"],
                                            entry_name=info["name"],
                                            entry_version=info["version"]
                                            )

# now depend on your need, you could:
bulk_addition()  # to bulk add all published catalogue, exclude duplicates.

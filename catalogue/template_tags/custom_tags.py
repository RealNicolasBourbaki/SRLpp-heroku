from django.template.defaulttags import register
from django.conf import settings
import os

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def define(val=None):
    return val


@register.simple_tag
def get_link_target(file_path):
    import os
    return os.path.relpath(file_path, settings.PUBLISHED_CATALOGUE_DIR)


@register.simple_tag
def get_basename(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


@register.simple_tag
def get_graph_type(graph_filename):
    graph_filename = os.path.splitext(graph_filename)[0]
    if graph_filename.split("_")[1] == "modelling":
        return "Modelling Part"
    else:
        return "Semantic Graph"


@register.simple_tag
def get_graph_id(graph_filename):
    return graph_filename.split("_")[0]

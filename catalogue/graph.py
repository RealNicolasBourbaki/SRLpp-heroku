import io
import os
import textwrap
import networkx as nx
import matplotlib.pyplot as plt
import boto3

from django.conf import settings
from .models import GraphEntries
from networkx.drawing.nx_pydot import graphviz_layout

s3 = boto3.resource('s3', region_name=settings.AWS_S3_REGION_NAME)
bucket = s3.Bucket(settings.AWS_BUCKET)

GRAPH_NODE_COLORS = {
    "concept_nodes": "#bcf5fb",  # light blue
    "omitted_nodes": "#ffffff",  # white
    "entity_nodes": "#ffffff",  # white
    "metaoperator_nodes": "##ffb070",  # light orange
    "pseudo_nodes": "none"  # white
}

GRAPH_NODE_SHAPE = {
    "concept_nodes": "s",
    "omitted_nodes": "o",
    "entity_nodes": "o",
    "metaoperator_nodes": "s",
    "pseudo_nodes": "o"
}


def _get_modellings(xml_tree):
    root = xml_tree.getroot()
    all_graphs_info = list()
    all_graphs_id = list()

    modelling_def = root.find("concept/modelling")

    semantic_graphs = root.findall("semanticGraph")
    if semantic_graphs:
        for semantic_graph in semantic_graphs:
            graph_info = semantic_graph.find("graphInfo")
            all_graphs_id.append(graph_info.attrib["graphId"])
            all_graphs_info.append(graph_info.attrib)

    return all_graphs_id, all_graphs_info, modelling_def, semantic_graphs


def get_nodes_from_def(sg):
    nodes = sg.find("modellingDef/nodes")
    concept_nodes = nodes.findall("conceptNode")
    anonymous_nodes = nodes.findall("omittedNode")
    entity_nodes = nodes.findall("entityNode")
    metaoperator_nodes = nodes.findall("metaoperatorNode")
    unknown_nodes = nodes.findall("pseudoNode")
    return {
        "concept_nodes": concept_nodes,
        "omitted_nodes": anonymous_nodes,
        "entity_nodes": entity_nodes,
        "metaoperator_nodes": metaoperator_nodes,
        "pseudo_nodes": unknown_nodes
    }


def _extract_graph_info(graph_info):
    modality = graph_info["modality"]
    language = graph_info["language"]
    source_link = graph_info["sourceLocation"]
    if "modellingPart" in graph_info.keys():
        modelling_part = True if graph_info["modellingPart"] == "true" else False
    else:
        modelling_part = False
    return modality, language, source_link, modelling_part


def make_edges(edges):
    all_edges_label = {}
    for edge in edges:
        edge_from = edge.attrib["from"]
        edge_to = edge.attrib["to"]
        label = edge.attrib["label"]
        all_edges_label[(edge_from, edge_to)] = label
    return all_edges_label


def make_graphs(tree, file_path, out_path):
    all_graphs_id, all_graphs_info, modelling_def, semantic_graphs = _get_modellings(
        tree)
    assert len(all_graphs_id) == len(
        all_graphs_info) == len(semantic_graphs)

    for graph_info, graph_id, sg in zip(
            all_graphs_info, all_graphs_id, semantic_graphs):
        make_graph(graph_info, graph_id, sg, file_path, out_path)


def make_graph(graph_info, graph_id, sg, file_path, out_path):
    if sg:
        modelling_graph = ModelGraph(graph_id, False)
        modelling_all_nodes = get_nodes_from_def(sg)
        modality, language, source_link, modelling_part = _extract_graph_info(graph_info)
        modelling_graph.set_graph_info(modality, language, source_link, modelling_part)
        this_root_id = None
        for node_type, nodes in modelling_all_nodes.items():
            if nodes:
                for node in nodes:
                    node_id, name, root, modelling, version, root_id = _make_nodes(node_type, node)
                    if root_id:
                        this_root_id = root_id
                    model_node = ModelNode(
                        node_id,
                        name,
                        root,
                        node_type,
                        modelling,
                        version)
                    modelling_graph.add_model_node(model_node)
        edges_labels = make_edges(sg.findall("modellingDef/edges/edge"))
        modelling_graph.add_edges_from(list(edges_labels.keys()))
        # check error (empty entry)
        draw_graph(modelling_graph, edges_labels, this_root_id, file_path, out_path)


def _make_nodes(node_type, node):
    node_attribs = node.attrib
    keys = node_attribs.keys()
    this_root = None
    node_id = node_attribs["nodeId"]
    # nodeId is required attribute
    if node_type == 'concept_nodes':
        if "name" not in keys:
            name = _get_cpt_name(node_attribs['id'])
        else:
            name = node_attribs["name"]
    else:
        name = node_attribs["name"] if "name" in keys else None

    if "root" in keys:
        root = True if node_attribs["root"] == "true" else False
        this_root = node_id
    else:
        root = False

    # "type", "root" and "role" are optional attributes

    modelling = node_attribs["modelling"] if "modelling" in keys else None

    version = node_attribs["version"] if "version" in keys else None

    return node_id, name, root, modelling, version, this_root


def _get_cpt_name(cpt_id):
    entries = GraphEntries.objects.all()
    for entry in entries:
        if entry.entry_id == cpt_id:
            return entry.entry_name
        else:
            continue
    return cpt_id


def draw_graph(graph, edges_labels, this_root, file_path, out_path):
    global GRAPH_NODE_COLORS
    pos = graphviz_layout(graph, root=this_root, prog="dot")
    node_info = graph.get_node_dict()

    plt.figure(figsize=(7, 8))

    concept_nodes = [
        node for node in filter(
            lambda x: node_info[x].get_node_type() == "concept_nodes",
            graph.nodes())]
    meta_nodes = [
        node for node in filter(
            lambda x: node_info[x].get_node_type() == "metaoperator_nodes",
            graph.nodes())]
    concept_labels = {
        node_id: node_info[node_id].get_node_label() for node_id in concept_nodes}
    meta_labels = {
        node_id: node_info[node_id].get_node_label() for node_id in meta_nodes}
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color="none",
        edgecolors="none",
        nodelist=concept_nodes + meta_nodes,
    )
    nx.draw_networkx_labels(
        graph,
        pos,
        concept_labels,
        bbox=dict(
            facecolor=GRAPH_NODE_COLORS["concept_nodes"],
            edgecolor=GRAPH_NODE_COLORS["concept_nodes"],
            boxstyle='round,pad=1'))
    nx.draw_networkx_labels(
        graph,
        pos,
        meta_labels,
        bbox=dict(
            facecolor=GRAPH_NODE_COLORS["metaoperator_nodes"],
            edgecolor=GRAPH_NODE_COLORS["metaoperator_nodes"],
            boxstyle='round,pad=1'))
    other_nodes = [node_id for node_id in graph.nodes(
    ) if node_id not in concept_nodes and node_id not in meta_nodes]
    for node_id in other_nodes:
        nx.draw_networkx_nodes(
            graph,
            pos,
            linewidths=1,
            edgecolors="#d3d3d3",
            node_size=1800,
            node_color=GRAPH_NODE_COLORS[node_info[node_id].get_node_type()],
            nodelist=[node_id])
        nx.draw_networkx_labels(
            graph, pos, {
                node_id: '\n'.join(
                    textwrap.wrap(
                        node_info[node_id].get_node_label(), width=12))})

    nx.draw(graph, pos, node_color="none", node_shape="s", node_size=2500)
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edges_labels,
        font_color="black")
    plt.axis("off")
    basename = os.path.splitext(os.path.basename(file_path))[0]
    # goal_dir = os.path.join(out_path, basename)
    img_data = io.BytesIO()
    # if not os.path.exists(goal_dir):
    #    os.makedirs(goal_dir)
    if graph.ifmodelling:
        plt.savefig(img_data, format="png")
        img_data.seek(0)
        upload_path = os.path.join(settings.TEMP_DIR, basename, graph.graph_id+"_modelling.png")
        bucket.upload_fileobj(img_data, os.path.relpath(upload_path, settings.AWS_URL))
        # plt.savefig(
        #    os.path.join(
        #        out_path,
        #        basename,
        #        graph.graph_id +
        #        "_modelling.png"),
        #    format="PNG")
    else:
        plt.savefig(img_data, format="png")
        img_data.seek(0)
        upload_path = os.path.join(settings.TEMP_DIR, basename, graph.graph_id + "_sg.png")
        bucket.upload_fileobj(img_data, os.path.relpath(upload_path, settings.AWS_URL))
        # plt.savefig(
        #     os.path.join(
        #         out_path,
        #         basename,
        #         graph.graph_id +
        #         "_sg.png"),
        #     format="PNG")


class ModelNode:
    def __init__(
            self,
            node_id,
            name,
            root,
            node_type,
            modelling,
            version
    ):
        self.node_id = node_id
        self.label = name
        self.root = True if root == "true" else False
        self.node_type = node_type
        self.modelling = modelling
        self.version = version

    def get_node_id(self):
        return self.node_id

    def get_node_label(self):
        return self.label

    def get_node_type(self):
        return self.node_type


class ModelGraph(nx.DiGraph):

    def __init__(
            self,
            graph_id,
            ifmodelling,
            incoming_graph_data=None,
            **attr):
        super().__init__(incoming_graph_data, **attr)
        self.graph_id = graph_id
        self.ifmodelling = ifmodelling
        self.node_dict = dict()

    def add_model_node(self, modelling_node):
        global GRAPH_NODE_SHAPE
        node_id = modelling_node.get_node_id()
        self.add_node(node_id, s=GRAPH_NODE_SHAPE[modelling_node.node_type])
        self.node_dict[node_id] = modelling_node

    def set_graph_info(self, media, language, source_link, modelling_part):
        self.media = media
        self.language = language
        self.source_link = source_link
        self.modelling_part = modelling_part

    def get_node_dict(self):
        return self.node_dict

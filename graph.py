# -*- coding: utf-8 -*-
# by Alejandro Rojo Gualix 2021-06
"""
Clase básica para definir grafos y operaciones básicas con ellos
"""
import sys
import urllib.parse
import webbrowser
graphviz_website = 'https://dreampuf.github.io/GraphvizOnline/#%s'
# How to disable TOKENIZERS_PARALLELISM=(true | false) warning?
# https://stackoverflow.com/questions/62691279/how-to-disable-tokenizers-parallelism-true-false-warning
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class Graph:
    def __str__(self):
        if self.edges:
            return ', '.join([str(_) for _ in self.nodes]) + '\n' + ' | '.join([f'{edge.start}->{edge.end}' for edge in self.edges.keys()])
        else:
            return ', '.join([str(_) for _ in self.nodes])

    def __init__(self, nodes=None, nodes_attr=None):
        # key is an object, value is a dictionary of dot display properties
        self.nodes = {}
        self.edges = {}
        if nodes is not None:
            for index, node in enumerate(nodes):
                if node is not None:
                    if nodes_attr is None:
                        self.create_node(node, {})  # <<<<<<<<<<<< IMPORTANTÍSIMO {} same properties
                    else:
                        self.create_node(node, nodes_attr[index])

    def merge_graphs(self, graphs, erase=False):
        if erase:  # note: erases previous data
            self.nodes = {}
            self.edges = {}        
        for graph in graphs:
            #     graph.print()
            self.nodes.update(graph.nodes)
            self.edges.update(graph.edges)

    def create_node(self, node, properties={}):
        # if isinstance(node, list):
        #     [create_node(_, properties) for _ in node]  # assign the same properties by reference
        # el
        if node in self.nodes:
            self.update_node_properties(node, properties)  # update. or erase?
            return False
        else:
            self.nodes[node] = properties
            return True

    # independiente de valor edge
    def add_edge(self, start, end, label='', properties={}, multiple_edges=False):
        if start not in self.nodes:  # edge points to an inexistent node'
            self.create_node(start)
        if end not in self.nodes:  # edge points to an inexistent node'
            self.create_node(end)

        if not multiple_edges:
            for edge in self.edges.keys():
                if type(edge.start) == type(start) and type(edge.end) == type(end) \
                and edge.start == start and edge.end == end and edge.label == label:
                    return False

        # assert len(self.edges) == len(self.edges_attr), 'ERROR len(self.edges) == len(self.edges_attr)'
        self.edges[Edge(start, end, label)] = properties
        return True

    def reverse_edge(self, edge):
        edge.start, edge.end = edge.end, edge.start

    def remove_node(self, node):
        self.remove_edges(start=node)
        self.remove_edges(end=node)
        del self.nodes[node]

    def remove_edges(self, start=None, end=None):
        for edge in self.search_edges(start, end):
            del self.edges[edge]

    def bypass_node(self, node):
        """
            A -> B -> C, D
            bypass B
            A -> C, D
        """
        target_node = self.search_nodes(start=node)[0]  # <<<<<<<<<<<<<<
        for edge in self.search_edges(end=node):
            edge.end = target_node
        # removes node
        self.remove_node(node)

    def reset_nodes_properties(self):
        for node in self.nodes.keys():
            self.nodes[node] = {}

    def reset_edges_properties(self):
        for edge in self.edges.keys():
            self.edges[edge] = {}

    def update_node_properties(self, node, properties):
        self.nodes[node].update(properties)

    def update_edge_properties(self, edge, properties):
        self.edges[edge].update(properties)


    def search_edges(self, start=None, end=None):
        # start
        if start is not None and end is not None:
            return [_ for _ in self.edges.keys() if _.start == start and _.end == end]
        elif start is not None:
            return [_ for _ in self.edges.keys() if _.start == start]
        elif end is not None:
            return [_ for _ in self.edges.keys() if _.end == end]
        else:  # no conditions, return all edges
            return self.edges.keys()

    def search_nodes(self, start=None, end=None):
        # start
        if start is not None or end is not None:
            edges = self.search_edges(start, end)
            nodes = []
            if start is not None:
                nodes = [ _.end for _ in edges ]
            if end is not None:
                nodes += [ _.start for _ in edges ]
            return nodes
        else:  # no conditions, return all nodes
            return self.nodes

    def complement(self, exclude_nodes):
        return [ _ for _ in self.nodes if not _ in exclude_nodes ]

    def root_nodes(self):
        end_nodes = { _.end for _ in self.edges.keys() }
        complement = [ _ for _ in self.nodes if not _ in end_nodes ]
        return complement

    def leaf_nodes(self):
        start_nodes = { _.start for _ in self.edges.keys() }
        complement = [ _ for _ in self.nodes if not _ in start_nodes ]
        return complement

    def isolated_nodes(self):
        return self.root_nodes().intersection(self.leave_nodes()) 

    # def start_nodes(self, node):
    #     return self.search_nodes(end=node)
    # def end_nodes(self, node):
    #     return self.search_nodes(start=node)

    # for trees, one parent only
    def head(self, node):
        froms = self.search_nodes(end=node)
        assert len(froms) < 2, 'A node has more than one parent node so this is not a tree, use search_nodes() method instead'
        if froms:
            return froms[0]

    def children(self, node):
        return self.search_nodes(start=node)


    def dot_write_attributes(self, obj, properties):
        properties_str = [ f'{attribute}="{value}"' for attribute, value in properties.items() if not attribute == 'label']

        if 'label' in properties and properties['label']:  # tiene preferencia para la presentación de información
            label = properties['label']
            if len(label) >= 2 and label[0] == '<' and label[-1] == '>':  #html
                properties_str.insert(0, f'label={label}')
            else:
                properties_str.insert(0, f'label="{label}"')
        elif obj.label:
            properties_str.insert(0, f'label="{obj.label}"')

        if properties_str:
            return ' [' + ', '.join(properties_str) + ']'
        else:
            return ''

    def get_index(self, arg_list, arg_search):
        # type checking. avoid wordnet eq function error
        for index, item in enumerate(arg_list):
            if type(item) == type(arg_search) and item == arg_search:
                return index

    def dot_graph_format(self, title_section='', defaults_section=''):
        node_list = list(self.nodes.keys())  # enumerate dictionary
        nodes_dot = '\n'.join(
            [f'{index}{self.dot_write_attributes(node, self.nodes[node])};' 
            for index, node in enumerate(node_list)])
        edges_dot = '\n'.join(
            [f"{self.get_index(node_list, edge.start)} -> {self.get_index(node_list, edge.end)}{self.dot_write_attributes(edge, self.edges[edge])};"
            for edge in self.edges.keys()])

        # defaults_section = """edge [color="gray80", fontcolor="gray60"];"""
        return f"""digraph G {{
            {title_section}
            node [shape="plaintext"];
            edge [color="gray80"];
            {defaults_section}

            {nodes_dot}

            {edges_dot}
        }}"""

    def dot_graph_subgraph_format(self, subgraphs, title_section='', defaults_section=''):
        node_list = list(self.nodes.keys())  # enumerate dictionary

        nodes = set(self.nodes.keys())
        subgraphs_dot = ''
        for index, subgraph in enumerate(subgraphs):
            nodes_dot = '\n'.join(
                [f'{self.get_index(node_list, node)}{self.dot_write_attributes(node, self.nodes[node])};'
                 for node in subgraph])
            # aquí las aristas
            subgraphs_dot += f"""
            subgraph cluster_{index} {{
                style=filled;
                color=gray93;
                node [style=filled, color=white];
                {nodes_dot}
                # label = "process #1";
            }}
            """
            for node in subgraph:
                nodes.remove(node)

        main_graph_dot = '\n'.join(
            [f'{self.get_index(node_list, node)}{self.dot_write_attributes(node, self.nodes[node])};'
            for node in nodes])

        edges_dot = '\n'.join(
            [f"{self.get_index(node_list, edge.start)} -> {self.get_index(node_list, edge.end)}{self.dot_write_attributes(edge, self.edges[edge])};"
            for edge in self.edges.keys()])

        # defaults_section = """edge [color="gray80", fontcolor="gray60"];"""
        return f"""digraph G {{
            {title_section}
            node [shape="plaintext"];
            edge [color="gray80"];
            {defaults_section}

            {subgraphs_dot}
            {main_graph_dot}

            {edges_dot}
        }}"""

    def visualize(self):
        self.visualize_string(self.dot_graph_format())

    def visualize_string(self, data):
        """ hay dos opciones
        1) en el navegador a través de una aplicación web
        2) aquí, creando un archivo de imagen [POR IMPLEMENTAR]
        """
        url = graphviz_website % urllib.parse.quote(data)
        # webbrowser.open(url, new=2)  # new=2     a new browser page (“tab”) is opened if possible
        webbrowser.open_new_tab(url)
        title = """
            labelloc="t";
            label="patrón: %s";    
            fontsize = 14;
            fontcolor = gray60;""" % ''
        # dot_pattern = PatternGraph(graph.pattern, graph.pattern_trace).dot_graph_format(title)


class Edge:
    def __str__(self):
        return self.label
        if 'label' in self.properties:
            return self.properties['label']
        else:
            return ''

    def __init__(self, start, end, label='', properties={}):
        self.start = start
        self.end = end
        self.label = label
        self.properties = properties  # custom properties dictionary


class Node:
    def __str__(self):
        return self.label

    def __init__(self, label, properties={}, ref_object=None):
        self.label = label
        self.ref_object = ref_object  # optional reference_object that this class is based on
        self.properties = properties  # custom properties dictionary

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import argparse
import collections
import itertools
import os
import sys

import msat_runner
import wcnf


# Graph class
###############################################################################


class Graph(object):
    """This class represents an undirected graph. The graph nodes are
    labeled 1, ..., n, where n is the number of nodes, and the edges are
    stored as pairs of nodes.
    """

    def __init__(self, file_path=""):
        self.edges = []
        self.n_nodes = 0

        if file_path:
            self.read_file(file_path)

    def read_file(self, file_path):
        """Loads a graph from the given file.

        :param file_path: Path to the file that contains a graph definition.
        """
        with open(file_path, 'r') as stream:
            self.read_stream(stream)

    def read_stream(self, stream):
        """Loads a graph from the given stream.

        :param stream: A data stream from which read the graph definition.
        """
        n_edges = -1
        edges = set()

        reader = (l for l in (ll.strip() for ll in stream) if l)
        for line in reader:
            l = line.split()
            if l[0] == 'p':
                self.n_nodes = int(l[2])
                n_edges = int(l[3])
            elif l[0] == 'c':
                pass  # Ignore comments
            else:
                edges.add(frozenset([int(l[1]), int(l[2])]))

        self.edges = tuple(tuple(x) for x in edges)
        if n_edges != len(edges):
            print("Warning incorrect number of edges")


    def visualize(self, name="graph"):
        """Visualize graph using 'graphviz' library.

        To install graphviz you can use 'pip install graphviz'.
        Notice that graphviz should also be installed in your system.
        For ubuntu, you can install it using 'sudo apt install graphviz'
        :param name: Name of the generated file, defaults to "graph"
        :type name: str, optional
        :raises ImportError: When unable to import graphviz.
        """
        try:
            from graphviz import Graph
        except ImportError:
            msg = (
                "Could not import 'graphviz' module. "
                "Make shure 'graphviz' is installed "
                "or install it typing 'pip install graphviz'"
            )
            raise ImportError(msg)
        # Create graph
        dot = Graph()
        # Create nodes
        for n in range(1, self.n_nodes + 1):
            dot.node(str(n))
        # Create edges
        for n1, n2 in self.edges:
            dot.edge(str(n1), str(n2))
        # Visualize
        dot.render(name, view=True, cleanup=True)

    def min_vertex_cover(self, solver):
        """Computes the minimum vertex cover of the graph.

        :param solver: An instance of MaxSATRunner.
        :return: A solution (list of nodes).
        """
        # Initialize formula
        formula = wcnf.WCNFFormula()
        # Creates Variables
        nodes = [formula.new_var() for _ in range(self.n_nodes)]
        # Creates soft calusules
        list(map(lambda x: formula.add_clause([-x], weight=1), nodes))
        list(map(lambda x: formula.add_clause([nodes[x[0] - 1], nodes[x[1] - 1]],
            weight=wcnf.TOP_WEIGHT), self.edges))
        # formula.write_dimacs()  # Prints for debug.
        _, model = solver.solve(formula)
        # print("Opt: ", opt)
        # print("Model: ", model)
        return list(filter(lambda x: x > 0, model))

    def max_clique(self, solver):
        """Computes the maximum clique of the graph.

        :param solver: An instance of MaxSATRunner.
        :return: A solution (list of nodes).
        """
        # Initialize formula
        formula = wcnf.WCNFFormula()
        # Creates Variables
        nodes = [formula.new_var() for _ in range(self.n_nodes)]
        # Creates soft calusules
        list(map(lambda x: formula.add_clause([-x], weight=1), nodes))
        list(map(lambda x: formula.add_clause([nodes[x[0] - 1], nodes[x[1] - 1]],
            weight=wcnf.TOP_WEIGHT), self.edges))
        # formula.write_dimacs()  # Prints for debug.
        _, model = solver.solve(formula)
        # print("Opt: ", opt)
        # print("Model: ", model)
        return list(filter(lambda x: x > 0, model))


    def max_cut(self, solver):
        """Computes the maximum cut of the graph.

        :param solver: An instance of MaxSATRunner.
        :return: A solution (list of nodes).
        """
        def soft_clause(x):
            formula.add_clause([nodes[x[0] - 1], nodes[x[1] - 1]], weight=1)
            formula.add_clause([-nodes[x[0] - 1], -nodes[x[1] - 1]], weight=1)
        # Initialize formula
        formula = wcnf.WCNFFormula()
        # Creates Variables
        nodes = [formula.new_var() for _ in range(self.n_nodes)]
        # Creates soft calusules
        list(map(soft_clause, self.edges))
        _, model = solver.solve(formula)
        # print(formula)
        formula.write_dimacs(open('prova.dimacs', 'w'))
        return list(filter(lambda x: x > 0, model))



# Program main
###############################################################################


def main(argv=None):
    args = parse_command_line_arguments(argv)

    solver = msat_runner.MaxSATRunner(args.solver)
    graph = Graph(args.graph)
    if args.visualize:
        graph.visualize(os.path.basename(args.graph))

    min_vertex_cover = graph.min_vertex_cover(solver)
    print("MVC", " ".join(map(str, min_vertex_cover)))

    max_clique = graph.max_clique(solver)
    print("MCLIQUE", " ".join(map(str, max_clique)))

    max_cut = graph.max_cut(solver)
    print("MCUT", " ".join(map(str, max_cut)))



# Utilities
###############################################################################


def parse_command_line_arguments(argv=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("solver", help="Path to the MaxSAT solver.")

    parser.add_argument("graph", help="Path to the file that descrives the"
                                      " input graph.")
    parser.add_argument("--visualize", "-v", action="store_true",
                        help="Visualize graph (graphviz required)")

    return parser.parse_args(args=argv)


# Entry point
###############################################################################


if __name__ == "__main__":
    sys.exit(main())

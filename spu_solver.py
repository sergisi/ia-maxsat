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


# SPU class
###############################################################################


class Spu(object):
    """This class represents a list of packages to be installed. The packages are
    labeled by their name.
    """

    def __init__(self, file_path=""):
        self.n_pkg = 0
        self.conflicts = []  # format (pkg, pkg)
        self.dependencies = []  # format (pkg, [pkgs...])
        self.pkg_toinstall = set()
        if file_path:
            self.read_file(file_path)

    def read_file(self, file_path):
        """Loads a packages list from the given file.

        :param file_path: Path to the file that contains a graph definition.
        """
        with open(file_path, 'r') as stream:
            self.read_stream(stream)

    def read_stream(self, stream):
        """Loads a package list from the given stream.

        :param stream: A data stream from which read the graph definition.
        """
        n_edges = -1
        edges = set()

        reader = (l for l in (ll.strip() for ll in stream) if l)
        for line in reader:
            l = line.split()
            if l[0] == 'p':
                self.n_pkg = int(l[2])
            elif l[0] == 'n':
                self.pkg_toinstall.append(l[1])
            elif l[0] == 'd':
                self.dependencies.append((l[1], l[2:]))
            else:  # c conflics
                edges.conflicts.append((l[1], l[2]))

        if self.n_pkg != len(self.pkg_toinstall):
            print("Warning incorrect number of packages")

    # TODO: @sergi this upwards needs to be done.
    def visualize(self, name="graph"):
        """Visualize dependencies and unrelated using 'graphviz' library.

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
        for n in self.packages:
            dot.node(n)
        # Create edges
        for n1, n2 in self.dependencies:
            dot.edge(str(n1), str(n2))
        for n1, n2 in self.conflicts:
            dot.edge(n1, n2)
        # Visualize
        dot.render(name, view=True, cleanup=True)


    def package_dependencies(self, solver):
        """ Computes the packages that cannot be installed.
        :param solver : An instance of MaxSatRunner.
        :return: A solution of packages not needed to install. The 
            format is: 
                o <n>
                v [pkg, ...]
            where n is the number of packages not installed and pkg is the
            package not installed
        """
        pass


# Program main
###############################################################################


def main(argv=None):
    args = parse_command_line_arguments(argv)

    solver = msat_runner.MaxSATRunner(args.solver)
    spu = Spu(args.spu)
    if args.visualize:
        spu.visualize(os.path.basename(args.spu))

    pkg_dependencie = spu.package_dependencies(solver)
    print("PKG_DEPENDENCIES:\n", " ".join(min_vertex_cover))



# Utilities
###############################################################################


def parse_command_line_arguments(argv=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("solver", help="Path to the MaxSAT solver.")

    parser.add_argument("spu", help="Path to the file that descrives the"
                                      " input graph.")
    parser.add_argument("--visualize", "-v", action="store_true",
                        help="Visualize graph (graphviz required)")

    return parser.parse_args(args=argv)


# Entry point
###############################################################################


if __name__ == "__main__":
    sys.exit(main())
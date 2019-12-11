#!/usr/bin/env python3
""" This module serves to resolve SPU problems. """
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import argparse
import collections
# import itertools
import os
import sys

import msat_runner
import wcnf


# SPU class
###############################################################################


class Spu():
    """This class represents a list of packages to be installed.
    The packages are labeled by their name.
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
        self.pkg_toinstall = []
        reader = (l for l in (ll.strip() for ll in stream) if l)
        for line in reader:
            words = line.split()
            if words[0] == 'p':
                self.n_pkg = int(words[2])
            elif words[0] == 'n':
                self.pkg_toinstall.append(words[1])
            elif words[0] == 'd':
                self.dependencies.append((words[1], words[2:]))
            else:  # c conflicts
                self.conflicts.append((words[1], words[2]))
        self.pkg_toinstall = set(self.pkg_toinstall)
        if self.n_pkg != len(self.pkg_toinstall):
            print("Warning incorrect number of packages")


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
            from graphviz import Digraph
        except ImportError:
            msg = (
                "Could not import 'graphviz' module. "
                "Make shure 'graphviz' is installed "
                "or install it typing 'pip install graphviz'"
            )
            raise ImportError(msg)
        # Create graph
        dot = Digraph()
        # Create nodes
        for node in self.pkg_toinstall:
            dot.node(node)
        # Create edges
        for node1, ns2 in self.dependencies:
            for node2 in ns2:
                dot.edge(str(node1), str(node2))
        for node1, node2 in self.conflicts:
            dot.edge(node1, node2, color='Red')
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
        formula = wcnf.WCNFFormula()
        generated = collections.defaultdict(formula.new_var)
        list(map(lambda pkg: formula.add_clause([generated[pkg]], weight=1),
                 self.pkg_toinstall))
        func = lambda pkgs: formula.add_clause([-generated[pkgs[0]],
                                                *[generated[x] for x
                                                  in pkgs[1]]],
                                               weight=wcnf.TOP_WEIGHT)
        list(map(func, self.dependencies))
        list(map(lambda pkgs: formula.add_clause([-generated[x] for x in pkgs],
                                                 weight=wcnf.TOP_WEIGHT),
                 self.conflicts))
        opt, model = solver.solve(formula)
        inv_map = {v: k for k, v in generated.items()}
        res = list(map(lambda x: inv_map[-x], filter(lambda x: x < 0, model)))
        res.sort()
        pkgs = ' '.join(res)
        return '\to ' + str(opt) +'\n\tv ' + pkgs

# Program main
###############################################################################


def main(argv=None):
    """ Main program """
    args = parse_command_line_arguments(argv)

    solver = msat_runner.MaxSATRunner(args.solver)
    spu = Spu(args.spu)
    if args.visualize:
        spu.visualize(os.path.basename(args.spu))

    pkg_dependencie = spu.package_dependencies(solver)
    print("PKG_DEPENDENCIES:\n", pkg_dependencie)



# Utilities
###############################################################################


def parse_command_line_arguments(argv=None):
    """ Parses CLI arguments """
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

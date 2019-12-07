#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import networkx as nx


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("num_nodes", type=int,
                        help="Number of nodes in the graph.")

    parser.add_argument("edge_prob", type=float,
                        help="Probability of edge creation.")

    parser.add_argument("-s", "--seed", type=int, default=123456,
                        help="Seed for the PRNG.")

    args = parser.parse_args()

    if not 0.0 <= args.edge_prob <= 1.0:
        print("Error: edge_prob range is [0.0, 1.0]")
        sys.exit(1)

    graph = nx.gnp_random_graph(args.num_nodes, args.edge_prob, args.seed)
    print("p dmg", len(graph), graph.size())
    for node1, node2 in graph.edges:
        print("e", node1+1, node2+1)

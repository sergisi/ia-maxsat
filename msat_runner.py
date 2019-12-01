# -*- coding: utf-8 -*-

# pylint: disable=missing-docstring

from __future__ import absolute_import, print_function

import os
import os.path
import subprocess
import sys
import tempfile

import wcnf


class MaxSATRunner(object):

    def __init__(self, solver):
        self._solver = solver

        if not is_executable(solver):
            raise ValueError("{0} is not executable".format(solver))

    @property
    def solver_path(self):
        return self._solver

    def solve(self, instance):
        """
        """
        if isinstance(instance, wcnf.WCNFFormula):
            with tempfile.NamedTemporaryFile(mode="wt", delete=False) as tmpf:
                instance.write_dimacs(tmpf)
            _instance = tmpf.name
        elif isinstance(instance, str):
            _instance = instance
        else:
            raise TypeError("instance must be WCNFFormula or str")


        cmd = [self._solver, _instance]
        with open(os.devnull, "w") as DEVNULL:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=DEVNULL,
                                    universal_newlines=True)

        out, _ = proc.communicate()
        opt, model = -1, []
        for line in out.split("\n"):
            if line.startswith("o "):
                opt = int(line.split()[1])
            elif line.startswith("v "):
                model = [int(v) for v in line.split()[1:]]

        return opt, model


def solve_formula(solver, formula):
    if isinstance(solver, MaxSATRunner):
        _solver = solver
    elif isinstance(solver, str):
        _solver = MaxSATRunner(solver)
    else:
        raise TypeError("solver must be MaxSATRunner or string")

    return _solver.solve(formula)


def is_executable(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)

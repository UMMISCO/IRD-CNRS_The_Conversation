#!/usr/bin/env python3
"""Rebuild the three figures. Offline - the fetch_*.py scripts are the only ones needing
network, and their output is kept under data/.

    python3 scripts/make_all.py
"""
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

for script in ("make_fig1_carte.py", "make_fig1bis_carte_structures.py", "make_fig2_anteriorite.py", "make_fig3_euro.py", "make_fig4_catastrophes.py"):
    print(script)
    sys.argv = [script]
    runpy.run_path(os.path.join(HERE, script), run_name="__main__")

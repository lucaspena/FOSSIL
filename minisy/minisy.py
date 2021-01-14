"""
Script to call from terminal and run miniature SyGuS engine.
Argument after script call should be the name of the input file containing
SyGuS grammar descriptions. The engine will write a file with the SyGuS grammars
replaced by constraint grammars (with the synthesized lemmas). A solver (currently
only CVC4) is then called on the written file to determine satisfiability.
If sat, then the solver's model is obtained and applied to each synthesized lemma,
then printed to the terminal.
"""

import sys
import os

from minisy.minisy_utils import *

args = sys.argv[1:]
if args:
    infile_name = os.path.basename(args[0])
    # For now, create tmp folder in the same folder as the input file
    infile_dirname = os.path.dirname(args[0])
    outfile_dirname = os.path.join(infile_dirname, 'tmp')
    os.makedirs(outfile_dirname, exist_ok=True)
    smtfile_name = get_outfile_name(infile_name)
    outfile_full_name = os.path.join(outfile_dirname, smtfile_name)
    grammars = sygus_to_constraint(args[0], outfile_full_name)
    model = call_solver(outfile_full_name, grammars)

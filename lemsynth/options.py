# This is an options module that is used by the lemma synthesis source code.
# TODO: move the material here into a config file format with library support, say json or toml

import os
import importlib_resources

# SyGuS solver that supports only ground constraints and uses constraint-solving methods
minisy = 'minisy'
# Enumerative general-purpose SyGuS solver
cvc4sy = 'cvc4sy'

###############################################################################
# Setting lemma synthesis options here. DO NOT MODIFY.
streaming_synthesis_swtich = False
use_cex_models = False
synthesis_solver = minisy
# Verbosity as a positive number. 0 is completely silent.
verbose = 0

use_cex_true_models = True
###############################################################################

log_file_path = os.path.abspath(importlib_resources.files('lemsynth')/'../logs')

debug = True

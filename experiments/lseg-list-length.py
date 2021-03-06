import importlib_resources
from z3 import *
from lemsynth.lemsynth_engine import *

####### Section 0
# some general FOL macros
# TODO: move to utils
def Iff(b1, b2):
    return And(Implies(b1, b2), Implies(b2, b1))

def IteBool(b, l, r):
    return And(Implies(b, l), Implies(Not(b), r))

# Datastructure initialisations Below are some dictionaries being
# initialised. Will be updated later with constants/functions/definitions of
# different input/output signatures

# fcts_z3 holds z3 function/predicate/recursive definition symbols.
# The signatures are written as
# <arity>_<input-tuple-type_underscore-separated>_<output-type>
# for non-recursive functions. Signatures are
# <rec*>_<arity>_<input-tuple-type_underscore-separated>_<output-type>
# forrecursive functions/predicates where <rec*> is a string starting with rec
fcts_z3 = {}

# Axioms always provide boolean output and may have different signatures for inputs
# Z3 axioms return z3's boolean type and the python version returns a boolean value
axioms_z3 = {}
axioms_python = {}

# Unfolding recursive definitions.

# The Z3 version says that the recursive call and its unfolding are equivalent
# The python version computes the value based on one level of unfolding given a
# concrete model
unfold_recdefs_z3 = {}
unfold_recdefs_python = {}

# NOTE: All axioms as well as unfoldings will only take one argument 'w'
# corresponding to the input parameters (apart from the model argument for the
# python versions). For those that require multiple arguments, this will be
# packed into a tuple before calling the functions/axioms.

######## Section 1
# Variables and Function Symbols

# The z3py variable for a z3 variable will be the same as its string value.
# So we will use the string 'x' for python functions and just x for creating z3 types
x, y, z, nil = Ints('x y z nil')
fcts_z3['0_int'] = [x, y, z, nil]

######## Section 2
# Functions
next = Function('next', IntSort(), IntSort())

# Axioms for next and prev of nil equals nil as z3py formulas
next_nil_z3 = next(nil) == nil

# Python version for the axioms above
def next_nil_python(model):
    return model['next'][model['nil']] == model['nil']

# Updating fcts and fct_Axioms for next and next_p
# TODO: change signature to have 'loc' rather than 'int'
fcts_z3['1_int_int'] = [next]
axioms_z3['0'] = [next_nil_z3]
axioms_python['0'] = [next_nil_python]

######## Section 3
# Recursive definitions

# Recdefs can only be unary (on the foreground sort?)
# TODO: add support for recursive functions
list = Function('list', IntSort(), BoolSort())
lseg_y = Function('lseg_y', IntSort(), BoolSort())
lseglen_y_bool = Function('lseglen_y_bool', IntSort(), BoolSort())
lseglen_y_int = Function('lseglen_y_int', IntSort(), IntSort())
length = Function('length', IntSort(), IntSort())

############ Section 4
# Unfolding recursive definitions
# TODO: Must add support for recursive functions

# Macros for unfolding recursive definitions
def ulist_z3(x):
    return Iff( list(x), IteBool(x == nil, True, list(next(x))) )

def ulseg_y_z3(x):
    return Iff( lseg_y(x), IteBool(x == y, True, lseg_y(next(x))) )

def ulseglen_y_bool_z3(x):
    return Iff( lseglen_y_bool(x), IteBool(x == y, True, lseglen_y_bool(next(x))) )

def ulseglen_y_int_z3(x):
    is_y = x == y
    in_domain = lseglen_y_bool(x)
    then_case = Implies(is_y, lseglen_y_int(x) == 0)
    else_case = Implies(Not(is_y), lseglen_y_int(x) == lseglen_y_int(next(x)) + 1)
    return Implies(in_domain, And(then_case, else_case))

def ulength_z3(x):
    is_nil = x == nil
    then_case = Implies(is_nil, length(x) == 0)
    else_case = Implies(Not(is_nil), length(x) == length(next(x)) + 1)
    return And(then_case, else_case)

# Python versions for finding valuation on true models
def ulist_python(x, model):
    if x == model['nil']:
        return True
    else:
        next_val = model['next'][x]
        return model['list'][next_val]

def ulseg_y_python(x, model):
    if x == model['y']:
        return True
    else:
        next_val = model['next'][x]
        return model['lseg_y'][next_val]

def ulseglen_y_bool_python(x, model):
    if x == model['y']:
        return True
    else:
        next_val = model['next'][x]
        return model['lseglen_y_bool'][next_val]

def ulseglen_y_int_python(x, model):
    if x == model['y']:
        return 0
    else:
        next_val = model['next'][x]
        curr_lseglen_y_int = model['lseglen_y_int'][x]
        next_lseglen_y_int = model['lseglen_y_int'][next_val]
        curr_lseglen_y_bool = model['lseglen_y_bool'][x]
        if curr_lseglen_y_bool:
            return next_lseglen_y_int + 1
        else:
            return curr_lseglen_y_int

def ulength_python(x, model):
    if x == model['nil']:
        return 0
    else:
        next_val = model['next'][x]
        curr_len = model['length'][x]
        next_len = model['length'][next_val]
        curr_list = model['list'][x]
        if curr_list:
            return next_len + 1
        else:
            return curr_len

unfold_recdefs_z3['1_int_bool'] = [ulist_z3, ulseg_y_z3, ulseglen_y_bool_z3]
unfold_recdefs_python['1_int_bool'] = [ulist_python, ulseg_y_python, ulseglen_y_bool_python]
unfold_recdefs_z3['1_int_int'] = [ulseglen_y_int_z3, ulength_z3]
unfold_recdefs_python['1_int_int'] = [ulseglen_y_int_python, ulength_python]
pfp_dict = {}
pfp_dict['list'] = '''
(=> (ite (= {primary_arg} {nil})
         true
         (and (list (next {primary_arg})) (lemma (next {primary_arg}) {rest_args})))
    (lemma {primary_arg} {rest_args}))'''

pfp_dict['lseg_y'] = '''
(=> (ite (= {primary_arg} {y})
         true
         (and (lseg_y (next {primary_arg})) (lemma (next {primary_arg}) {rest_args})))
    (lemma {primary_arg} {rest_args}))'''

pfp_dict['lseglen_y_bool'] = '''
(=> (ite (= {primary_arg} {y})
         true
         (and (lseglen_y_bool (next {primary_arg})) (lemma (next {primary_arg}) {rest_args})))
    (lemma {primary_arg} {rest_args}))'''

# Recall recursive predicates are always unary
fcts_z3['recpreds-loc_1_int_bool'] = [list, lseg_y, lseglen_y_bool]
fcts_z3['recfunctions-loc_1_int_int'] = [lseglen_y_int, length]

############# Section 5
# Program, VC, and Instantiation

# lemma: lseg(x,y) /\ list(x) -> length(x) = lseg-len(x, y) + length(y)

def pgm(x, y, z):
    return And( lseg_y(x), next(y) == z, list(z) )

def vc(x, y, z):
    return Implies( pgm(x, y, z), length(x) == lseglen_y_int(x) + length(y) )

deref = [x]
const = [nil, y]
verification_condition = vc(x,y,z)

# End of input

###########################################################################################################################
# Lemma synthesis stub 
##########################################################################################################################

config_params = {'mode': 'random', 'num_true_models':0}
config_params['pfp_dict'] = pfp_dict
config_params['use_cex_models'] = True

name = 'lseg-list-length'
grammar_string = importlib_resources.read_text('experiments', 'grammar_{}.sy'.format(name))

synth_dict = {}

solveProblem(fcts_z3, axioms_python, axioms_z3, unfold_recdefs_z3, unfold_recdefs_python, deref, const, verification_condition, name, grammar_string, config_params, synth_dict)

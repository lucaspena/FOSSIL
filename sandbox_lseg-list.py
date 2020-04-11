from z3 import *
from sandbox_lemma_synthesis import *
from sandbox_true_models import *


####### Section 0
# some general FOL macros
def Iff(b1, b2):
    return And(Implies(b1, b2), Implies(b2, b1))

def IteBool(b, l, r):
    return And(Implies(b, l), Implies(Not(b), r))

# Datastructure initialisations
# Below are some dictionaries being initialised. Will be updated later with constants/functions/definitions of different input/output signatures

# fcts_z3 holds z3 function/predicate/recursive definition symbols.
# The signatures are written as <arity>_<input-tuple-type_underscore-separated>_<output-type> for non recursive functions
# Signatures are <rec*>_<arity>_<input-tuple-type_underscore-separated>_<output-type> for recursive functions/predicates where <rec*> is a string starting with rec
fcts_z3 = {}
# Axioms always provide boolean output and may have different signatures for inputs
axioms_z3 = {}
axioms_python = {} #Z3 axioms return z3's boolean type and the python version returns a boolean value
# Unfolding recursive definitions.
# The Z3 version says that the recursive call and its unfolding are equal (or bi-implication if predicate)
# The python version computes the value based on one level of unfolding
unfold_recdefs_z3 = {}
unfold_recdefs_python = {}

# NOTE: All axioms (both z3 and python versions) as well as the unfoldings (both z3 and python versions)
## will only take one argument 'w' corresponding to the input parameters (apart from the model argument for the python versions).
## For those that require multiple arguments, this will be packed into a tuple before calling the functions/axioms.


######## Section 1
# Variables and Function Symbols

# The z3py variable for a z3 variable will be the same as its string value.
# So we will use the string 'x' for python functions and just x for creating z3 types
x, y, z, nil = Ints('x y z nil')
fcts_z3['0_int'] = [x,y,z,nil]
####### Section 2
## Functions
next = Function('next', IntSort(), IntSort())
next_p = Function('next_p', IntSort(), IntSort())

# Axiom for nexty with ite
def next_p_fct_axiom_z3(w):
    return IteBool(w == y, next_p(w) == z, next_p(w) == next(w))
# Python version for the above axiom for true model generation
def next_p_fct_axiom_python(w,model):
    if w == model['y']:
        return model['next_p'][w] == model['z']
    else:
        return model['next_p'][w] == model['next'][w]

# Axioms for next and prev of nil equals nil as python functions -
axiomNextNil_z3 = next(nil) == nil
axiomNextpNil_z3 = next_p(nil) == nil
# Python version for the axioms above
def axiomNextNil_python(model):
    return model['next'][model['nil']] == model['nil']

def axiomNextpNil_python(model):
    return model['next_p'][model['nil']] == model['nil']

# Updating fcts and fct_Axioms for next and next_p
# Use dict.setdefault to be able to update the dictionary in multiple stages
# Must change signature to have 'loc' rather than 'int' once types are changed for the location variables
fcts_z3['1_int_int'] = [next, next_p]
axioms_z3['0'] = [axiomNextNil_z3, axiomNextpNil_z3]
axioms_z3['1_int'] = [next_p_fct_axiom_z3]
axioms_python['0'] = [axiomNextNil_python, axiomNextpNil_python]
axioms_python['1_int'] = [next_p_fct_axiom_python]

########Section 3
## Recursive definitions
# Recdefs can only be unary (on the foreground sort?)
# TODO: Must add support for recursive functions

list = Function('list', IntSort(), BoolSort())
lsegy = Function('lsegy', IntSort(), BoolSort())
list_p = Function('list_p', IntSort(), BoolSort())
lsegy_p = Function('lsegy_p', IntSort(), BoolSort())

# Axioms about recdefs
axiomLsegyNil_z3 = lsegy(nil) == False
axiomLsegypNil_z3 = lsegy_p(nil) == False
# Python versions of axioms
def axiomLsegyNil_python(model):
    return model['lsegy'][model['nil']] == False
def axiomLsegypNil_python(model):
    return model['lsegy_p'][model['nil']] == False

axioms_z3['0'] = axioms_z3['0'] + [axiomLsegyNil_z3,axiomLsegypNil_z3]
axioms_python['0'] = axioms_python['0'] + [axiomLsegyNil_python,axiomLsegypNil_python]


############ Section 4
# Unfolding recursive definitions
# TODO: Must add support for recursive functions

# Macros for unfolding recursive definitions
def ulist_z3(x):
    return Iff( list(x), IteBool(x == nil, True, list(next(x))) )

def ulsegy_z3(x):
    return Iff( lsegy(x), IteBool(x == y, True, lsegy(next(x))) )

def ulist_p_z3(x):
    return Iff( list_p(x), IteBool(x == nil, True, list_p(next_p(x))) )

def ulsegy_p_z3(x):
    return Iff( lsegy_p(x), IteBool(x == y, True, lsegy_p(next_p(x))) )

# Python versions for finding valuation on true models
def ulist_python(x, model):
    if x == model['nil']:
        return True
    else:
        next_val = model['next'][x]
        return model['list'][next_val]

def ulsegy_python(x, model):
    if x == model['y']:
        return True
    else:
        next_val = model['next'][x]
        return model['lsegy'][next_val]

def ulist_p_python(x, model):
    if x == model['nil']:
        return True
    else:
        next_val = model['next_p'][x]
        return model['list_p'][next_val]

def ulsegy_p_python(x, model):
    if x == model['y']:
        return True
    else:
        next_val = model['next_p'][x]
        return model['lsegy_p'][next_val]

unfold_recdefs_z3['1_int_bool'] = [ulist_z3, ulsegy_z3, ulist_p_z3, ulsegy_p_z3]
unfold_recdefs_python['1_int_bool'] = [ulist_python, ulsegy_python, ulist_p_python, ulsegy_p_python]


# Recursive predicates are only unary, so there's no signature apart from the fact that
## they are predicates on the loc sort
fcts_z3['recpreds-loc_1_int_bool'] = [list,lsegy,list_p,lsegy_p]

############# Section 5
# Program, VC and Instantiation

def pgm(x, y, z):
    return And( lsegy(x), next(y) == nil, list(z) )

def vc(x, y, z):
    return Implies( pgm(x, y, z), list_p(x) )


deref = [x,next(x)]
const = [nil, y]
elems = [*range(3)]
num_true_models = 10


lemma = getSygusOutput(elems, num_true_models, fcts_z3, axioms_python, axioms_z3, unfold_recdefs_z3, unfold_recdefs_python, deref, const, vc(x,y,z), 'lseg-list')

#print(lemma)

# TODO: enforce small false model?
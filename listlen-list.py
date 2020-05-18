from z3 import *
from lemma_synthesis import *
from true_models import *

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
x, ret, nil = Ints('x ret nil')
fcts_z3['0_int'] = [x, ret, nil]

####### Section 2
# Functions
next = Function('next', IntSort(), IntSort())

# Axioms for next and next' of nil equals nil as z3py formulas
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
listlen_bool = Function('listlen_bool', IntSort(), BoolSort())
listlen_int = Function('listlen_int', IntSort(), IntSort())


############ Section 4
# Unfolding recursive definitions
# TODO: add support for recursive functions

# Macros for unfolding recursive definitions
def ulist_z3(x):
    return Iff( list(x), IteBool(x == nil, True, list(next(x))) )

def ulistlen_bool_z3(x):
    return Iff( listlen_bool(x), IteBool(x == nil, True, listlen_bool(next(x))) )

def ulistlen_int_z3(x):
    cond = x == nil
    then_case = Implies(cond, listlen_int(x) == 0)
    else_case = Implies(Not(cond), listlen_int(x) == listlen_int(next(x)) + 1)
    return And(then_case, else_case)

# Python versions for finding valuation on true models
def ulist_python(x, model):
    if x == model['nil']:
        return True
    else:
        next_val = model['next'][x]
        return model['list'][next_val]

def ulistlen_bool_python(x, model):
    if x == model['nil']:
        return True
    else:
        next_val = model['next'][x]
        return model['listlen_bool'][next_val]

def ulistlen_int_python(x, model):
    if x == model['nil']:
        return 0
    else:
        next_val = model['next'][x]
        return model['listlen_int'][next_val] + 1

unfold_recdefs_z3['1_int_bool'] = [ulist_z3, ulistlen_bool_z3]
unfold_recdefs_python['1_int_bool'] = [ulist_python, ulistlen_bool_python]

unfold_recdefs_z3['1_int_int'] = [ulistlen_int_z3]
unfold_recdefs_python['1_int_int'] = [ulistlen_int_python]

# Recall recursive predicates are always unary
fcts_z3['recpreds-loc_1_int_bool'] = [list, listlen_bool]
fcts_z3['recfunctions-loc_1_int_int'] = [listlen_int]

############# Section 5
# Program, VC, and Instantiation

def pgm(x, ret):
    return IteBool(listlen_int(x) == 1, ret == x, ret == next(x))

def vc(x, ret):
    return Implies( listlen_bool(x), Implies( pgm(x, ret), list(x) ) )

deref = [x]
const = [nil]
elems = [*range(3)]
num_true_models = 'full'

# valid and invalid lemmas
valid_lemmas = []
invalid_lemmas = []


# # continuously get valid lemmas until VC has been proven
# while True:
#     lemmas = getSygusOutput(elems, num_true_models, fcts_z3, axioms_python, axioms_z3,
#                             valid_lemmas, unfold_recdefs_z3, unfold_recdefs_python, deref, const,
#                             vc(x,y,z), 'lseg-list')
#     lemmas = lemmas + ['(define-fun lemma ((x Int) (nil Int) (y Int)) Bool (=> (lsegy_p x) (=> (list_p y) (list_p x))))']
#     print('Lemmas: {}'.format(lemmas))
#     for lemma in lemmas:
#         z3py_lemma = translateLemma(lemma, fcts_z3)
#         if z3py_lemma in invalid_lemmas:
#             print('lemma has already been proposed')
#             continue
#         model = getFalseModel(axioms_z3, fcts_z3, valid_lemmas, unfold_recdefs_z3, deref, const, z3py_lemma, True)
#         if model != None:
#             print('proposed lemma cannot be proved.')
#             invalid_lemmas = invalid_lemmas + [ z3py_lemma ]
#             # TODO: add to bag of unwanted lemmas (or add induction principle of lemma to axioms)
#             # and continue
#         else:
#             valid_lemmas = valid_lemmas + [ z3py_lemma ]
#             break
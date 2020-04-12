from z3 import *
from lemma_synthesis import *
from natural_proofs import *

# functions
next = Function('next', IntSort(), IntSort())
prev = Function('prev', IntSort(), IntSort())
key = Function('key', IntSort(), IntSort())

fcts = ['next', 'prev', 'key']
fct_axioms = [next(-1) == -1, prev(-1) == -1, key(-1) == -1]

# axioms for next and prev of nil equals nil as python functions -
# for true model generation
def axiomNextNil(model):
    return model['next'][-1] == -1

def axiomPrevNil(model):
    return model['prev'][-1] == -1

def axiomKeyNil(model):
    return model['key'][-1] == -1

vc_axioms  = [axiomNextNil, axiomPrevNil, axiomKeyNil]

# recursive definitions
dlist = Function('dlist', IntSort(), BoolSort())
slist = Function('slist', IntSort(), BoolSort())
sdlist = Function('sdlist', IntSort(), BoolSort())

# some general FOL macros
def Iff(b1, b2):
    return And(Implies(b1, b2), Implies(b2, b1))

def IteBool(b, l, r):
    return And(Implies(b, l), Implies(Not(b), r))

# macros for unfolding recursive definitions
def udlist(x):
    return Iff( dlist(x), IteBool( x == -1,
                                   True,
                                   IteBool( next(x) == -1,
                                            True,
                                            And(prev(next(x)) == x, dlist(next(x))) ))
   )

def uslist(x):
    return Iff( slist(x), IteBool( x == -1,
                                   True,
                                   IteBool( next(x) == -1,
                                            True,
                                            And(key(x) <= key(next(x)), slist(next(x))) ))
   )

def usdlist(x):
    rho = IteBool( x == -1,
                   True,
                   IteBool( next(x) == -1,
                            True,
                            And(key(x) <= key(next(x)),
                                prev(next(x)) == x, sdlist(next(x))) ))
    return Iff(sdlist(x), rho)

recdefs_macros = [udlist, uslist, usdlist]

# for producing true models: functional versions of recursive definitions
def dlist_fct(x, model):
    if x == -1:
        return True
    elif model['next'][x] == -1:
        return True
    else:
        next_val = model['next'][x]
        doubly_linked_cond = model['prev'][next_val] == x
        return doubly_linked_cond and model['dlist'][next_val]

def slist_fct(x, model):
    if x == -1:
        return True
    elif model['next'][x] == -1:
        return True
    else:
        next_val = model['next'][x]
        sorted_cond = model['key'][x] <= model['key'][next_val]
        return sorted_cond and model['slist'][next_val]
    
def sdlist_fct(x, model):
    if x == -1:
        return True
    elif model['next'][x] == -1:
        return True
    else:
        next_val = model['next'][x]
        sorted_cond = model['key'][x] <= model['key'][next_val]
        doubly_linked_cond = model['prev'][next_val] == x
        return sorted_cond and doubly_linked_cond and model['sdlist'][next_val]

recdefs = [dlist_fct, slist_fct, sdlist_fct]

# string representation of recursive definition
# TODO: do this in a more systematic way
recdef_str = { dlist_fct : 'dlist', slist_fct : 'slist', sdlist_fct : 'sdlist' }

# Z3Py representation of strings (for converting internal model to Z3Py model)
z3_str = { 'dlist' : dlist, 'slist' : slist, 'sdlist' : sdlist, 'next' : next, 'prev' : prev, 'key' : key }

# VC
def pgm(x, ret):
    return IteBool(x == -1, ret == -1, ret == next(x))

def vc(x, ret):
    return Implies( sdlist(x),
                    Implies(pgm(x, ret), And(dlist(ret), slist(ret))))

x, ret = Ints('x ret')
deref = [x]
const = [-1]
elems = [-1, *range(2)]

# translate output of cvc4 into z3py form
def translateLemma(lemma):
    smt_string = lemma + ' (assert (forall ((x Int)) (lemma x)))'
    z3py_lemma = parse_smt2_string(smt_string, decls=z3_str)[0]
    print(z3py_lemma)
    model = proveVC(fct_axioms, z3_str, recdefs_macros, deref, const, z3py_lemma, True)
    if model == None:
        # TODO: check if lemma is valid/provable
        return z3py_lemma
    else:
        print('proposed lemma cannot be proved.')
        # TODO: add to bag of unwanted lemmas
        exit(0)

while True:
    lemma = getSygusOutput(elems, fcts, vc_axioms, fct_axioms, recdefs_macros, recdefs,
                           recdef_str, deref, const, vc(x, ret), z3_str,
                           'preamble_sdlist-dlist-and-slist.sy',
                           'grammar_sdlist-dlist-and-slist.sy',
                           'out_sdlist-dlist-and-slist.sy')
    z3py_lemma = translateLemma(lemma)
    fct_axioms = fct_axioms + [ z3py_lemma ]

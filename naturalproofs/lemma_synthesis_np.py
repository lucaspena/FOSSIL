from z3 import *

from lemsynth.lemma_synthesis import *
from lemsynth.lemsynth_utils import *

from naturalproofs.AnnotatedContext import default_annctx
from naturalproofs.pfp import make_pfp_formula
from naturalproofs.prover import NPSolver

from naturalproofs.decl_api import Const
from naturalproofs.uct import fgsort
from naturalproofs.extensions.finitemodel import extract_finite_model

def solveProblem(axioms_python, unfold_recdefs_python, lemma_args, model_terms, goal, name, grammar_string, config_params, annctx=default_annctx):

    # Extract relevant parameters for running the verification-synthesis engine from synth_dict
    valid_lemmas = set()
    invalid_lemmas = []
    use_cex_models = config_params.get('use_cex_models', True)
    cex_models = config_params.get('cex_models',[])

    # check if goal is provable on its own using induction
    pfp_of_goal = make_pfp_formula(goal)
    npsolver = NPSolver()
    npsolution = npsolver.solve(pfp_of_goal)

    if npsolution.if_sat:
        print('vc cannot be proved using induction.')
    else:
        print('vc is provable using induction.')
        exit(0)

    # continuously get valid lemmas until VC has been proven
    while True:
        lemma = getSygusOutput(axioms_python, valid_lemmas, unfold_recdefs_python, lemma_args, model_terms, goal, name, grammar_string, config_params, annctx)
        if lemma is None:
            print('CVC4 SyGuS returns unknown. Exiting.')
            exit('Instance failed.')

        # convert CVC4 versions of membership, insertion to z3py versions
        SetIntSort = createSetSort('int')
        membership = Function('membership', IntSort(), SetIntSort, BoolSort())
        insertion = Function('insertion', IntSort(), SetIntSort, SetIntSort)
        addl_decls = {'member' : membership, 'insert' : insertion}
        swap_fcts = {insertion : SetAdd}
        replace_fcts = {membership : IsMember}

        # testing translation of lemma
        rhs_lemma = translateLemma(lemma[0], lemma_args, addl_decls, swap_fcts, replace_fcts, annctx)
        index = int(lemma[1][-2])
        recs = get_recursive_definition(None, True, annctx)
        vocab = get_vocabulary(annctx)
        vocab_dict = {v.name() : v for v in vocab}
        var = vocab_dict['x']
        lhs = sorted(recs, key=lambda x: x[0].name())[index][0]
        lhs_arity = lhs.arity()
        lhs_lemma_args = tuple(lemma_args[:lhs_arity])
        lhs_lemma = lhs(lhs_lemma_args)
        z3py_lemma = Implies(lhs_lemma, rhs_lemma)

        print('proposed lemma: ' + str(z3py_lemma))
        if z3py_lemma in invalid_lemmas or z3py_lemma in valid_lemmas:
            print('lemma has already been proposed')
            if use_cex_models:
                if z3py_lemma in invalid_lemmas:
                    print('Something is wrong. Lemmas should not be reproposed in the presence of countermodels. Exiting.')
                if z3py_lemma in valid_lemmas:
                    print('This is a currently known limitation of the tool. Consider restricting your grammar to have terms of lesser height.')
                exit('Instance failed.')
            else:
                # Using bag-of-lemmas + prefetching formulation, or the reproposed lemma is a valid one. Continue and hope for the best.
                continue
        pfp_lemma = make_pfp_formula(z3py_lemma)
        npsolution = npsolver.solve(pfp_lemma)
        npmodel = npsolution.model
        false_model_dict = extract_finite_model(npmodel, model_terms)
        if npsolution.if_sat:
            print('proposed lemma cannot be proved.')
            invalid_lemmas = invalid_lemmas + [ z3py_lemma ]
            if use_cex_models:
                cex_models = cex_models + [ false_model_dict ]
        else:
            valid_lemmas.add((tuple(lemma_args), z3py_lemma))
            # check if new valid lemma helped prove original VC
            # TODO: currently this check is done in getSygusOutput. Should be moved here
            lemma_solution = npsolver.solve(goal, valid_lemmas)
            if not lemma_solution.if_sat:
                print('Original goal is proved. Lemmas used to prove goal:')
                for lemma in valid_lemmas:
                    print(lemma[1])
            exit(0)
            
            # Reset countermodels and invalid lemmas to empty because we have additional information to retry those proofs.
            cex_models = []
            invalid_lemmas = []
        # Update countermodels before next round of synthesis
        config_params['cex_models'] = cex_models
        
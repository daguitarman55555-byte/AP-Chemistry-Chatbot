"""Bounded arithmetic checking: no eval, code execution, or hidden result returned."""
import ast
import math
import operator

OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Pow:operator.pow}
FUNCS={'sqrt':math.sqrt,'ln':math.log,'log10':math.log10,'exp':math.exp,'abs':abs}

def arithmetic(expression):
    if not isinstance(expression,str) or len(expression)>300: raise ValueError('Expression must be at most 300 characters')
    tree=ast.parse(expression,mode='eval')
    if sum(1 for _ in ast.walk(tree))>80: raise ValueError('Too many operations')
    def visit(node):
        if isinstance(node,ast.Constant) and type(node.value) in (int,float): value=float(node.value)
        elif isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            value=visit(node.operand)*(1 if isinstance(node.op,ast.UAdd) else -1)
        elif isinstance(node,ast.BinOp) and type(node.op) in OPS:
            left,right=visit(node.left),visit(node.right)
            if isinstance(node.op,ast.Pow) and abs(right)>100: raise ValueError('Exponent outside bounds')
            value=OPS[type(node.op)](left,right)
        elif isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in FUNCS and len(node.args)==1 and not node.keywords:
            value=FUNCS[node.func.id](visit(node.args[0]))
        else: raise ValueError('Use numbers, + - * / **, sqrt, ln, log10, exp, or abs only')
        if type(value) not in (int,float) or not math.isfinite(value) or abs(value)>1e100:
            raise ValueError('Result is not a finite real number within bounds')
        return value
    try: return visit(tree.body)
    except (ArithmeticError,TypeError) as exc: raise ValueError('Expression is outside its mathematical domain') from exc

def check_step(expression,claimed):
    if type(claimed) not in (int,float) or not math.isfinite(claimed): raise ValueError('Supply a finite claimed result')
    try: actual=arithmetic(expression)
    except (SyntaxError,ValueError) as exc: return {'status':'invalid_step','message':str(exc)}
    correct=math.isclose(actual,claimed,rel_tol=1e-5,abs_tol=max(abs(actual)*1e-10,1e-300))
    return {'status':'arithmetic_matches' if correct else 'check_arithmetic',
            'message':('Your arithmetic matches. This does not verify the chemistry equation or units.' if correct else 'Recheck the arithmetic and parentheses. The calculated result stays hidden.'),
            'verification_scope':'arithmetic_only'}

# A formula grammar for conservation checks, not a reaction predictor or laboratory guide.
import re
from collections import Counter
ELEMENTS=set('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og'.split())

def formula_counts(formula):
    if not isinstance(formula,str) or not 1<=len(formula)<=100: raise ValueError('Formula must be 1–100 characters')
    formula=re.sub(r'\((?:aq|s|l|g)\)$','',formula.strip())
    if formula=='e^-': return {},-1
    charge=0;match=re.search(r'\^(\d*)([+-])$',formula)
    if match:
        magnitude=int(match[1] or '1')
        if not 1<=magnitude<=20: raise ValueError('Charge outside supported range')
        charge=magnitude*(1 if match[2]=='+' else -1);formula=formula[:match.start()]
    tokens=re.findall(r'[A-Z][a-z]?|\d+|[()]',formula)
    if ''.join(tokens)!=formula: raise ValueError('Use element symbols, parentheses, and charges such as Fe^3+; hydration dots and isotope notation are not supported')
    stack=[Counter()];i=0
    while i<len(tokens):
        token=tokens[i]
        if token=='(':
            if len(stack)>8: raise ValueError('Formula nesting too deep')
            stack.append(Counter());i+=1;continue
        if token==')':
            if len(stack)==1 or not stack[-1]: raise ValueError('Unmatched or empty parentheses')
            group=stack.pop()
        elif token in ELEMENTS:group=Counter({token:1})
        else:raise ValueError('Unknown element or misplaced subscript')
        i+=1;factor=1
        if i<len(tokens) and tokens[i].isdigit():factor=int(tokens[i]);i+=1
        if not 1<=factor<=1000: raise ValueError('Subscript outside supported range')
        for element,n in group.items():
            stack[-1][element]+=n*factor
            if stack[-1][element]>100000: raise ValueError('Atom count outside supported range')
    if len(stack)!=1 or not stack[0]: raise ValueError('Unmatched parentheses or empty formula')
    return dict(stack[0]),charge

def check_balance(equation):
    if not isinstance(equation,str) or len(equation)>1000: raise ValueError('Equation must be at most 1000 characters')
    sides=re.split(r'\s*(?:<->|->|→|⇌)\s*',equation)
    if len(sides)!=2: raise ValueError('Use one reaction arrow: ->')
    totals=[]
    for side in sides:
        terms=re.split(r'\s+\+\s+',side.strip())
        if not 1<=len(terms)<=12: raise ValueError('Use at most 12 species per side')
        atoms=Counter();charge=0
        for term in terms:
            m=re.fullmatch(r'(?:(\d+)\s*)?(.+)',term)
            if not m: raise ValueError('Missing species')
            coefficient=int(m[1] or '1')
            if not 1<=coefficient<=1000: raise ValueError('Use positive integer coefficients up to 1000')
            counts,z=formula_counts(m[2]);atoms.update({e:coefficient*n for e,n in counts.items()});charge+=coefficient*z
        totals.append((atoms,charge))
    mismatched=sorted(e for e in totals[0][0].keys()|totals[1][0].keys() if totals[0][0][e]!=totals[1][0][e])
    charge_matches=totals[0][1]==totals[1][1]
    balanced=not mismatched and charge_matches
    return dict(status='conserved' if balanced else 'not_conserved',
        message='Atoms and charge are conserved. This does not establish that the reaction occurs or that coefficients are the smallest integers.' if balanced else 'Recheck conservation of '+(', '.join(mismatched+([] if charge_matches else ['charge'])))+'. Coefficients stay for you to determine.',
        verification_scope='atom_and_charge_conservation_only')

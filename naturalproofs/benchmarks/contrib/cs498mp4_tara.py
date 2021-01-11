# -*- coding: utf-8 -*-
"""CS498MP4 - Tara.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PvhHD-XxfWAjv7T0TfzGTfJhLl1CzlPJ

# **CS498MP4 Project (Fall 2020)** 
# Completeness Procedure for Groups, Rings, and Fields

Submitted by **Tara Vijaykumar** *(tgv2@illinois.edu)*

Link to run: https://colab.research.google.com/drive/1PvhHD-XxfWAjv7T0TfzGTfJhLl1CzlPJ?usp=sharing


---

# Contents

1.   Introduction
2.   Requirements
3.   Groups & Group Theories
4.   Rings & Ring Theories 
5.   Variant: Commutative Rings
6.   Fields & Field Theories
7.   References



---

# Introduction

In class, we learned how to prove the validity of a first-order formula by following a completeness procedure that negaes it, Skolemizes it, uses systematic term instatiation to convert it to a quantifier free formula, and checks whether the quantifier-free formula is unsatisfiable using Z3. By showing that the set of axioms of the negated formula along with the others are unsatisfiable, we prove that the original formula must be valid. 

In this project, I attempt to extend this completeness procedure for groups, rings, and fields, modularize the various properties into functions, automate the process of term instantiation (for depths 0 and 1) and use these to prove the original formula valid, by showing that the set of axioms that contain its negation is unsatisfiable.

The project has been implemented in Python with the Z3 library. The link to the Z3 API in Python is in the References section.


---

# Requirements

Packages that need to be installed to run this code.
"""

!pip install z3-solver
!pip install handcalcs

from z3 import *
import handcalcs.render

"""# **Groups & Group Theories**

To start off, I tried to redo the procedure we did in Homework 4 for Groups. This helped me get familiarized with using the Z3 API in Python before extending it to other variants.

**Groups**

A group is defined as a set $S$ endowed with a binary relation $\circ: S \times S \rightarrow S$ that satisfies the following properties:

*   Associativity: for every $a, b, c \in S,(a \circ b) \circ c=a \circ(b \circ c)$ 
*   Identity: There is an element $e \in S$ such that for every $a \in S, a \circ e=e \circ a=a$. 
*   Inverse: For every $a \in S,$ there exists an $a^{\prime} \in S$ such that $a \circ a^{\prime}=a^{\prime} \circ a=e$.

**Group Axioms**

Final axioms that were converted to prenex normal form and Skolemized:
1. Associativity: $\forall x, y, z . f(f(x, y), z)=f(x, f(y, z))$
2. Identity: $\forall x . f(x, e)=x \wedge f(e, x)=x$
3. Inverse: $\forall x  \cdot f(x, g(x))=e \wedge f(g(x), x)=e$

**Group Theories**

Final axioms that were converted to prenex normal form, negated, and Skolemized:
1. Under group axioms, identity is unique 

  $\begin{aligned} \varphi & \equiv \forall e^{\prime} .\left(\left(\forall x .\left(f\left(x, e^{\prime}\right)=x \wedge f\left(e^{\prime}, x\right)=x\right) \Rightarrow\left(e=e^{\prime}\right)\right)\right) \end{aligned}$

  Negated and skolemized: 

  $\forall x \cdot(f(x, c)=x \wedge f(c, x)=x \wedge \neg(e=c))$

2. Under group axioms, every element has only one inverse

  $\varphi: \forall x, y .(f(x, y)=e \wedge f(y, x)=e) \Rightarrow(y=g(x))$

  Negated and skolemized: 
 
  $(f(c, d)=e \wedge f(d, c)=e \wedge \neg(d=g(c)))$

3. If in a group G, $x$, $y$ and $z$ are three elements such that $x \circ y = z \circ y$, then $x = z$.

  $\varphi: \forall x, y, z .(f(x, y)=f(z,y)) \Rightarrow(x=z)$

  Negated and skolemized: 

  $f(c, d) = f(b, d) \wedge \neg(c = b)$

---

In the next few blocks, I will:
1. Define functions and constants
2. Define the properties for group axioms
3. Define a function to instantiate with depth 0 or 1
4. Prove the validity of the above 3 theories
---

Functions and constants
"""

f = Function('f', IntSort(), IntSort(), IntSort()) # binary function f(x, y)
g = Function('g', IntSort(), IntSort()) # inverse g(x)

c = Const('c', IntSort())
e = Const('e', IntSort())
d = Const('d', IntSort()) # identity

"""Group axioms"""

def associative(f, x, y, z):
   return f(f(x, y), z) == f(x, f(y, z))

def inverse(f, g, x):
  return And(f(x, g(x)) == e, f(g(x), x) == e)

def identity(f, x):
  return And(f(x, e) == x, f(e, x) == x)

"""Theories to prove (after negation and Skolemization)"""

def theory1(f, x):
  # Under group axioms, identity is unique
  return And(f(x, c) == x, f(c, x) == x, e != c)

def theory2(f, g):
  # Under group axioms, every element has only one inverse
  return And(f(c, d) == e, f(d, c) == e, d != g(c))

def theory3(f):
  # If in a group G, x, y and z are three elements such that x o y = z o y, then x = z
  return And(f(c, d) == f(e, d), c != e)

"""Instantiate to depth 0 and/or 1"""

def instantiate(functions, constants, depth = 0):
  f, g = functions[0], functions[1]

  if depth == 0: # ground terms only 
    insts = []
    for c1 in constants:
      insts.append(inverse(f, g, c1))
      insts.append(identity(f, c1))
      for c2 in constants:
        for c3 in constants:
          insts.append(associative(f, c1, c2, c3))
    return insts, constants

  if depth == 1: # ground terms and fucntions
    insts = []
    new_constants = constants.copy()
    for c1 in constants:
      new_constants.append(g(c1))
      for c2 in constants:
        new_constants.append(f(c1,c2))
    constants = new_constants

    for c1 in constants:
      insts.append(inverse(f, g, c1))
      insts.append(identity(f, c1))
      for c2 in constants:
        for c3 in constants:
          insts.append(associative(f, c1, c2, c3))
    return insts, constants

"""**Theory 1: Under group axioms, identity is unique**


"""

functions = [f, g]
constants = [c, e]
insts, constants = instantiate(functions, constants, depth = 0)

for constant in constants:
  inst = theory1(f, constant) # add theory axioms
  insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check() # check-sat
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 2: Under group axioms, every element has only one inverse**
"""

functions = [f, g]
constants = [c, e, d]
insts, constants = instantiate(functions, constants, depth = 1)

inst = theory2(f, g) # add theory axioms
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check() # check-sat
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 3: If in a group G,  𝑥 ,  𝑦  and  𝑧  are three elements such that  𝑥∘𝑦=𝑧∘𝑦 , then  𝑥=𝑧 .**
"""

functions = [f, g]
constants = [c, e, d]
insts, constants = instantiate(functions, constants, depth = 1)

inst = theory3(f) # add theory axioms
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check() # check-sat
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

# **Rings & Ring Theories**

**Rings**

A ring is a set $R$ with an operation called addition:
for any $a, b \in R,$ there is an element $a+b \in R$
and another operation called multiplication:
for any $a, b \in R,$ there is an element $a b \in R$
satisfying the following properties:

1. Addition is associative

   $(a+b)+c=a+(b+c) \text { for all } a, b, c \in R$

2. Additive identity exists (e = 0)
    
   $a+e=e+a=a \text { for all } a \in R$

3. Additive inverse exists (e' = -a)

   $a+e'=e'+a=e \text { for all } a \in R$$

4. Addition is commutative

   $a+b=b+a \text { for all } a, b \in R$

5. Multiplication is associative
    
   $(a b) c=a(b c) \text { for all } a, b, c \in R$

6. Multiplication is distributive over addition
 
   $a(b+c)=a b+a c$ and $(a+b) c=a c+b c$ for all $a, b, c \in R$

**Ring Axioms**

Final axioms that were converted to prenex normal form and Skolemized:
1. Associativity (addition): $\forall x, y, z . f(f(x, y), z)=f(x, f(y, z))$
2. Associativity (multiplication): $\forall x, y, z . g(g(x, y), z)=g(x, g(y, z))$
3. Identity (addition): $\forall x . f(x, e)=x \wedge f(e, x)=x$
4. Inverse (addition): $\forall x  \cdot f(x, h(x))=e \wedge f(h(x), x)=e$
5. Commutative (addition): $\forall x,y . f(x, y)=f(y,x)$
6. Distributive (multiplication over addition): 
$\forall x,y,z . g(x, f(y, z)) = f(g(x, y), g(x, z)) \wedge g(f(x, y), z) = f(g(x, z), g(y, z))$

**Ring Theories**

Final axioms that were converted to prenex normal form, negated, and Skolemized:
1. Under ring axioms, additive identity is unique 

  $\begin{aligned} \varphi & \equiv \forall e^{\prime} .\left(\left(\forall x .\left(f\left(x, e^{\prime}\right)=x \wedge f\left(e^{\prime}, x\right)=x\right) \Rightarrow\left(e=e^{\prime}\right)\right)\right) \end{aligned}$

  Negated and skolemized: 

  $\forall x \cdot(f(x, c)=x \wedge f(c, x)=x \wedge \neg(e=c))$

2. Under ring axioms, every element has only one additive inverse

  $\varphi: \forall x, y .(f(x, y)=e \wedge f(y, x)=e) \Rightarrow(y=h(x))$

  Negated and skolemized: 
 
  $(f(c, d)=e \wedge f(d, c)=e \wedge \neg(d=h(c)))$

---

In the next few blocks, I will:
1. Define functions and constants
2. Define the properties for ring axioms
3. Define a function to instantiate with depth 0 or 1
4. Prove the validity of the above theories
---

Functions and constants
"""

f = Function('f', IntSort(), IntSort(), IntSort()) # addition f(x, y) = x + y
g = Function('g', IntSort(), IntSort(), IntSort()) # multiplication g(x, y) = g * y
h = Function('h', IntSort(), IntSort()) #additive inverse h(x) = -x

c = Const('c', IntSort())
d = Const('d', IntSort())

e = Const('z', IntSort()) # additive identity 0

"""Ring axioms"""

def associative(func, x, y, z):
   # pass both f and g
   return func(func(x, y), z) == func(x, func(y, z))

def additive_inverse(f, h, x):
  # x+(-x) = (-x)+x = 0
  return And(f(x, h(x)) == e, f(h(x), x) == e) 

def additive_identity(f, x):
  # x+0 = 0+x = x
  return And(f(x, e) == x, f(e, x) == x) 

def distributive(f, g, x, y, z):
  return And(g(f(x, y), z) == f(g(x, z), g(y, z)), g(x, f(y,z)) == f(g(x,y), g(x,z)))

def commutative(f, x, y):
  return f(x, y) == f(y, x)

"""Ring theories"""

def theory1(f, x):
  # Under ring axioms, additive identity is unique
  return And(f(x, c) == x, f(c, x) == x, e != c)

def theory2(f, h):
  # Under ring axioms, every element has only one additive inverse
  return And(f(c, d) == e, f(d, c) == e, d != h(c))

"""Instantiate to depth 0 and/or 1"""

def instantiate(functions, constants, depth = 0):
  f, g, h = functions[0], functions[1], functions[2]

  if depth == 0: # ground terms only
    insts = []
    for c1 in constants:
      insts.append(additive_inverse(f, h, c1))
      insts.append(additive_identity(f, c1))
      for c2 in constants:
        insts.append(commutative(f, c1, c2))
        for c3 in constants:
          insts.append(associative(f, c1, c2, c3))
          insts.append(associative(g, c1, c2, c3))
          insts.append(distributive(f, g, c1, c2, c3))
    return insts, constants

  if depth == 1: # ground terms and functions
    insts = []
    new_constants = constants.copy()
    for c1 in constants:
      new_constants.append(h(c1))
      for c2 in constants:
        new_constants.append(f(c1,c2))
        new_constants.append(g(c1,c2))
    constants = new_constants

    for c1 in constants:
      insts.append(additive_inverse(f, h, c1))
      insts.append(additive_identity(f, c1))
      for c2 in constants:
        insts.append(commutative(f, c1, c2))
        for c3 in constants:
          insts.append(associative(f, c1, c2, c3))
          insts.append(associative(g, c1, c2, c3))
          insts.append(distributive(f, g, c1, c2, c3))
    return insts, constants

"""**Theory 1: Under ring axioms, additive identity is unique**


"""

functions = [f, g, h]
constants = [c, e]
insts, constants = instantiate(functions, constants, depth = 0)

for constant in constants:
  inst = theory1(f, constant)
  insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 2: Under ring axioms, every element has only one additive inverse**
"""

functions = [f, g, h]
constants = [c, e, d]
insts, constants = instantiate(functions, constants, depth = 1)

inst = theory2(f, h)
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

# **Variant: Commutative Rings**


**Commutative Rings**

The commutative ring has the same properties as the ring defined in the previous section, with the additional property:

7. Multiplication is commutative

   $(ab)c=a(bc) \text { for all } a, b, c \in R$


**Commutative Ring Axioms**

Final axioms that were converted to prenex normal form and Skolemized:
1. Associativity (addition): $\forall x, y, z . f(f(x, y), z)=f(x, f(y, z))$
2. Associativity (multiplication): $\forall x, y, z . g(g(x, y), z)=g(x, g(y, z))$
3. Identity (addition): $\forall x . f(x, e)=x \wedge f(e, x)=x$
4. Inverse (addition): $\forall x  \cdot f(x, h(x))=e \wedge f(h(x), x)=e$
5. Commutative (addition): $\forall x,y . f(x, y)=f(y,x)$
6. Distributive (multiplication over addition): 
$\forall x,y,z . g(x, f(y, z)) = f(g(x, y), g(x, z)) \wedge g(f(x, y), z) = f(g(x, z), g(y, z))$
7. Commutative (multiplication): $\forall x,y . g(x, y)=g(y,x)$

**Commutative Ring Theories**

Final axioms that were converted to prenex normal form, negated, and Skolemized:
1. Under commutative ring axioms, additive identity is unique 

  $\begin{aligned} \varphi & \equiv \forall e^{\prime} .\left(\left(\forall x .\left(f\left(x, e^{\prime}\right)=x \wedge f\left(e^{\prime}, x\right)=x\right) \Rightarrow\left(e=e^{\prime}\right)\right)\right) \end{aligned}$

  Negated and skolemized: 

  $\forall x \cdot(f(x, c)=x \wedge f(c, x)=x \wedge \neg(e=c))$

2. Under commutative ring axioms, every element has only one additive inverse

  $\varphi: \forall x, y .(f(x, y)=e \wedge f(y, x)=e) \Rightarrow(y=g(x))$

  Negated and skolemized: 
 
  $(f(c, d)=e \wedge f(d, c)=e \wedge \neg(d=g(c)))$

3. A ring R is commutative if and only if $(x+y)^2 = x^2 + 2xy + y^2$ holds for all $x, y \in R$. (Using one direction of the statement: if it holds, it is commutative)

   $\varphi: \forall x, y .((x+y)^2 = x^2 + 2xy + y^2) \Rightarrow(g(x, y)=g(y,x))$

  Negated and skolemized: 
 
  $g(f(c,d), f(c,d)) = f(f(g(c,c), g(d,d)), g(2, g(c,d))) \wedge \neg(g(c,d) = g(d,c))$

4. If $x^2 = x$ holds for all $x \in R$, the ring $R$ is commutative. (This is also called a Boolean Ring)

   $\varphi: \forall x, y .(g(x,x) = x)  \Rightarrow(g(x, y)=g(y,x))$

  Negated and skolemized: 
 
  $g(c, c) = c \wedge \neg(g(c,d) = g(d,c))$

5. If $(xy)^2 = x^2y^2$ holds for all $x \in R$, the ring $R$ is commutative. 

   $\varphi: \forall x, y .(g(g(x,y),g(x,y)) = g(g(x,x),g(y,y)))  \Rightarrow(g(x, y)=g(y,x))$

  Negated and skolemized: 
 
  $g(g(c,d),g(c,d)) = g(g(c,c),g(d,d)) \wedge \neg(g(c,d) = g(d,c))$


---

In the next few blocks, I will:
1. Define functions and constants
2. Define the properties for commutative ring axioms
3. Define a function to instantiate with depth 0 or 1
4. Prove the validity of the above theories
---

Functions and constants
"""

f = Function('f', IntSort(), IntSort(), IntSort()) # addition f(x, y) = x + y
g = Function('g', IntSort(), IntSort(), IntSort()) # multiplication g(x, y) = x* y
h = Function('h', IntSort(), IntSort()) #additive inverse h(x) = -x

c = Const('c', IntSort())
d = Const('d', IntSort())

e = Const('z', IntSort()) # additive identity zero

"""Commutative ring properties"""

def associative(func, x, y, z):
  # for both f and g
  return func(func(x, y), z) == func(x, func(y, z))

def additive_inverse(f, h, x):
  # x+(-x) = (-x)+x = 0
  return And(f(x, h(x)) == e, f(h(x), x) == e) 

def additive_identity(f, x):
  # x+0 = 0+x = x
  return And(f(x, e) == x, f(e, x) == x) 

def distributive(f, g, x, y, z):
  return And(g(f(x, y), z) == f(g(x, z), g(y, z)), g(x, f(y,z)) == f(g(x,y), g(x,z)))

def commutative(func, x, y):
  # for both f and g
  return func(x, y) == func(y, x)

"""Commutative ring theories"""

def theory1(f, x):
  # Under commutative ring axioms, additive identity is unique
  return And(f(x, c) == x, f(c, x) == x, e != c)

def theory2(f, h):
  # Under commutative ring axioms, every element has only one additive inverse
  return And(f(c, d) == e, f(d, c) == e, d != h(c))

def theory3(f, g):
  # A ring R is commutative if and only if (x+y)^2 = x^2 + 2xy + y^2 holds for all x, y  R. (Using one direction of the statement: if it holds, it is commutative)
  return And(g(f(c,d), f(c,d)) == f(f(g(c,c), g(d,d)), g(2, g(c,d))), g(c,d) != g(d,c)) 

def theory4(g):
  # If x^2 = x holds for all x in R, the ring R is commutative. (This is also called a Boolean Ring)
  return And(g(c,c) == c, g(c,d) != g(d,c))

def theory5(g):
  # If (xy)^2 = x^2y^2 holds for all x in R, the ring R is commutative.
  return And(g(g(c,d),g(c,d)) == g(g(c,c),g(d,d)), g(c,d) != g(d,c))

"""Instatiate to depth 0 and/or 1"""

def instantiate(functions, constants, depth = 0):
  f, g, h = functions[0], functions[1], functions[2]

  if depth == 0: # ground terms only
    insts = []
    for c1 in constants:
      insts.append(additive_inverse(f, h, c1))
      insts.append(additive_identity(f, c1))
      for c2 in constants:
        insts.append(commutative(f, c1, c2))
        insts.append(commutative(g, c1, c2))
        for c3 in constants:
          insts.append(associative(f, c1, c2, c3))
          insts.append(associative(g, c1, c2, c3))
          insts.append(distributive(f, g, c1, c2, c3))
    return insts, constants

  if depth == 1:  # ground terms and functions
    insts = []
    new_constants = constants.copy()
    for c1 in constants:
      new_constants.append(h(c1))
      for c2 in constants:
        new_constants.append(f(c1,c2))
        new_constants.append(g(c1,c2))
    constants = new_constants

    for c1 in constants:
      insts.append(additive_inverse(f, h, c1))
      insts.append(additive_identity(f, c1))
      for c2 in constants:
        insts.append(commutative(f, c1, c2))
        insts.append(commutative(g, c1, c2))
        for c3 in constants:
          insts.append(associative(f, c1, c2, c3))
          insts.append(associative(g, c1, c2, c3))
          insts.append(distributive(f, g, c1, c2, c3))
    return insts, constants

"""**Theory 1: Under commutative ring axioms, additive identity is unique**

"""

functions = [f, g, h]
constants = [c, e]
insts, constants = instantiate(functions, constants, depth = 0)

for constant in constants:
  inst = theory1(f, constant)
  insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 2: Under commutative ring axioms, every element has only one additive inverse**
"""

functions = [f, g, h]
constants = [c, e, d]
insts, constants = instantiate(functions, constants, depth = 1)

inst = theory2(f, h)
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 3: A ring R is commutative if and only if $(x+y)^2 = x^2 + 2xy + y^2$ holds for all $x, y \in R$. (Using one direction of the statement: if it holds, it is commutative)**
"""

functions = [f, g, h]
constants = [c, e, d]
insts, constants = instantiate(functions, constants, depth = 0)

inst = theory3(f, g)
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 4: If $x^2 = x$ holds for all $x \in R$, the ring $R$ is commutative. (This is also called a Boolean Ring)**
"""

functions = [f, g, h]
constants = [c, e, d]
insts, constants = instantiate(functions, constants, depth = 0)

inst = theory4(g)
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 5: If $(xy)^2 = x^2y^2$ holds for all $x \in R$, the ring $R$ is commutative.**
"""

functions = [f, g, h]
constants = [c, e, d]
insts, constants = instantiate(functions, constants, depth = 0)

inst = theory5(g)
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

# **Fields & Field Theories**

**Fields**

A field is a triple $(F,+,\cdot)$ where $F$ is a set, and $+$ and $\cdot$ are binary operations on $F$ (called addition and multiplication respectively) satisfying the following properties:

1. Addition is associative

   $(a+b)+c=a+(b+c) \text { for all } a, b, c \in R$

2. Additive identity exists (= 0)
    
   $a+ea=ea+a=a \text { for all } a \in R$
 
3. Additive inverse exists (=-a)

   $a+ea'=ea'+a=ea \text { for all } a \in R$$

4. Addition is commutative

   $a+b=b+a \text { for all } a, b \in R$

5. Multiplication is associative
    
   $(a b) c=a(b c) \text { for all } a, b, c \in R$

6. Multiplication is distributive over addition
 
   $a(b+c)=a b+a c$ and $(a+b) c=a c+b c$ for all $a, b, c \in R$

7. Multiplicative identity exists (= 1)
    
   $a \cdot em=em \cdot a=a \text { for all } a \in R$

8. Multiplicative inverse exists (= 1/a, a != 0)

   $a \cdot em'=em' \cdot a=em \text { for all } a \in R$

9. Zero-One law (additive identity and multiplicative identity are distinct)

   $0 \neq 1$

**Field Axioms**

Final axioms that were converted to prenex normal form and Skolemized:
1. Associativity (addition): $\forall x, y, z . f(f(x, y), z)=f(x, f(y, z))$
2. Associativity (multiplication): $\forall x, y, z . g(g(x, y), z)=g(x, g(y, z))$
3. Identity (addition): $\forall x . f(x, ea)=x \wedge f(ea, x)=x$
4. Inverse (addition): $\forall x  \cdot f(x, h(x))=e \wedge f(h(x), x)=e$
5. Commutative (addition): $\forall x,y . f(x, y)=f(y,x)$
6. Distributive (multiplication over addition): 
$\forall x,y,z . g(x, f(y, z)) = f(g(x, y), g(x, z)) \wedge g(f(x, y), z) = f(g(x, z), g(y, z))$
7. Identity (multiplication): $\forall x . g(x, em)=x \wedge g(em, x)=x$
8. Inverse (multiplication): $\forall x  \cdot g(x, j(x))=em \wedge g(j(x), x)=em$
9. Zero-One law: $\neg(ea = em)$

**Field Theories**

Final axioms that were converted to prenex normal form, negated, and Skolemized:
1. Under field axioms, additive identity is unique 

  $\begin{aligned} \varphi & \equiv \forall e^{\prime} .\left(\left(\forall x .\left(f\left(x, e^{\prime}\right)=x \wedge f\left(e^{\prime}, x\right)=x\right) \Rightarrow\left(ea=e^{\prime}\right)\right)\right) \end{aligned}$

  Negated and skolemized: 

  $\forall x \cdot(f(x, c)=x \wedge f(c, x)=x \wedge \neg(ea=c))$

2. Under field axioms, every element has only one additive inverse

  $\varphi: \forall x, y .(f(x, y)=ea \wedge f(y, x)=ea) \Rightarrow(y=h(x))$

  Negated and skolemized: 
 
  $(f(c, d)=ea \wedge f(d, c)=ea \wedge \neg(d=h(c)))$

3. [F is commutative too] A ring R is commutative if and only if $(x+y)^2 = x^2 + 2xy + y^2$ holds for all $x, y \in R$. (Using one direction of the statement: if it holds, it is commutative)

   $\varphi: \forall x, y .((x+y)^2 = x^2 + 2xy + y^2) \Rightarrow(g(x, y)=g(y,x))$

  Negated and skolemized: 
 
  $g(f(c,d), f(c,d)) = f(f(g(c,c), g(d,d)), g(2, g(c,d))) \wedge \neg(g(c,d) = g(d,c))$

4. [F is commutative too] If $x^2 = x$ holds for all $x \in R$, the ring $R$ is commutative. (This is also called a Boolean Ring)

   $\varphi: \forall x, y .(g(x,x) = x)  \Rightarrow(g(x, y)=g(y,x))$

  Negated and skolemized: 
 
  $g(c, c) = c \wedge \neg(g(c,d) = g(d,c))$

5. [F is commutative too] If $(xy)^2 = x^2y^2$ holds for all $x \in R$, the ring $R$ is commutative. 

   $\varphi: \forall x, y .(g(g(x,y),g(x,y)) = g(g(x,x),g(y,y)))  \Rightarrow(g(x, y)=g(y,x))$

  Negated and skolemized: 
 
  $g(g(c,d),g(c,d)) = g(g(c,c),g(d,d)) \wedge \neg(g(c,d) = g(d,c))$

6. Under field axioms, multiplicative identity is unique 

  $\begin{aligned} \varphi & \equiv \forall e^{\prime} .\left(\left(\forall x .\left(g\left(x, e^{\prime}\right)=x \wedge g\left(e^{\prime}, x\right)=x\right) \Rightarrow\left(e=e^{\prime}\right)\right)\right) \end{aligned}$

  Negated and skolemized: 

  $\forall x \cdot(g(x, c)=x \wedge g(c, x)=x \wedge \neg(em=c))$

7. Under field axioms, every element has only one multiplicative inverse

  $\varphi: \forall x, y .(g(x, y)=em \wedge g(y, x)=em) \Rightarrow(y=j(x))$

  Negated and skolemized: 
 
  $(g(c, d)=e \wedge g(d, c)=e \wedge \neg(d=j(c)))$

---

In the next few blocks, I will:
1. Define functions and constants
2. Define the properties for ring axioms
3. Define a function to instantiate with depth 0 or 1
4. Prove the validity of the above theories
---

Functions and constants
"""

f = Function('f', RealSort(), RealSort(), RealSort()) # addition
g = Function('g', RealSort(), RealSort(), RealSort()) # multiplication
h = Function('h', RealSort(), RealSort()) #additive inverse h(x) = -x
j = Function('j', RealSort(), RealSort()) #multiplicative inverse j(x) = 1/x

c = Const('c', RealSort())
d = Const('d', RealSort())

ea = Const('ea', RealSort()) # additive identity 0
em = Const('em', RealSort()) # multiplicative identity 1

"""Field properties"""

def associative(func, x, y, z):
  # for both f and g
  return func(func(x, y), z) == func(x, func(y, z))

def additive_inverse(f, h, x):
  #x+(-x) = (-x)+x = 0
  return And(f(x, h(x)) == ea, f(h(x), x) == ea) 

def additive_identity(f, x):
  # x+0 = 0+x = x
  return And(f(x, ea) == x, f(ea, x) == x) 

def multiplicative_identity(g, x):
  # x.1 = 1.x = x
  return And(g(x, em) == x, g(em, x) == x)

def multiplicative_inverse(g, j, x):
  #x.(1/x) = (1/x).x = 1 and x!=0
  return And(g(x, j(x)) == em, g(j(x), x) == em, x!= 0) 

def distributive(f, g, x, y, z):
  return And(g(f(x, y), z) == f(g(x, z), g(y, z)), g(x, f(y,z)) == f(g(x,y), g(x,z)))

def commutative(func, x, y):
  # for both f and g
  return func(x, y) == func(y, x)

def zero_one(ea, em):
  return ea != em

"""Field Theories"""

def theory1(f, x):
  # Under field axioms, additive identity is unique
  return And(f(x, c) == x, f(c, x) == x, ea != c)

def theory2(f, h):
  # Under field axioms, every element has only one additive inverse
  return And(f(c, d) == ea, f(d, c) == ea, d != h(c))

def theory3(f, g):
  # [applies for fields] A ring R is commutative if and only if (x+y)^2 = x^2 + 2xy + y^2 holds for all x, y  R. (Using one direction of the statement: if it holds, it is commutative)
  return And(g(f(c,d), f(c,d)) == f(f(g(c,c), g(d,d)), g(2, g(c,d))), g(c,d) != g(d,c)) 

def theory4(g):
  # [applies for fields] If x^2 = x holds for all x in R, the ring R is commutative. (This is also called a Boolean Ring)
  return And(g(c,c) == c, g(c,d) != g(d,c))

def theory5(g):
  # [applies for fields] If (xy)^2 = x^2y^2 holds for all x in R, the ring R is commutative.
  return And(g(g(c,d),g(c,d)) == g(g(c,c),g(d,d)), g(c,d) != g(d,c))

def theory6(g, x): 
  # Under field axioms, multiplicative identity is unique
  return And(g(x, c) == x, g(c, x) == x, em != c)

def theory7(g, j):
  # Under field axioms, every element has only one multiplicative inverse
  return And(g(c, d) == em, g(d, c) == em, d != j(c))

"""Instantiate to depth 0 and/or 1"""

def instantiate(functions, constants, depth = 0):
  f, g, h, j = functions[0], functions[1], functions[2], functions[3]

  if depth == 0:
    insts = []
    inst = zero_one(ea, em)
    insts.append(inst)
    for c1 in constants:
      insts.append(additive_inverse(f, h, c1))
      insts.append(additive_identity(f, c1))
      insts.append(multiplicative_inverse(g, j, c1))
      insts.append(multiplicative_identity(g, c1))
      for c2 in constants:
        insts.append(commutative(f, c1, c2))
        insts.append(commutative(g, c1, c2))
        for c3 in constants:
          insts.append(associative(f, c1, c2, c3))
          insts.append(associative(g, c1, c2, c3))
          insts.append(distributive(f, g, c1, c2, c3))
    return insts, constants

  if depth == 1:
    insts = []
    new_constants = constants.copy()
    for c1 in constants:
      new_constants.append(h(c1))
      new_constants.append(j(c1))
      for c2 in constants:
        new_constants.append(f(c1,c2))
        new_constants.append(g(c1,c2))
    constants = new_constants

    inst = zero_one(ea, em)
    insts.append(inst)
    for c1 in constants:
      insts.append(additive_inverse(f, h, c1))
      insts.append(additive_identity(f, c1))
      insts.append(multiplicative_inverse(g, j, c1))
      insts.append(multiplicative_identity(g, c1))
      for c2 in constants:
        insts.append(commutative(f, c1, c2))
        insts.append(commutative(g, c1, c2))
        for c3 in constants:
          insts.append(associative(f, c1, c2, c3))
          insts.append(associative(g, c1, c2, c3))
          insts.append(distributive(f, g, c1, c2, c3))
    return insts, constants

"""**Theory 1: Under field axioms, additive identity is unique**

"""

functions = [f, g, h, j]
constants = [c, em, d, ea]
insts, constants = instantiate(functions, constants, depth = 1)

for constant in constants:
  inst = theory1(f, constant)
  insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 2: Under field axioms, every element has only one additive inverse**
"""

functions = [f, g, h, j]
constants = [c, em, d, ea]
insts, constants = instantiate(functions, constants, depth = 1)

inst = theory2(f, h)
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 3: [applies to fields too] A ring R is commutative if and only if $(x+y)^2 = x^2 + 2xy + y^2$ holds for all $x, y \in R$. (Using one direction of the statement: if it holds, it is commutative)**
"""

functions = [f, g, h, j]
constants = [c, em, d, ea]
insts, constants = instantiate(functions, constants, depth = 0)

inst = theory3(f, g)
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 4: [applies to fields too] If $x^2 = x$ holds for all $x \in R$, the ring $R$ is commutative. (This is also called a Boolean Ring)**
"""

functions = [f, g, h, j]
constants = [c, em, d, ea]
insts, constants = instantiate(functions, constants, depth = 0)

inst = theory4(g)
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 5: [applies to fields too] If $(xy)^2 = x^2y^2$ holds for all $x \in R$, the ring $R$ is commutative.**
"""

functions = [f, g, h, j]
constants = [c, em, d, ea]
insts, constants = instantiate(functions, constants, depth = 0)

inst = theory5(g)
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 6: Under field axioms, multiplictive identity is unique**
"""

functions = [f, g, h, j]
constants = [c, em, d, ea]
insts, constants = instantiate(functions, constants, depth = 0)

for constant in constants:
  inst = theory6(g, constant)
  insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)

**Theory 7: Under field axioms, every element has only one multiplicative inverse**
"""

functions = [f, g, h, j]
constants = [c, em, d, ea]
insts, constants = instantiate(functions, constants, depth = 1)

inst = theory7(g, j)
insts.append(inst)

s = Solver()
for inst in insts:
  s.add(inst)
s.check()
# s.model()

"""The set of axioms that contain the negation of the theory is unsatisfiable.

Hence the original theory is valid :)


---

# References

1.   Logic in CS - Course Notes (https://courses.engr.illinois.edu/cs498mp3/fa2020/Logic_in_CS.pdf)
2.   http://talus.maths.usyd.edu.au/u/UG/SM/MATH3062/r/ah-ringaxioms.pdf
3.   http://www.maths.nuigalway.ie/~rquinlan/groups/section1-2.pdf
4.   http://ksuweb.kennesaw.edu/~sellerme//sfehtml/classes/math4362/notesonrings.pdf
5.   http://people.reed.edu/~mayer/math112.html/html1/node16.html
6.   https://en.wikibooks.org/wiki/Ring_Theory/Properties_of_rings
7.   https://en.wikipedia.org/wiki/Commutative_ring
8.   Z3Py Guide: https://ericpony.github.io/z3py-tutorial/guide-examples.htm
9.   Z3Py Advanced Guide: https://ericpony.github.io/z3py-tutorial/advanced-examples.htm
"""
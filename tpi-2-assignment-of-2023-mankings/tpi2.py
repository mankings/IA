#encoding: utf8

# YOUR NAME: Mancósmico
# YOUR NUMBER: 069420

# COLLEAGUES WITH WHOM YOU DISCUSSED THIS ASSIGNMENT:
# - Filipe Antão 103470 - discussed about the new cardinality dynamic on associations and it's impact in type infering
# - Paulo Pinto 103234 - discussed about the new cardinality dynamic on associations and it's impact in type infering

from semantic_network import *
from bayes_net import *
from constraintsearch import *

import itertools
import inspect

class MySN(SemanticNetwork):
    recur_count = 0

    def __init__(self):
        SemanticNetwork.__init__(self)
        # ADD CODE HERE IF NEEDED
        pass

    def is_object(self,user,obj):
        userdecl = [decl for decl in self.declarations if decl.user == user]
        objects = {d.relation.entity1 for d in userdecl if type(d.relation) is Member or type(d.relation) is Association and d.relation.card == None}
        objects = objects.union({d.relation.entity2 for d in userdecl if type(d.relation) is Association and d.relation.card == None})
        if obj in objects:
            return True
        return False

    def is_type(self,user,type_):
        userdecl = [decl for decl in self.declarations if decl.user == user]
        types = {d.relation.entity1 for d in userdecl if type(d.relation) is Subtype or type(d.relation) is Association and d.relation.card != None}
        types = types.union({d.relation.entity2 for d in userdecl if type(d.relation) in [Member, Subtype] or type(d.relation) is Association and d.relation.card != None})
        if type_ in types:
            return True
        return False


    def infer_type(self,user,obj):
        if not self.is_object(user, obj):
            return None

        userdecl = [decl for decl in self.declarations if decl.user == user]

        memberdecls = [d for d in userdecl if type(d.relation) is Member and d.relation.entity1 == obj]
        if memberdecls != []:
            return memberdecls[0].relation.entity2
        
        objassocdecls = [d for d in userdecl if type(d.relation) is Association and d.relation.card == None and obj in [d.relation.entity1, d.relation.entity2]]

        if objassocdecls != []:
            assocs = {d.relation.name for d in objassocdecls}
            typeassocdecls = {assoc: [d for d in userdecl if type(d.relation) is Association and d.relation.card != None and d.relation.name == assoc] for assoc in assocs}
            typeassocdecls = {key: typeassocdecls[key] for key in typeassocdecls.keys() if typeassocdecls[key] != []}
            if typeassocdecls == {}:
                return '__unknown__'

            signatures = [self.infer_signature(user, a) for a in typeassocdecls.keys()]
            signatures = [e for e in signatures if e != None]

        if obj in [d.relation.entity1 for d in objassocdecls]:
            return signatures[0][0]
        return signatures[0][1]

 
    def infer_signature(self,user,assoc):
        userdecl = [decl for decl in self.declarations if decl.user == user]

        assocdecls = [d for d in userdecl if type(d.relation) is Association and d.relation.name == assoc]
        if assocdecls == []:
            return None

        typeassocdecls = [d for d in assocdecls if d.relation.card != None]
        if typeassocdecls != []:
            return typeassocdecls[0].relation.entity1, typeassocdecls[0].relation.entity2
        
        objassocdecls = [d for d in assocdecls if d.relation.card == None]
        if objassocdecls != []:
            types = [(self.infer_type(user, d.relation.entity1), self.infer_type(user, d.relation.entity2)) for d in objassocdecls]
            return (types[0][0], types[0][1])

class MyBN(BayesNet):

    def __init__(self):
        BayesNet.__init__(self)
        # ADD CODE HERE IF NEEDED
        pass

    def markov_blanket(self,var):
        parents = [v for v in self.dependencies[var][0][0]] + [v for v in self.dependencies[var][0][1]]
        children = [v for v in self.dependencies if var in self.dependencies[v][0][0] or var in self.dependencies[v][0][0]]
        spouses = [v for sublist in [[v for v in self.dependencies[child][0][0] if v != var] + [v for v in self.dependencies[child][0][1] if v != var] for child in children] for v in sublist]

        blanket = parents + children + spouses
        return blanket


class MyCS(ConstraintSearch):

    def __init__(self,domains,constraints):
        ConstraintSearch.__init__(self,domains,constraints)
        # ADD CODE HERE IF NEEDED
        pass

    def propagate(self, domains, var):
        pairs = [(a, b) for a, b in self.constraints if b == var]
        while pairs != []:
            a, b = pairs.pop()
            domainsize = len(domains[a])

            domains[a] = [aval for aval in domains[a] if any(self.constraints[a, b](a, aval, b, bval) for bval in domains[b])]

            if len(domains[a]) < domainsize:
                pairs += [(v1, v2) for v1, v2 in self.constraints if v2 == a]

    def higherorder2binary(self,ho_c_vars,unary_c):
        newvar = ''.join(ho_c_vars)
        cartprod = list(itertools.product(*[self.domains[d] for d in ho_c_vars]))
        self.domains[newvar] = [t for t in cartprod if unary_c(t)]

        binaryconstraints = {}
        for i, v in enumerate(ho_c_vars):
            binaryconstraints[newvar, v] = lambda v1, x1, v2, x2: x1[i] == x2

        for i, a in enumerate(ho_c_vars):
            for b in ho_c_vars[i+1:]:
                binaryconstraints[a, b] = lambda v1, x1, v2, x2: x1 != x2
        for c in binaryconstraints:
            self.constraints[c] = binaryconstraints[c]


        # for k in self.constraints.keys(): print(k, inspect.getsource(self.constraints[k]).strip())
        
        # stor eu não sei de onde falta a constraint perdida
        # stor eu não sei porque é que a linha 132 não funciona para passar o teste da linha 247 dos testes

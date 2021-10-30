#!/usr/bin/python3
import sys


def negate(x):
    return x * -1


class Sequent:
    def __init__(self, antecedents, succedents):
        self.antecedents = antecedents  # [[1, 2], [1, -2]]
        self.succedents = succedents  # [[1, 2], [3]]

    def __str__(self) -> str:
        return f'{self.antecedents} --> {self.succedents}'

    def is_axiom(self):
        return len(self.antecedents & self.succedents) > 0

    def can_apply_left_rule(self):
        return self.can_apply_or_left() or self.can_apply_not_left()

    def can_apply_or_left(self):
        return any([len(a) > 1 for a in self.antecedents])

    def can_apply_not_left(self):
        return any([len(a) == 1 and list(a)[0] < 0 for a in self.antecedents])

    def apply_a_rule(self):
        if (self.can_apply_or_left()):
            return self.apply_or_left()
        if (self.can_apply_not_left()):
            return self.apply_not_left()
        raise Exception('should not happen')

    def apply_or_left(self):
        # split up one of the antecedents that consists of more than one literal
        # also has to account for more than two literals in clause!!!
        aa_list = list(self.antecedents)
        for antecedent in aa_list:
            if len(antecedent) > 1:  # form is A v B
                # convert set to list to use indexes
                print(f'splitting up {antecedent}')
                antecedent_as_list = list(antecedent)

                a = frozenset([antecedent_as_list[0]])  # first element
                b = frozenset(antecedent_as_list[1:])  # rest

                antecedents_with_a = set([
                    c for c in aa_list if c != antecedent] + [a])
                antecedents_with_b = set([
                    c for c in aa_list if c != antecedent] + [b])
                print(f'--> antecedents with a: {antecedents_with_a}')
                print(f'--> antecedents with b: {antecedents_with_b}')

                # return new sequents used as premises
                s_with_a = Sequent(antecedents_with_a, self.succedents)
                s_with_b = Sequent(antecedents_with_b, self.succedents)
                return [s_with_a, s_with_b]

        raise Exception('this should not happen')

    def apply_not_left(self):
        aa_list = self.antecedents
        for antecedent in aa_list:
            is_literal = len(antecedent) == 1
            is_negated_literal = is_literal and list(antecedent)[0] < 0
            if is_negated_literal:
                # we can apply the rule to this clause
                literal = list(antecedent)[0]
                pos_literal = negate(literal)

                new_antecedents = set(
                    [c for c in self.antecedents if c != antecedent])
                new_succedents = set(
                    list(self.succedents) + [frozenset([pos_literal])])

                new_sequent = Sequent(new_antecedents, new_succedents)

                return [new_sequent]


def read_input():
    clauses = set()
    clause_strs = sys.stdin.read().split('\n')
    for s in clause_strs:
        literals = frozenset([int(x) for x in s.split()])
        if (len(literals) > 0):
            clauses.add(literals)
    return clauses


def main():
    clauses = read_input()
    # we are trying to show the satisfiability of Φ
    # this means, we show the falsibiability of ¬Φ
    # effectively, this means, try to show the validity of Φ ⇒

    # take clauses as antecedents
    s = Sequent(clauses, set())
    print(clauses)
    result = prove(s)
    print(result)


def prove(s: Sequent):
    print(f'proving {s}')
    if (s.is_axiom()):
        return 'closed branch'

    if (not s.can_apply_left_rule()):
        return 'open branch'

    prems = s.apply_a_rule()
    for p in prems:
        answer = prove(p)
        if (answer == 'open branch'):
            return answer

    return 'closed branch'


main()

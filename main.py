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

    def can_apply_or_left(self):
        return any([len(a) > 0 for a in self.antecedents])

    def apply_or_left(self):
        # split up one of the antecedents that consists of more than one literal
        aa_list = list(self.antecedents)
        for a in aa_list:
            if len(a) > 1:
                print(f'splitting up {a}')


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
    prove(s)


def prove(s: Sequent):
    print(f'proving {s}')
    if (s.is_axiom()):
        return None

    if (not s.can_apply_or_left()):
        return []

    s.apply_or_left()


main()

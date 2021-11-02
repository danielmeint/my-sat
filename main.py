#!/usr/bin/python3
import sys
import time


def negate(x):
    return x * -1


class Clause(frozenset):
    def __str__(self) -> str:
        return super().__str__()


class Sequent:
    def __init__(self, antecedents, succedents):
        self.antecedents = antecedents
        self.succedents = succedents

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
                # print(f'splitting up {antecedent}')
                antecedent_as_list = list(antecedent)

                a = Clause([antecedent_as_list[0]])  # first element
                b = Clause(antecedent_as_list[1:])   # rest

                antecedents_with_a = set([
                    c for c in aa_list if c != antecedent] + [a])
                antecedents_with_b = set([
                    c for c in aa_list if c != antecedent] + [b])
                # print(f'--> antecedents with a: {antecedents_with_a}')
                # print(f'--> antecedents with b: {antecedents_with_b}')

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
                    list(self.succedents) + [Clause([pos_literal])])

                new_sequent = Sequent(new_antecedents, new_succedents)

                return [new_sequent]

    def extract_falsifying_assignment(self):
        assignment = set()
        if self.can_apply_left_rule():
            raise Exception('this should not happen')
        for antecedent in self.antecedents:
            assert len(antecedent) == 1
            literal = list(antecedent)[0]
            assignment.add(literal)
        for succedent in self.succedents:
            assert len(succedent) == 1
            literal = list(succedent)[0]
            assignment.add(negate(literal))
        return assignment


def parse_clauses(lines):
    clauses = set()
    for l in lines:
        literals = Clause([int(x) for x in l.split()])
        if 0 in literals:
            raise Exception(
                'cannot use 0 as propositional variable; Please try again!')
        if (len(literals) > 0):
            clauses.add(literals)
    return clauses


def read_file(fname):
    print(f'reading clauses from {fname}')
    f = open(fname, 'r')
    lines = f.readlines()
    clauses = parse_clauses(lines)
    f.close()
    return clauses


def read_std_in():
    print('Provide one clause per line (integers, space-separated), press ENTER for the next clause or CTRL+D to start the validation.\nPlease use integers (positive and negative, not zero) as literals.\nThe negation of 1 is represeted by -1. Example clause: 1 -2')
    clauses = set()
    clause_strs = sys.stdin.read().split('\n')
    clauses = parse_clauses(clause_strs)
    return clauses


def test_kth_bit(n, k):
    # print(bin(n))
    try:
        return bin(n)[-(k+1)] == '1'
    except:
        return False


def generate_clauses(n):
    clauses = set()
    for i in range(2**n):
        clause = Clause([k+1 if test_kth_bit(i, k)
                        else (k+1) * -1 for k in range(n)])
        clauses.add(clause)

    return clauses


'''
method to test performance
'''


def test():
    n = 1
    while(True):
        start = time.time()
        clauses = generate_clauses(n)
        print(clauses)
        s = Sequent(clauses, set())
        result = prove(s)

        end = time.time()
        print_result(clauses, result)
        print(f'Took {end - start} seconds to solve')

        n += 1


def main():
    clauses = read_file(sys.argv[1]) if len(sys.argv) == 2 else read_std_in()
    print(clauses)

    # we are trying to show the satisfiability of Φ
    # this means, we show the falsibiability of ¬Φ
    # effectively, this means, try to show the validity of Φ ⇒

    # take clauses as antecedents
    s = Sequent(clauses, set())

    result = prove(s)
    print_result(clauses, result)


def print_result(clauses, result):
    if result == 'closed branch':
        # ¬Φ is valid; therefore, Φ is unsatisfiable
        print('unsatisfiable')
    else:
        # ¬Φ is falsifiable; therefore, Φ is satisfiable
        print('satisfiable')
        print(f'minimum requirements for satisfying interpretation: {result}')

        # there might be additional variables that are not contained in the min requirements, i.e., it doesn't matter if they are negated or not
        # --> we simply include them all non-negated
        remaining_variables = set(
            [abs(v) for c in clauses for v in c if not (v in result or negate(v) in result)])

        # valid interpretation is the union of min requirements and remaining literals (non-negated)
        satisfying_interpretation = result | remaining_variables
        print(
            f'example satisfying interpretation: {satisfying_interpretation}')


def prove(s: Sequent):
    # print(f'proving {s}')
    if (s.is_axiom()):
        return 'closed branch'

    if (not s.can_apply_left_rule()):
        # open branch
        return s.extract_falsifying_assignment()

    prems = s.apply_a_rule()
    for p in prems:
        answer = prove(p)
        if (answer != 'closed branch'):
            return answer

    return 'closed branch'


main()
# test()

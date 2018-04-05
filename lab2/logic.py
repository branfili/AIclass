import util
import functools

class Labels:
    """
    Labels describing the WumpusWorld
    """
    WUMPUS = 'w'
    TELEPORTER = 't'
    POISON = 'p'
    SAFE = 'o'

    """
    Some sets for simpler checks
    >>> if literal.label in Labels.DEADLY:
    >>>     # Don't go there!!!
    """
    DEADLY = set([WUMPUS, POISON])
    WTP = set([WUMPUS, POISON, TELEPORTER])

    UNIQUE = set([WUMPUS, POISON, TELEPORTER, SAFE])

    POISON_FUMES = 'b'
    TELEPORTER_GLOW = 'g'
    WUMPUS_STENCH = 's'

    INDICATORS = set([POISON_FUMES, TELEPORTER_GLOW, WUMPUS_STENCH])


def stateWeight(state):
    """
    To ensure consistency in exploring states, they will be sorted
    according to a simple linear combination.
    The maps will never be
    larger than 20x20, and therefore this weighting will be consistent.
    """
    x, y = state
    return 20*x + y


@functools.total_ordering
class Literal:
    """
    A literal is an atom or its negation
    In this case, a literal represents if a certain state (x,y) is or is not
    the location of GhostWumpus, or the poisoned pills.
    """

    def __init__(self, label, state, negative=False):
        """
        Set all values. Notice that the state is remembered twice - you
        can use whichever representation suits you better.
        """
        x,y = state

        self.x = x
        self.y = y
        self.state = state

        self.negative = negative
        self.label = label

    def __key(self):
        """
        Return a unique key representing the literal at a given point
        """
        return (self.x, self.y, self.negative, self.label)

    def __hash__(self):
        """
        Return the hash value - this operator overloads the hash(object) function.
        """
        return hash(self.__key())

    def __eq__(first, second):
        """
        Check for equality - this operator overloads '=='
        """
        return first.__key() == second.__key()

    def __lt__(self, other):
        """
        Less than check
        by using @functools decorator, this is enough to infer ordering
        """
        return stateWeight(self.state) < stateWeight(other.state)

    def __str__(self):
        """
        Overloading the str() operator - convert the object to a string
        """
        s = self.label + '(' + str(self.x) + ', ' + str(self.y) + ')'
        if self.negative: s = '~' + s
        return s

    def __repr__(self):
        """
        Object representation, in this case a string
        """
        return self.__str__()

    def copy(self):
        """
        Return a copy of the current literal
        """
        return Literal(self.label, self.state, self.negative)

    def negate(self):
        """
        Return a new Literal containing the negation of the current one
        """
        return Literal(self.label, self.state, not self.negative)

    def isDeadly(self):
        """
        Check if a literal represents a deadly state
        """
        return self.label in Labels.DEADLY

    def isWTP(self):
        """
        Check if a literal represents GhostWumpus, the Teleporter or
        a poisoned pill
        """
        return self.label in Labels.WTP

    def isSafe(self):
        """
        Check if a literal represents a safe spot
        """
        return self.label == Labels.SAFE

    def isTeleporter(self):
        """
        Check if a literal represents the teleporter
        """
        return self.label == Labels.TELEPORTER


class Clause:
    """
    A disjunction of finitely many unique literals.
    The Clauses have to be in the CNF so that resolution can be applied to them. The code
    was written assuming that the clauses are in CNF, and will not work otherwise.

    A sample of instantiating a clause (~B v C):

    >>> premise = Clause(set([Literal('b', (0, 0), True), Literal('c', (0, 0), False)]))

    or; written more clearly
    >>> LiteralNotB = Literal('b', (0, 0), True)
    >>> LiteralC = Literal('c', (0, 0), False)

    >>> premise = Clause(set([[LiteralNotB, LiteralC]]))
    """

    def __init__(self, literals):
        """
        The constructor for a clause. The clause assumes that the data passed
        is an iterable (e.g., list, set), or a single literal in case of a unit clause.
        In case of unit clauses, the Literal is wrapped in a list to be safely passed to
        the set.
        """
        if not type(literals) == set and not type(literals) == list:
            self.literals = set([literals])
        else:
            self.literals = set(literals)

    def isResolveableWith(self, otherClause):
        """
        Check if a literal from the clause is resolveable by another clause -
        if the other clause contains a negation of one of the literals.
        e.g., (~A) and (A v ~B) are examples of two clauses containing opposite literals
        """
        for literal in self.literals:
            if literal.negate() in otherClause.literals:
                return True
        return False

    def isRedundant(self, otherClauses):
        """
        Check if a clause is a subset of another clause.
        """
        for clause in otherClauses:
            if self == clause: continue
            if clause.literals.issubset(self.literals):
                return True
        return False

    def negateAll(self):
        """
        Negate all the literals in the clause to be used
        as the supporting set for resolution.
        """
        negations = set()
        for literal in self.literals:
            clause = Clause(literal.negate())
            negations.add(clause)
        return negations

    #My functions
    def isValid(self):
        for literal in self.literals:
            if literal.negate() in self.literals:
                return True
        return False

    def isNIL(self):
        return len(self.literals) == 0

    def __str__(self):
        """
        Overloading the str() operator - convert the object to a string
        """
        return ' V '.join([str(literal) for literal in self.literals])

    def __repr__(self):
        """
        The representation of the object
        """
        return self.__str__()

    def __key(self):
        """
        Return a unique key representing the literal at a given point
        """
        return tuple(sorted(list(self.literals)))

    def __hash__(self):
        """
        Return the hash value - this operator overloads the hash(object) function.
        """
        return hash(self.__key())

    def __eq__(first, second):
        """
        Check for equality - this operator overloads '=='
        """
        return first.__key() == second.__key()


def resolution(clauses, goal):
    """
    Implement refutation resolution.

    The pseudocode for the algorithm of refutation resolution can be found
    in the slides. The implementation here assumes you will use set of support
    and simplification strategies. We urge you to go through the slides and
    carefully design the code before implementing.
    """
    resolvedPairs = set()
    setOfSupport = goal.negateAll()

    clauses, setOfSupport = removeRedundant(clauses, setOfSupport)

    while True:
        newClausePairs = selectClauses(clauses, setOfSupport, resolvedPairs)
        newResolvents = set()

        for clause1, clause2 in newClausePairs:
            resolvedPairs |= set([(clause1, clause2)])

            resolvent = resolvePair(clause1, clause2)

            if resolvent.isNIL():
                return True

            newResolvents |= set([resolvent])

        if (newResolvents <= (clauses | setOfSupport)):
            return False

        setOfSupport |= newResolvents

        clauses, setOfSupport = removeRedundant(clauses, setOfSupport)

def removeRedundant(clauses, setOfSupport):
    allClauses = clauses | setOfSupport

    newClauses = []

    for clause in clauses:
        if clause.isValid() or \
                clause.isRedundant(allClauses):
            continue

        newClauses += [clause]

    newSOS = []

    for clause in setOfSupport:
        if clause.isValid() or \
                clause.isRedundant(allClauses):
            continue

        newSOS += [clause]

    return (set(newClauses), set(newSOS))

def resolvePair(firstClause, secondClause):
    #Assume they are resolveable

    for lit in firstClause.literals:
        if lit.negate() not in secondClause.literals:
            continue

        return Clause((firstClause.literals | secondClause.literals) - set([lit, lit.negate()]))

    return Clause([])

def selectClauses(clauses, setOfSupport, resolvedPairs):
    allClauses = clauses | setOfSupport
    result = set()

    for clause1 in setOfSupport:
        for clause2 in allClauses:
            if (clause1 == clause2 or \
                    (clause1, clause2) in resolvedPairs or \
                    not clause1.isResolveableWith(clause2)):
                continue

            result |= set([(clause1, clause2)])

    return result

def testResolution():
    """
    A sample of a resolution problem that should return True.
    You should come up with your own tests in order to validate your code.
    """
    premise1 = Clause(set([Literal('a', (0, 0), True), Literal('b', (0, 0), False)]))
    premise2 = Clause(set([Literal('b', (0, 0), True), Literal('c', (0, 0), False)]))
    premise3 = Clause(Literal('a', (0,0)))

    goal = Clause(Literal('c', (0,0)))
    print resolution(set([premise1, premise2, premise3]), goal)

if __name__ == '__main__':
    """
    The main function - if you run logic.py from the command line by
    >>> python logic.py

    this is the starting point of the code which will run.
    """
    testResolution()

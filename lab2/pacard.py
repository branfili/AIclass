
"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util
from logic import *

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def miniWumpusSearch(problem):
    """
    A sample pass through the miniWumpus layout. Your solution will not contain
    just three steps! Optimality is not the concern here.
    """
    from game import Directions
    e = Directions.EAST
    n = Directions.NORTH
    return  [e, n, n]

def chooseNextState(nextStates, memory):
    st = filter(lambda s: any(lit.isTeleporter() for lit in memory[s]), nextStates)
    if (len(st) != 0):
        return st[0]

    st = filter(lambda s: any(lit.isSafe() for lit in memory[s]), nextStates)
    st.sort(lambda x, y: stateWeight(x) < stateWeight(y))
    if (len(st) != 0):
        return st[0]

    st = filter(lambda s: all(not lit.isWTP() for lit in memory[s]), nextStates)
    st.sort(lambda x, y : stateWeight(x) < stateWeight(y))
    if (len(st) != 0):
        return st[0]

def logicBasedSearch(problem):
    """

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())

    print "Does the Wumpus's stench reach my spot?",
               \ problem.isWumpusClose(problem.getStartState())

    print "Can I sense the chemicals from the pills?",
               \ problem.isPoisonCapsuleClose(problem.getStartState())

    print "Can I see the glow from the teleporter?",
               \ problem.isTeleporterClose(problem.getStartState())

    (the slash '\\' is used to combine commands spanning through multiple lines -
    you should remove it if you convert the commands to a single line)

    Feel free to create and use as many helper functions as you want.

    A couple of hints:
        * Use the getSuccessors method, not only when you are looking for states
        you can transition into. In case you want to resolve if a poisoned pill is
        at a certain state, it might be easy to check if you can sense the chemicals
        on all cells surrounding the state.
        * Memorize information, often and thoroughly. Dictionaries are your friends and
        states (tuples) can be used as keys.
        * Keep track of the states you visit in order. You do NOT need to remember the
        tranisitions - simply pass the visited states to the 'reconstructPath' method
        in the search problem. Check logicAgents.py and search.py for implementation.
    """
    width = max(map(lambda (x, y): x, problem.walls.asList()))
    height = max(map(lambda (x, y): y, problem.walls.asList()))

    kl = []
    for x in range(width):
        for y in range(height):
            kl += [(x, y)]

    allStates = set(kl)

    baseKnowledge = set()
    for cur in allStates:
        succ = map(lambda (s, a, c): s, problem.getSuccessors(cur))

        succ2 = []
        for st1 in succ:
            for st2 in succ:
                if (st1 != st2):
                    succ2 += [(st1, st2)]

        baseKnowledge |= set([Clause(set([Literal(Labels.WUMPUS_STENCH, cur, True)] + [Literal(Labels.WUMPUS, sc, False) for sc in succ]))])
        baseKnowledge |= set([Clause(set([Literal(Labels.WUMPUS_STENCH, cur, False), Literal(Labels.WUMPUS, sc, True)])) for sc in succ])

        baseKnowledge |= set([Clause(set([Literal(Labels.POISON_FUMES, cur, True)] + [Literal(Labels.POISON, sc, False) for sc in succ]))])
        baseKnowledge |= set([Clause(set([Literal(Labels.POISON_FUMES, cur, False), Literal(Labels.POISON, sc, True)])) for sc in succ])

        baseKnowledge |= set([Clause(set([Literal(Labels.TELEPORTER_GLOW, cur, True)] + [Literal(Labels.TELEPORTER, sc, False) for sc in succ]))])
        baseKnowledge |= set([Clause(set([Literal(Labels.TELEPORTER_GLOW, cur, False), Literal(Labels.TELEPORTER, sc, True)])) for sc in succ])

        baseKnowledge |= set([Clause(set([Literal(Labels.WUMPUS, cur, True), Literal(Labels.WUMPUS, st, True)])) for st in allStates - set([cur])])
        baseKnowledge |= set([Clause(set([Literal(Labels.POISON_FUMES, cur, False), Literal(Labels.WUMPUS_STENCH, cur, False), Literal(Labels.SAFE, sc, False)])) for sc in succ])

        baseKnowledge |= set([Clause(set([Literal(Labels.WUMPUS, cur, False), Literal(Labels.POISON, cur, False), Literal(Labels.SAFE, cur, False)]))])

        baseKnowledge |= set([Clause(set([Literal(Labels.WUMPUS_STENCH, st1, True), Literal(Labels.WUMPUS_STENCH, st2, True), Literal(Labels.WUMPUS, cur, False)])) for (st1, st2) in succ2])

        baseKnowledge |= set([Clause(set([Literal(Labels.TELEPORTER_GLOW, st1, True), Literal(Labels.TELEPORTER_GLOW, st2, True), Literal(Labels.TELEPORTER, cur, False)])) for (st1, st2) in succ2])

        if (cur == (0, 0)):
            for clause in baseKnowledge:
                print(clause)

    # array in order to keep the ordering
    visitedStates = []
    startState = problem.getStartState()

    nextStates = [startState]
    memory = {s: set() for s in allStates}
    explored = set()

    while len(nextStates) != 0:
        s = chooseNextState(nextStates, memory)
        if (s is None):
            break

        nextStates.remove(s)

        if Labels.TELEPORTER in memory[s]:
            if (s in visitedStates):
                visitedStates += [s]
            break

        if (s in visitedStates):
            continue

        visitedStates += [s]

        if (problem.isWumpusClose(s)):
            stenchClause = Clause(set([Literal(Labels.WUMPUS_STENCH, s, False)]))
            memory[s] |= set([stenchClause])
            explored |= set([stenchClause])

        if (problem.isPoisonCapsuleClose(s)):
            fumesClause = Clause(set([Literal(Labels.POISON_FUMES, s, False)]))
            memory[s] |= set([fumesClause])
            explored |= set([fumesClause])

        if (problem.isTeleporterClose(s)):
            glowClause = Clause(set([Literal(Labels.TELEPORTER_GLOW, s, False)]))
            memory[s] |= set([glowClause])
            explored |= set([glowClause])

        succ = map(lambda (sc, c, a): sc, problem.getSuccessors(s))
        for sc in succ:
            wumpusClause = Clause(set[Literal(Labels.WUMPUS, sc, False)])
            teleporterClause = Clause(set[Literal(Labels.TELEPORTER, sc, False)])
            poisonClause = Clause(set[Literal(Labels.POISON, sc, False)])
            safeClause = Clause(set[Literal(Labels.SAFE, sc, False)])

            for clause in [teleporterClause, wumpusClause, poisonClause, safeClause]:
                if (resolution(baseKnowledge | explored, clause)):
                    memory[sc] |= set([clause])
                    explored |= set([clause])

                    literal = clause.pop()
                    clause = set([literal])

                    if (not literal.isDeadly()):
                        nextState += [sc]
                        break
                elif (resolution(baseKnowledge | explored, clause.negateAll().pop())):
                    memory[sc] |= clause.negateAll()
                    explored |= clause.negateAll()

                    if (clause == safeClause):
                        nextState += [sc]

    return problem.reconstructPath(visitedStates)

# Abbreviations
lbs = logicBasedSearch


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

#my functions
def chooseNextState(nextStates, memory):
    st = filter(lambda s: any(cl.getFirst().isTeleporter() for cl in memory[s]), nextStates)
    if (len(st) != 0):
        return st[0]

    st = filter(lambda s: any(cl.getFirst().isSafe() for cl in memory[s]), nextStates)
    st.sort(lambda x, y: stateWeight(x) < stateWeight(y))
    if (len(st) != 0):
        return st[0]

    st = filter(lambda s: safe(memory[s]), nextStates)
    st.sort(lambda x, y : stateWeight(x) < stateWeight(y))
    if (len(st) != 0):
        return st[0]

def environment(baseKnowledge, exploredKnowledge, allStates, d, cur):
    result = set()

    for st in allStates:
        if (util.manhattanDistance(cur, st) > d):
            continue

        for clause in (baseKnowledge[st] | exploredKnowledge[st]):
            flag = True

            for lit in clause.literals:
                st2 = lit.getState()
                if (util.manhattanDistance(cur, st2) > d):
                    flag = False
                    break

            if (flag):
                result |= set([clause])

    return result

def safe(knowledge):
    if (len(knowledge)) == 0:
        return True

    return all(not cl.getFirst().isDeadly() for cl in knowledge)

def outOfBounds(st, width, height):
    return (st[0] <= 0 or \
            st[0] >= width - 1 or \
            st[1] <= 0 or \
            st[1] >= height - 1)

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

    from itertools import product

    allStates = set(product(range(1, width), range(1, height)))

    bk = {st: set() for st in allStates}

    for cur in allStates:
        succ = map(lambda (s, a, c): s, problem.getSuccessors(cur))

        if (problem.walls[cur[0]][cur[1]]):
            for label in Labels.UNIQUE:
                bk[cur] |= set([Clause(Literal(label, cur, True))])
            bk[cur] |= set([Clause(Literal(Labels.WALL, cur, False))])
            continue

        bk[cur] |= set([Clause(set([Literal(Labels.WUMPUS_STENCH, cur, True)] +
                              [Literal(Labels.WUMPUS, sc, False) for sc in succ]))])

        bk[cur] |= set([Clause(set([Literal(Labels.WUMPUS_STENCH, cur, False),
                               Literal(Labels.WUMPUS, sc, True)]))
                               for sc in succ])

        bk[cur] |= set([Clause(set([Literal(Labels.POISON_FUMES, cur, True)] +
                              [Literal(Labels.POISON, sc, False) for sc in succ]))])

        bk[cur] |= set([Clause(set([Literal(Labels.POISON_FUMES, cur, False),
                               Literal(Labels.POISON, sc, True)]))
                               for sc in succ])

        bk[cur] |= set([Clause(set([Literal(Labels.TELEPORTER_GLOW, cur, True)] +
                              [Literal(Labels.TELEPORTER, sc, False) for sc in succ]))])

        bk[cur] |= set([Clause(set([Literal(Labels.TELEPORTER_GLOW, cur, False),
                                       Literal(Labels.TELEPORTER, sc, True)]))
                                       for sc in succ])

        bk[cur] |= set([Clause(set([Literal(Labels.POISON_FUMES, cur, False),
                               Literal(Labels.WUMPUS_STENCH, cur, False),
                               Literal(Labels.SAFE, sc, False)]))
                               for sc in succ])

        bk[cur] |= set([Clause(set([Literal(Labels.WUMPUS, cur, False),
                               Literal(Labels.POISON, cur, False),
                               Literal(Labels.SAFE, cur, False)]))])

        bk[cur] |= set([Clause(set([Literal(label, cur, True),
                                    Literal(Labels.SAFE, cur, True)]))
                                    for label in [Labels.WUMPUS,
                                                  Labels.POISON]])

        from game import Directions
        from game import Actions

        for action in [Directions.NORTH, Directions.EAST, Directions.SOUTH, Directions.WEST]:
            x, y = cur
            dxF, dyF = Actions.directionToVector(action)
            dxR, dyR = Actions.directionToVector(Directions.RIGHT[action])
            dxA, dyA = Actions.directionToVector(Directions.REVERSE[action])

            sucF = int(x + dxF), int(y + dyF)
            sucR = int(x + dxR), int(y + dyR)
            sucFR = int(x + dxF + dxR), int(y + dyF + dyR)

            if (all(not outOfBounds(p, width, height) for p in [sucF, sucR, sucFR])):
                bk[cur] |= set([Clause(set([Literal(Labels.WUMPUS_STENCH, sucF, True),
                                            Literal(Labels.WUMPUS_STENCH, sucR, True),
                                            Literal(Labels.WUMPUS, sucFR, False),
                                            Literal(Labels.WUMPUS, cur, False)]))])

                bk[cur] |= set([Clause(set([Literal(Labels.TELEPORTER_GLOW, sucF, True),
                                            Literal(Labels.TELEPORTER_GLOW, sucR, True),
                                            Literal(Labels.TELEPORTER, sucFR, False),
                                            Literal(Labels.TELEPORTER, cur, False)]))])

            sucA = int(x + dxA), int(y + dyA)

            if (all(not outOfBounds(p, width, height) for p in [sucF, sucA])):
                bk[cur] |= set([Clause(set([Literal(Labels.WUMPUS_STENCH, sucF, True),
                                            Literal(Labels.WUMPUS_STENCH, sucA, True),
                                            Literal(Labels.WUMPUS, cur, False)]))])

                bk[cur] |= set([Clause(set([Literal(Labels.TELEPORTER_GLOW, sucF, True),
                                            Literal(Labels.TELEPORTER_GLOW, sucA, True),
                                            Literal(Labels.TELEPORTER, cur, False)]))])

            sucFF = int(x + 2 * dxF), int(y + 2 * dyF)

            if (all (not outOfBounds(p, width, height) for p in [sucR, sucF, sucFR, sucFF])):
                bk[cur] |= set([Clause(set([Literal(Labels.POISON, sucR, True),
                                            Literal(Labels.POISON_FUMES, sucF, True),
                                            Literal(Labels.POISON_FUMES, sucFR, True),
                                            Literal(Labels.POISON, sucFF, False),
                                            Literal(Labels.POISON, cur, False)]))])

    # array in order to keep the ordering
    visitedStates = []
    startState = problem.getStartState()

    nextStates = [startState]
    memory = {s: set() for s in allStates}

    RADIUS = 2

    while len(nextStates) != 0:
        s = chooseNextState(nextStates, memory)
        if (s is None):
            break

        nextStates.remove(s)

        if (problem.isGoalState(s)):
            visitedStates += [s]
            break

        if (s in visitedStates):
            continue

        visitedStates += [s]

        for label in Labels.WTP:
            memory[s] |= set([Clause(Literal(label, s, True))])

        stenchClause = Clause(Literal(Labels.WUMPUS_STENCH, s, not problem.isWumpusClose(s)))
        memory[s] |= set([stenchClause])

        fumesClause = Clause(Literal(Labels.POISON_FUMES, s, not problem.isPoisonCapsuleClose(s)))
        memory[s] |= set([fumesClause])

        glowClause = Clause(Literal(Labels.TELEPORTER_GLOW, s, not problem.isTeleporterClose(s)))
        memory[s] |= set([glowClause])

        print (s)
        for clause in memory[s]:
            print (clause)
        print

        succ = map(lambda (sc, c, a): sc, problem.getSuccessors(s))
        for sc in succ:
            if (sc in visitedStates):
                continue

            wumpusLiteral = Literal(Labels.WUMPUS, sc, False)
            teleporterLiteral = Literal(Labels.TELEPORTER, sc, False)
            poisonLiteral = Literal(Labels.POISON, sc, False)
            safeLiteral = Literal(Labels.SAFE, sc, False)

            for literal in [teleporterLiteral, wumpusLiteral, poisonLiteral, safeLiteral]:
                clause = Clause(literal)
                negClause = Clause(literal.negate())

                if (set([clause, negClause]) & memory[sc] != set([])):
                    continue

                relevantKnowledge = environment(bk, memory, allStates, RADIUS, sc)

                if (resolution(relevantKnowledge, negClause)):
                    memory[sc] |= set([negClause])
                    continue

                if (resolution(relevantKnowledge, clause)):
                    memory[sc] |= set([clause])

                    if (not literal.isDeadly()):
                        nextStates += [sc]
                        break
                    elif (literal == wumpusLiteral):
                        for st in allStates - set([sc]):
                            memory[st] |= set([Clause(Literal(Labels.WUMPUS, st, True))])

            if (sc not in nextStates and \
                    safe(memory[sc])):
                nextStates += [sc]

    return problem.reconstructPath(visitedStates)

# Abbreviations
lbs = logicBasedSearch

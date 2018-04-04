
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
    allStates = set()
    for x in range(20):
        for y in range(20):
            allStates |= set([(x, y)])

    baseKnowledge = set()

    for cur in allStates:
        cur = (x, y)
        succ = problem.getSuccessors(cur)
        ns = set()

        ns |= set([Clause(set([Literal('S', cur, True)] + [Literal('W', sc, False) for sc in succ]))])
        ns |= set([Clause(set([Literal('S', cur, False), Literal('W', sc, True)])) for sc in succ])

        ns |= set([Clause(set([Literal('C', cur, True)] + [Literal('P', sc, False) for sc in succ]))])
        ns |= set([Clause(set([Literal('C', cur, False), Literal('P', sc, True)])) for sc in succ])

        ns |= set([Clause(set([Literal('G', cur, True)] + [Literal('T', sc, False) for sc in succ]))])
        ns |= set([Clause(set([Literal('G', cur, False), Literal('T', sc, True)])) for sc in succ])

        ns |= set([Clause(set([Literal('W', cur, True), Literal('W', st, True)])) for st in diff(allStates, set([cur]))])
        ns |= set([Clause(set([Literal('C', cur, False), Literal('S', cur, False), Literal('O', sc, False)])) for sc in succ])

        ns |= set([Clause(set([Literal('W', cur, False), Literal('P', cur, False), Literal('O', cur, False)]))])

        baseKnowledge |= ns

    # array in order to keep the ordering
    visitedStates = []
    startState = problem.getStartState()
    visitedStates.append(startState)

    q = Queue()
    q.push(startState)

    memory = {}
    memory[s] = ""


    while not q.isEmpty():
        s = q.pop()

        if (s in visitedStates):
            continue

        visitedStates.append(s)

        if 'T' in memory[s]:
            return problem.reconstructPath(visitedStates)

# Abbreviations
lbs = logicBasedSearch

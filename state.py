# -*- coding: utf-8 -*-

# Class State
# To solve a problem, you must define a sub-class of the class State that redefines these methods

class State:
    # State is changed according to action
    def executeActions(self, action):
        pass

    # Checks whether current state and the one in parameter are  the same
    def equals(self, state):
        return False

    # Checks whether the state is a goal state
    def isGoal(self):
        return False

    # Prints to the console a description of the state
    def show(self):
        pass

    # update State based on action
    def executeAction(self, action):
        pass

    # Returns a list of possible actions from the current state
    def possibleActions(self):
        return []

    # Returns the cost of executing some action from that state
    # By default, we suppose that all actions have the same cost = 1
    def cost(self, action):
        return 1

    # Returns a heuristic value that provides an estimate of the remaining
    # cost to reach the goal
    # By default, value is 0 - an optimistic heuristic!
    def heuristic(self):
        return 0
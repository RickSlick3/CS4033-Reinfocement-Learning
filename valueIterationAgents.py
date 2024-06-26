# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for _ in range(self.iterations):
            
            returnValues = util.Counter()
            
            for state in self.mdp.getStates():
                
                if self.mdp.isTerminal(state):
                    returnValues[state] = 0
                else:
                    bestAction = self.computeActionFromValues(state)
                    returnValues[state] = self.computeQValueFromValues(state, bestAction)
        
            self.values = returnValues

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        QValue = 0
        transitionStatesAndProbs = self.mdp.getTransitionStatesAndProbs(state, action)
        
        for (nextState, prob) in transitionStatesAndProbs:
            
            reward = self.mdp.getReward(state, action, nextState)
            QValue = QValue + (prob * (reward + (self.discount * self.values[nextState])))
        
        return QValue

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        
        if self.mdp.isTerminal(state):
            return None
        
        else:
            possibleActions = self.mdp.getPossibleActions(state)
            
            bestAction = possibleActions[0]
            bestQValue = self.getQValue(state, bestAction)
            
            for possibleAction in possibleActions[1:]:
                
                Qvalue = self.getQValue(state, possibleAction)
                if Qvalue > bestQValue:
                    bestAction = possibleAction
                    bestQValue = Qvalue
            
            return bestAction

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()
        numberOfStates = len(states)
        
        for iter in range(self.iterations):
            
            state = states[iter % numberOfStates]
            
            if not self.mdp.isTerminal(state):
                
                possibleActions = self.mdp.getPossibleActions(state)
                bestQValue = self.getQValue(state, possibleActions[0])
                
                for possibleAction in possibleActions[1:]:
                    
                    QValue = self.getQValue(state, possibleAction)
                    if QValue > bestQValue:
                        bestQValue = QValue
                        
                self.values[state] = bestQValue

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        predecessors = dict()
        
        priorityQueue = util.PriorityQueue()
        
        states = self.mdp.getStates()
        
        # For each non-terminal state s, do:
        for s in states:
            
            if not self.mdp.isTerminal(s):
            
                # Compute predecessors of all states
                for possibleAction in self.mdp.getPossibleActions(s):
                    for (nextState, prob) in self.mdp.getTransitionStatesAndProbs(s, possibleAction):
                            
                            if nextState in predecessors:
                                predecessors[nextState].add(s)
                            else:
                                predecessors[nextState] = set([s])
                
                # Find the absolute value of the difference between the current value of
                # s in self.values and the highest Q-value across all possible actions from s
                bestAction = self.computeActionFromValues(s)
                diff = abs(self.values[s] - self.getQValue(s, bestAction))
                # Push s into the priority queue with priority -dif
                priorityQueue.push(s, -diff)

        # For iteration in 0, 1, 2, . . . , self.iterations - 1, do:
        for _ in range(self.iterations):
            
            # If the priority queue is empty, then terminate
            if priorityQueue.isEmpty():
                return
            
            # Pop a state s off the priority queue
            s = priorityQueue.pop()

            # if it is not a terminal state
            if not self.mdp.isTerminal(s):
                
                # Update s’s value (if it is not a terminal state) in self.values
                bestAction = self.computeActionFromValues(s)
                self.values[s] = self.computeQValueFromValues(s, bestAction)

            # For each predecessor p of s, do:
            for p in predecessors[s]:

                # Find the absolute value of the difference between the current value of p in 
                # self.values and the highest Q-value across all possible actions from p
                bestAction = self.computeActionFromValues(p)
                diff = abs(self.values[p] - self.computeQValueFromValues(p, bestAction))
                
                # If diff > theta, push p into the priority queue with priority -diff
                if diff > self.theta:
                    # update method
                    priorityQueue.update(p, -diff)


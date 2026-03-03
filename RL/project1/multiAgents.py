# multiAgents.py
# --------------
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


from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        best = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == best]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best
        
        "Add more of your code here if you want to"

        
        
        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Evaluation function for your reflex agent (question 1).

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """

        "*** YOUR CODE HERE ***"
        """ Config & SetUp """
        from util import manhattanDist
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newFood = successorGameState.getFood()
        newPos = successorGameState.getPacmanPosition()
        
        E = 1e-05
        
        """ === Parameter === """
        # food 
        w1 = 1 # I gave extra points to food that was close to me, but it didn't seem to work like a score - it was an illusion that I executed it wrong
        w2 = 0.1 # Penalties decrease as food is reduced best: 0.1
        
        # capsule
        w3 = 0.5 # The closer you are, the more points you give capsule distance
        w4 = 1 # Penalties decrease as capsules shrink
        
        # ghost
        w5 = 2 # Scared Ghosts The Closer You Get, the Score
        w6 = 200 # If the ghost is too close, it's the same even if you get a bigger penalty
        w7 = 2 # If the ghost is close, a penalty
        
        # action
        w8 = 0 # If the penalty exceeds 0.2 when stopped, the action that is greatly reduced does not have a significant effect
        
        # Ghost and Agent Hazard Distance
        GAP = 2
        
        """ === Metric === """
        f1_score = 0
        f2_score = 0
        c1_score = 0
        c2_score = 0
        g1_score = 0
        g2_score = 0
        g3_score = 0
        a1_score = 0
        """ food """
        foodPos = successorGameState.getFood().asList()
        foodDists = [manhattanDist(newPos, i_foodPos) for i_foodPos in foodPos]
        
        # Give extra points for close food
        if foodDists:
            f1_score = 1 / (min(foodDists)+E)
            # f1_score = sum(1 / (d+E) for d in foodDists)
        else:
            f1_score = 0

        foodDists = [1/(x+E) for x in foodDists] # Inverse take and add - originally reverse take and find, but correct order because small values are added
        # The less food you eat, the less penalty you get
        f2_score = (-1) * len(foodPos)

        # score
        f_score = w1*f1_score + w2*f2_score
        
        """ Capsule """
        capsulePos = successorGameState.getCapsules()
        
        # Additional points as capsules get closer
        if capsulePos:
            capDists = [manhattanDist(newPos, c) for c in capsulePos]
            c1_score = 1 / (min(capDists) + E)
        else:
            c1_score = 0.0
    
        # Penalties decrease as capsules shrink
        c2_score = (-1) * len(capsulePos)

        # score
        c_score = w3*c1_score + w4*c2_score
        
        """ Ghost """
        ghostStates = successorGameState.getGhostStates()
        ghostPos = successorGameState.getGhostPositions()
        
        # Scared ghost extra points, the closer the ghost is, the bigger the penalty
        for i, pos in enumerate(ghostPos):
            dist = manhattanDist(newPos, pos)
            scaredTimer = ghostStates[i].scaredTimer
            if scaredTimer > 0:
                g1_score += 1 / (dist + E)
            else:
                if dist <= GAP: # I set Gap to 1, but I kept failing in process 3, I tried increasing it without thinking, but the performance got much better
                    g2_score += (-1)
                else:
                    g3_score += (-1) / (dist + E)
                    
        # score
        g_score = w5*g1_score + w6*g2_score + w7*g3_score
        
        """ Action """ 
        if action == 'Stop': # There were several cases, but 0~0.2 was the highest point, so use it as 0
            a1_score = (-1)

        a_score = w8*a1_score
        
        """ === score === """
        score = successorGameState.getScore() + f_score + c_score + g_score + a_score
        return score

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        
        numAgents = gameState.getNumAgents()

        def value(gameState, index, depth):
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            
            if index == 0:
                return max_value(gameState, index, depth)
            else:
                return min_value(gameState, index, depth)
        
        
        def max_value(gameState, index, depth):
            legalAction = gameState.getLegalActions(index)
            max_v = float("-inf")
                        
            if legalAction:
                for currentAction in legalAction:
                    succesors = gameState.generateSuccessor(index, currentAction)
                    nextAgent = (index+1) % numAgents 
                    check = value(succesors, nextAgent, depth)
                    if check > max_v:
                        max_v = check
                return max_v

            else:
                return self.evaluationFunction(gameState)
                    
        def min_value(gameState, index, depth):
            legalAction = gameState.getLegalActions(index)
            min_v = float("inf")
                        
            if legalAction:
                for currentAction in legalAction:
                    succesors = gameState.generateSuccessor(index, currentAction)
                    nextAgent = (index+1) % numAgents
                    
                    if nextAgent == 0:
                        nextDepth = depth + 1
                    else:
                        nextDepth = depth
                    check = value(succesors, nextAgent, nextDepth)
                    if check <= min_v:
                        min_v = check
                return min_v

            else:
                return self.evaluationFunction(gameState)
        
        best = float("-inf")
        bestAction = None
        for a in gameState.getLegalActions(0):
            successors = gameState.generateSuccessor(0, a)
            # The first index of ghosts is 1, and the depth is still zero
            score = value(successors, 1%numAgents, 0)
            if score > best:
                best = score
                bestAction = a
        return bestAction

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        numAgents = gameState.getNumAgents()

        def value(gameState, index, alpha, beta, depth):
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            
            if index == 0:
                return max_value(gameState, index, alpha, beta, depth)
            else:
                return min_value(gameState, index, alpha, beta, depth)
        
        
        def max_value(gameState, index, alpha, beta, depth):
            legalAction = gameState.getLegalActions(index)
            max_v = float("-inf")
                        
            if legalAction:
                for currentAction in legalAction:
                    succesors = gameState.generateSuccessor(index, currentAction)
                    nextAgent = (index+1) % numAgents 
                    
                    if nextAgent == 0:
                        nextDepth = depth + 1
                    else:
                        nextDepth = depth
                        
                    check = value(succesors, nextAgent, alpha,  beta, nextDepth)
                    if check > max_v:
                        max_v = check
                    if max_v > alpha:
                        alpha = max_v
                    if max_v >= beta:
                        return max_v
                    
                return max_v
            else:
                return self.evaluationFunction(gameState)
                    
        def min_value(gameState, index, alpha, beta, depth):
            legalAction = gameState.getLegalActions(index)
            min_v = float("inf")
                        
            if legalAction:
                for currentAction in legalAction:
                    succesors = gameState.generateSuccessor(index, currentAction)
                    nextAgent = (index+1) % numAgents
                    
                    if nextAgent == 0:
                        nextDepth = depth + 1
                    else:
                        nextDepth = depth

                    check = value(succesors, nextAgent, alpha, beta, nextDepth)
                    if check <= min_v:
                        min_v = check
                        
                    if min_v < beta:
                        beta = min_v
                    if min_v < alpha:
                        return min_v
                return min_v

            else:
                return self.evaluationFunction(gameState)
        
        best = float("-inf")
        alpha, beta = float("-inf"), float("inf")
        bestAction = None
        for a in gameState.getLegalActions(0):
            successors = gameState.generateSuccessor(0, a)
            # The first index of ghosts is 1, and the depth is still zero
            nextIndex = 1 % numAgents
            if nextIndex == 0:
                nextDepth = 1
            else:
                nextDepth = 0
            score = value(successors, 1 % numAgents, alpha, beta, nextDepth)
            
            if score > best:
                best = score
                bestAction = a
            if best >= beta:
                break
            if best > alpha:
                alpha = best
        # util.raiseNotDefined()
        return bestAction


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        
        numAgents = gameState.getNumAgents()

        def value(gameState, index, depth):
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            
            if index == 0:
                return max_value(gameState, index, depth)
            else:
                return exp_value(gameState, index, depth)
        
        
        def max_value(gameState, index, depth):
            legalAction = gameState.getLegalActions(index)
            max_v = float("-inf")
                        
            if legalAction:
                for currentAction in legalAction:
                    succesors = gameState.generateSuccessor(index, currentAction)
                    nextAgent = (index+1)%numAgents 
                    check = value(succesors, nextAgent, depth)
                    if check > max_v:
                        max_v = check
                return max_v

            else:
                return self.evaluationFunction(gameState)
                    
        def exp_value(gameState, index, depth):
            legalAction = gameState.getLegalActions(index)
            exp_v = 0
            p = 1 / len(legalAction)
                        
            if legalAction:
                for currentAction in legalAction:
                    succesors = gameState.generateSuccessor(index, currentAction)
                    nextAgent = (index+1)%numAgents
                    
                    if nextAgent == 0:
                        nextDepth = depth + 1
                    else:
                        nextDepth = depth
                    
                    check = value(succesors, nextAgent, nextDepth)
                    
                    exp_v += p*check
                    
                return exp_v

            else:
                return self.evaluationFunction(gameState)
        
        best = float("-inf")
        bestAction = None
        for a in gameState.getLegalActions(0):
            successors = gameState.generateSuccessor(0, a)
            score = value(successors, 1%numAgents, 0)
            if score > best:
                best = score
                bestAction = a
        return bestAction
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    The number of leftovers is better: If there are many leftovers, it is applied as a penalty term
    Good if it doesn't stop: If it stops, it's applied as a penalty
    Just ghost: The further away, the better
    Scared Ghost: The Closer the Better
    Capsule: I've already eaten it, so the less, the better
    Idea: The performance adds a very small value before and after the distance conversion - much better before the distance conversion. It is expected that unnecessary values have disappeared by not adding a small value before taking the reciprocal
    """
    "*** YOUR CODE HERE ***"
    E = 1e-5
    newPos = currentGameState.getPacmanPosition()
    from util import manhattanDist
    
    """ === Parameter === """
    # food 
    w1 = 1 # Give extra points to food that is close to you
    w2 = 0.1 # Penalties decrease as food is reduced
    
    # capsule
    w3 = 0.5 # The closer you are, the more points you give capsule distance
    w4 = 1 # Penalties decrease as capsules shrink
    
    # ghost
    w5 = 2 # Scared Ghosts The Closer You Get, the Score
    w6 = 200 # If the ghost is too close, it's the same even if you get a bigger penalty
    w7 = 2 # If the ghost is close, a penalty
    
    """ === Metric === """
    f1_score = 0
    f2_score = 0
    c1_score = 0
    c2_score = 0
    g1_score = 0
    g2_score = 0
    g3_score = 0
    
    """ Food """
    foodPos = currentGameState.getFood().asList()
    foodDists = [manhattanDist(newPos, i_foodPos) for i_foodPos in foodPos]

    # Additional score for close food
    if foodPos:
        f1_score = 1 / (min(foodDists) + E)
    else:
        f1_score = 0

    foodDists = [1/(x+E) for x in foodDists] # Take the reverse and add
    # The less food you eat, the less penalty you get
    f2_score = (-1) * len(foodPos)

    # score
    f_score = w1*f1_score + w2*f2_score

    """ Capsule """
    capsulePos = currentGameState.getCapsules()
    # The closer the capsule is, the more points you get
    if capsulePos:
        capDists = [manhattanDist(newPos, c) for c in capsulePos]
        c1_score = 1 / (min(capDists) + E)
    else:
        c1_score = 0.0
    # Penalties decrease as capsules shrink
    c2_score = (-1) * len(capsulePos)
    c_score = w3*c1_score + w4*c2_score
    
    """ Ghost """
    ghostStates = currentGameState.getGhostStates()
    ghostPos = currentGameState.getGhostPositions()

    # Scared ghost extra points, the closer the ghost is, the bigger the penalty
    for i, gpos in enumerate(ghostPos):
        dist = manhattanDist(newPos, gpos)
        scaredTimer = ghostStates[i].scaredTimer
        if scaredTimer > 0:
            g1_score += 1 / (dist + E)
        else:
            if dist <= 1:
                g2_score += (-1)
            else:
                g3_score += (-1) / (dist + E)

    g_score = w5*g1_score + w6*g2_score + w7*g3_score


    score = currentGameState.getScore() + f_score + c_score + g_score
    return score

# Abbreviation
better = betterEvaluationFunction

# multiAgents.py
# --------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
  """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
  """


  def getAction(self, gameState):
    """
    You do not need to change this method, but you're welcome to.

    getAction chooses among the best options according to the evaluation function.

    Just like in the previous project, getAction takes a GameState and returns
    some Directions.X for some X in the set {North, South, West, East, Stop}
    """
    # Collect legal moves and successor states
    legalMoves = gameState.getLegalActions()

    # Choose one of the best actions
    scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
    bestScore = max(scores)
    bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
    chosenIndex = random.choice(bestIndices) # Pick randomly among the best

    "Add more of your code here if you want to"

    return legalMoves[chosenIndex]

  def evaluationFunction(self, currentGameState, action):
    """
    Design a better evaluation function here.

    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    The code below extracts some useful information from the state, like the
    remaining food (newFood) and Pacman position after moving (newPos).
    newScaredTimes holds the number of moves that each ghost will remain
    scared because of Pacman having eaten a power pellet.

    Print out these variables to see what you're getting, then combine them
    to create a masterful evaluation function.
    """
    # Useful information you can extract from a GameState (pacman.py)
    successorGameState = currentGameState.generatePacmanSuccessor(action)
    newPos = successorGameState.getPacmanPosition()
    newFood = successorGameState.getFood()
    oldFood = currentGameState.getFood()

    "*** YOUR CODE HERE ***"
    from decimal import Decimal
    import sys
    minFoodDist = sys.maxint

    if successorGameState.isWin(): return sys.maxint
    if successorGameState.isLose(): return -sys.maxint

    if newPos in oldFood.asList():
      minFoodDist = 1
    else:
      for foodPos in newFood.asList():
        minFoodDist = min(minFoodDist, manhattanDistance(foodPos, newPos))

      minFoodDist = Decimal(1.0 / (minFoodDist * len(newFood.asList())))

    sumGhost = 0
    for ghostPos in successorGameState.getGhostPositions():
      dist = manhattanDistance(ghostPos, newPos)
      sumGhost = sumGhost + Decimal(dist) if dist != 0 else 0


    return Decimal(minFoodDist)*Decimal(sumGhost)

def scoreEvaluationFunction(currentGameState):
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
  import itertools
  import copy
  import sys

  def getAction(self, gameState):
    """
      Returns the minimax action from the current gameState using self.depth
      and self.evaluationFunction.

      Here are some method calls that might be useful when implementing minimax.

      gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

      Directions.STOP:
        The stop direction, which is always legal

      gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

      gameState.getNumAgents():
        Returns the total number of agents in the game
    """
    "*** YOUR CODE HERE ***"
    totalAgentNum = gameState.getNumAgents()
    indexCurAgent = self.index
    finalDirection = self.MinMaxValueHelper(gameState, indexCurAgent, totalAgentNum, 0)[1]

    return finalDirection

  def MinMaxValueHelper(self, currentState, indexCurAgent, totalAgentNum, depth):

    if self.checkGameState(currentState, depth):
      return (self.evaluationFunction(currentState), None)

    succIndexCurAgent = 0 if indexCurAgent + 1 == totalAgentNum else indexCurAgent + 1

    depth += 1 if succIndexCurAgent == 0 else 0

    from util import PriorityQueue

    if not indexCurAgent == 0:
      pq = PriorityQueue()
      ghostsActions = currentState.getLegalActions(indexCurAgent)
      for ghostAction in ghostsActions:
        _succState = currentState.generateSuccessor(indexCurAgent, ghostAction)
        _value = self.MinMaxValueHelper(_succState, succIndexCurAgent, totalAgentNum, depth)[0]
        pq.push((_value, ghostAction), _value)
      return pq.pop()

    else:
      pq = PriorityQueue()
      ghostsActions = currentState.getLegalActions(indexCurAgent)
      for ghostAction in ghostsActions:
        _succState = currentState.generateSuccessor(indexCurAgent, ghostAction)
        _value = self.MinMaxValueHelper(_succState, succIndexCurAgent, totalAgentNum, depth)[0]
        pq.push((_value, ghostAction), -_value)
      return pq.pop()

  def checkGameState(self, currentState, depth):
    if depth >= self.depth:
      return True
    elif currentState.isWin() or currentState.isLose():
      return True
    else:
      return False


class AlphaBetaAgent(MultiAgentSearchAgent):
  """
    Your minimax agent with alpha-beta pruning (question 3)
  """
  import itertools
  import copy
  import sys
  import random
  def getAction(self, gameState):
    """
      Returns the minimax action using self.depth and self.evaluationFunction
    """
    "*** YOUR CODE HERE ***"
    alpha = -self.sys.maxint
    beta = self.sys.maxint
    totalAgentNum = gameState.getNumAgents()
    indexCurAgent = self.index
    finalDirection = self.MinMaxValueHelper(gameState, indexCurAgent, totalAgentNum, 0, alpha, beta)[1]

    return finalDirection

  def MinMaxValueHelper(self, currentState, indexCurAgent, totalAgentNum, depth, alpha, beta):

    if self.checkGameState(currentState, depth):
      return (self.evaluationFunction(currentState), None)

    succIndexCurAgent = 0 if indexCurAgent + 1 == totalAgentNum else indexCurAgent + 1

    depth += 1 if succIndexCurAgent == 0 else 0

    from util import PriorityQueue

    if not indexCurAgent == 0:
      pq = PriorityQueue()
      ghostsActions = currentState.getLegalActions(indexCurAgent)
      for ghostAction in ghostsActions:
        _succState = currentState.generateSuccessor(indexCurAgent, ghostAction)
        _value = self.MinMaxValueHelper(_succState, succIndexCurAgent, totalAgentNum, depth, alpha, beta)[0]
        pq.push((_value, ghostAction), _value)
        if pq.heap[0][1][0] < alpha:
          break
        else:
          beta = min(beta, pq.heap[0][1][0])
      return pq.pop()

    else:
      pq = PriorityQueue()
      ghostsActions = currentState.getLegalActions(indexCurAgent)
      for ghostAction in ghostsActions:
        _succState = currentState.generateSuccessor(indexCurAgent, ghostAction)
        _value = self.MinMaxValueHelper(_succState, succIndexCurAgent, totalAgentNum, depth, alpha, beta)[0]
        pq.push((_value, ghostAction), -_value)
        if pq.heap[0][1][0] > beta:
          break
        else:
          alpha = max(alpha, pq.heap[0][1][0])
      return pq.pop()

  def checkGameState(self, currentState, depth):
    if depth >= self.depth:
      return True
    elif currentState.isWin() or currentState.isLose():
      return True
    else:
      return False

class ExpectimaxAgent(MultiAgentSearchAgent):
  """
    Your expectimax agent (question 4)
  """

  import itertools
  import copy
  import sys
  import random

  def getAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    "*** YOUR CODE HERE ***"
    alpha = -self.sys.maxint
    beta = self.sys.maxint
    totalAgentNum = gameState.getNumAgents()
    indexCurAgent = self.index
    finalDirection = self.MinMaxValueHelper(gameState, indexCurAgent, totalAgentNum, 0, alpha, beta)[1]

    return finalDirection

  def MinMaxValueHelper(self, currentState, indexCurAgent, totalAgentNum, depth, alpha, beta):

    from util import PriorityQueue

    if self.checkGameState(currentState, depth):
      return (self.evaluationFunction(currentState), None)

    succIndexCurAgent = 0 if indexCurAgent + 1 == totalAgentNum else indexCurAgent + 1

    depth += 1 if succIndexCurAgent == 0 else 0

    if not indexCurAgent == 0:
      ghostsActions = currentState.getLegalActions(indexCurAgent)
      _value = 0
      for ghostAction in ghostsActions:
        _succState = currentState.generateSuccessor(indexCurAgent, ghostAction)
        _value += self.MinMaxValueHelper(_succState, succIndexCurAgent, totalAgentNum, depth, alpha, beta)[0]
      return (float(_value/len(ghostsActions)), ghostAction)
    else:
      pq = PriorityQueue()
      ghostsActions = currentState.getLegalActions(indexCurAgent)
      for ghostAction in ghostsActions:
        _succState = currentState.generateSuccessor(indexCurAgent, ghostAction)
        _value = self.MinMaxValueHelper(_succState, succIndexCurAgent, totalAgentNum, depth, alpha, beta)[0]
        pq.push((_value, ghostAction), -_value)
      return pq.pop()

  def checkGameState(self, currentState, depth):
    if depth >= self.depth:
      return True
    elif currentState.isWin() or currentState.isLose():
      return True
    else:
      return False


def betterEvaluationFunction(currentGameState):

  """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION:

    The value of evaluation function is given by the current score minus the evaluation
    value of current state(food, capsules, ghosts).

    Here we divide the game situation into two part, first one is when pacman
    eat the capsules, which means the pacman don't need to dodge the ghost, in this
    case we make sure the pacman will take eating ghost as first choice instead of
    eat food, and in the normal case, if there is no ghosts in scared state, pacman will
    evaluate the distance to the closest food, which make sure pacmon will go to the closest
    food in order to get high score.

    helper functions:

    (1) getPossibleSuccessors() : get the legal successor state for provided state

    (2) HeuristicDistanceHelper(): by using heuristic we make sure pacman will always go to
    the closest food. Also we use heuristic to calculate the cost from pos1 to pos2, by using this
     function, we can make sure the distance to a certain point is consistent.
  """
  "*** YOUR CODE HERE ***"
  import sys

  pacmanPos = currentGameState.getPacmanPosition()
  foodList = currentGameState.getFood().asList()
  capsuleList = currentGameState.getCapsules()
  itemList = foodList+capsuleList
  ghostsStates = currentGameState.getGhostStates()
  disableGhostIndexes = []
  idn = 0

  for ghost in ghostsStates:
    ghostPos = ghost.getPosition()
    if pacmanPos == (int(ghostPos[0]), int(ghostPos[1])):
      return -sys.maxint
    if ghost.scaredTimer > 0:
      disableGhostIndexes.append(idn)
    idn += 1

  minDistanceToDisabledGhost = sys.maxint
  for index in disableGhostIndexes:
    ghostPos = ghostsStates[index].getPosition()
    minDistanceToDisabledGhost = min(
      minDistanceToDisabledGhost,
      HeuristicDistanceHelper(pacmanPos, (int(ghostPos[0]), int(ghostPos[1])), currentGameState)
    )

  minDistanceToItem = sys.maxint
  for item in itemList:
    minDistanceToItem = min(
      minDistanceToItem,
      HeuristicDistanceHelper(pacmanPos, item, currentGameState)
    )

  if len(itemList) == 0:
    return sys.maxint
  elif len(disableGhostIndexes) == 0:
    return scoreEvaluationFunction(currentGameState) - minDistanceToItem
  else:
    return 2 * scoreEvaluationFunction(currentGameState) - minDistanceToDisabledGhost



def getPossibleSuccessors(currentPos, currentGameState):
  from game import Actions
  pacPos = currentPos
  walls = currentGameState.getWalls()
  possileSuccessors = []


  for dir, vec in Actions._directionsAsList:
    dx, dy = vec
    next_y = pacPos[1] + dy
    next_x = pacPos[0] + dx
    if not walls[next_x][next_y]: possileSuccessors.append(((next_x, next_y), 1))

  return possileSuccessors


def HeuristicDistanceHelper(pos1, pos2, currentGameState):
  from util import PriorityQueue
  explored = set(pos1)
  pq = PriorityQueue()
  pq.push((pos1, 0), 0)
  while True:
    node = pq.pop()
    pos = node[0]
    cost = node[1]
    if pos == pos2:
      return cost
    successors = getPossibleSuccessors(pos, currentGameState)
    for succ in successors:
      if succ[0] in explored:
        continue
      else:
        _cost = succ[1] + cost
        _pos = succ[0]
        _estCost = _cost + manhattanDistance(_pos, pos2)
        pq.push((_pos, _cost), _estCost)
        explored.add(_pos)


# Abbreviation
better = betterEvaluationFunction

class ContestAgent(MultiAgentSearchAgent):
  """
    Your agent for the mini-contest
  """

  def getAction(self, gameState):
    """
      Returns an action.  You can use any method you want and search to any depth you want.
      Just remember that the mini-contest is timed, so you have to trade off speed and computation.

      Ghosts don't behave randomly anymore, but they aren't perfect either -- they'll usually
      just make a beeline straight towards Pacman (or away from him if they're scared!)
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


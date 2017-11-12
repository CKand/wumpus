from utils import *
from logic import *
from agents import *
from agent import *
from state import *

class WumpusWorld(State): 

	def __init__(self, agent, worldState):
		self.agent = agent;
		self.worldState = worldState;


    # State is changed according to action
	def executeActions(self, action):
		self.worldState.execute_action(self.agent,action);

    # Checks whether current state and the one in parameter are  the same
    #dont think we need this 
	def equals(self, state):
		return False

    # Checks whether the state is a goal state
	def isGoal(self):
		return self.worldState.is_done();

    # Prints to the console a description of the state
    #shows roomContents
	def show(self):
		return self.worldState.get_world();

    # Returns a list of possible actions from the current state
	def possibleActions(self):
		return [];
	 # Returns a list of sensations from the current state
	def percept(self, agent): 
		return self.worldState.percept(self.agent);

	#get agents location
	def getCurrentLocation():
		return self.agent.location;

	#get agents direction
	def getCurrentDirection():
		return self.agent.direction;

#puzzle = WumpusEnvironment(None,4,4);
#program here needs to be be done, it should take in precepts and return an action.
#agent = Agent(program)
agentTest = KnowledgeBasedAgent()
#print(agentTest.choose_location(agentTest))

#WumpusWorld(puzzle.get_world, [1,1],0, puzzle.percepts_from(puzzle.agents[0],(1,1)));#should just be puzzle.precept(agent) if had a valid agent right nwo 
puzzle = WumpusWorld(agentTest, WumpusEnvironment(agentTest,4,4)); #where None should be agent

print(puzzle.worldState.get_world())
listper =puzzle.percept(agentTest)
agent = Agent(agentTest.program)
# print("here is the issue")
# print(puzzle.percept(agentTest))
#TraceAgent(agent);
#print(agent)



while not puzzle.worldState.is_done():
	puzzle.worldState.execute_action(agentTest, agentTest.program(puzzle.percept(agentTest)))

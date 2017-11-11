from utils import *
from logic import *
from agents import *
from state import *

# print(wumpus_kb.clauses)

#print("test");
#puzzle = WumpusEnvironment(None,4,4);
#print(puzzle.get_world());
#print("im so lost");
#print(puzzle.things);
class WumpusWorld(State): 

	def __init__(self, agent, worldState):
		self.agent = agent;
		self.worldState = worldState;
		print("send help");


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
		return self.worldState.precept(self.agent);

	#get agents location
	def getCurrentLocation():
		return self.agent.location;

	#get agents direction
	def getCurrentDirection():
		return self.agent.direction;


wumpus_kb = PropKB()
P11, P12, P21, P22, P31, B11, B21 = expr('P11, P12, P21, P22, P31, B11, B21')
wumpus_kb.tell(~P11)
wumpus_kb.tell(B11 | '<=>' | ((P12 | P21)))
wumpus_kb.tell(B21 | '<=>' | ((P11 | P22 | P31)))
wumpus_kb.tell(~B11)
wumpus_kb.tell(B21)
#puzzle = WumpusEnvironment(None,4,4);
#program here needs to be be done, it should take in precepts and return an action.
agent = Agent(program); 
#WumpusWorld(puzzle.get_world, [1,1],0, puzzle.percepts_from(puzzle.agents[0],(1,1)));#should just be puzzle.precept(agent) if had a valid agent right nwo 
WumpusWorld(agent, WumpusEnvironment(None,4,4)); #where None should be agent
print("uhh");
TraceAgent(agent);
print(agent)
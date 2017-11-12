# 
# resolution(KB, q): Given a propositional knowledge base and query, return
# whether the query can be inferred from the knowledgebase using resolution.
# The implementation is more efficient than pl_resolution in the AIMA code.

# KnowledgeBasedAgent: An abstract class that makes decisions to navigate
# through a world based on its knowledge.
#
# Compiled against Python 2.7
# Author: Stephen Bahr (sbahr@bu.edu)

import collections
import logic
from agents import *

RESULT_DEATH = 0
RESULT_GIVE_UP = 1
RESULT_WIN = 2

class GameOver(Exception):
	"""A class representing the event of the game ending."""
	def __init__(self, result):
		"""Result is one of the RESULT constants above."""
		self.result = result


# Utility functions
def normalize(clause):
	return frozenset(map(str, logic.disjuncts(clause)))

def negate(literal):
	if literal[0] == '~': return literal[1:]
	else: return '~' + literal


def resolution(KB, alpha):
	"""Apply the resolution algorithm to determine if alpha can be inferred from KB.
	Args:
	KB: an instance of logic.PropKB
	alpha: an instance of logic.Expr
	Return True if KB |- alpha"""
 # We do not want to waste effort resolving clauses of the KB against
 # one another directly, we only want to resolve clauses that contain
  # information derived from alpha.  tainted_clauses will be the set
  # we grow.
	tainted_clauses = set(normalize(clause)
	for clause in logic.conjuncts(logic.to_cnf(~alpha)))
	KB_clauses = [normalize(clause) for clause in KB.clauses]
	new = set()
	while True:
   # clausesWith is a map from literals to clauses containing that literal.
		clausesWith = collections.defaultdict(list)
		for clause in list(tainted_clauses) + KB_clauses:
			for literal in clause:
				clausesWith[literal].append(clause)
    # For each tainted clause, add a pair of that clause and any
    # tainted or KB clause that matches it (i.e. opposes on one literal).
		pairs = []
		for clause0 in tainted_clauses:
			for literal in clause0:
				for clause1 in clausesWith[negate(literal)]:
					pairs.append((literal, clause0, clause1))
    # Resolve all the pairs found above.  If any result in None, the 
    # resolution is a bust (provides no new information).
    # If any result in False (empty set), we have reached a contradiction
    # and proven our goal.
		for literal, clause0, clause1 in pairs:
			result = resolve(clause0, clause1, literal)
			if result is not None:
				if result == set(): return True
				else: new.add(frozenset(result))
    # We now survey all the new clauses.  In order to want to keep them,
    # they must not be a superset of any already-known clause (since that
    # would provide no new information).
		added = False
		for clause in new:
			if not any(old_clause.issubset(clause)
				for old_clause in list(tainted_clauses) + KB_clauses):
					tainted_clauses.add(clause)
					added = True
    # If we have not found any new information, we've reached the end
    # and cannot prove our goal (it may be True, it may be False, but we
    # can't definitively say either way).
		if not added: return False


def resolve(clause0, clause1, literal):
  """Resolve two clauses.
  Each input clause is represented as a sequence of strings, each string being
  one literal.  The two clauses must be resolvable, one containing literal,
  the other the negation of literal.
  Args:
    clause0: An arbitrary clause, containing literal.
    clause1: An arbitrary clause, containing the negation of literal.
    literal: A string.
  Returns:
    None if the two clauses also match on a different literal, because
        in that case, all the resolved clauses would be equivalent to True
    The empty set if the two clauses are exactly literal and not-literal,
        i.e. they resolve to False
    Otherwise, a frozenset of literals, the resolved clause.
  """
  clause0 = set(clause0)
  clause1 = set(clause1)
  clause0.remove(literal)
  clause1.remove(negate(literal))
  if any(negate(other) in clause1 for other in clause0): return None
  return clause0.union(clause1)


class KnowledgeBasedAgent:
	def __init__(self):
		self.KB = logic.PropKB()
		self.size = 4
		cave_size = 4
		self.location = (1,1)
		self.direction = Direction("up")
		self.holding = []
		self.performance = 0

		# example of propositional logic
		#self.KB.tell("B11 <=> (P12|P21)")
		#self.KB.tell("~B11")

		# background knowledge about the wumpus world
		# Every x on the board
		for x in range(1, cave_size + 1):
			#Every y on the board
			for y in range(1, cave_size + 1):

				#Breeze notBreeze Stench notStench
				B = "B" + str(x) + "_" + str(y) + " <=> ("
				notB = "~B" + str(x) + "_" + str(y) + " <=> ("
				S = "S" + str(x) + "_" + str(y) + " <=> ("
				notS = "~S" + str(x) + "_" + str(y) + " <=> ("

				#Lets get the nearby neighbors
				neighbors = self.get_neighbors(x, y, self.size)


				for n in neighbors:
					B += " P" + str(n[0]) + "_" + str(n[1]) + " |"

				for n in neighbors:
					notB += " ~P" + str(n[0]) + "_" + str(n[1]) + " &"

				for n in neighbors:
					S += " W" + str(n[0]) + "_" + str(n[1]) + " |"

				for n in neighbors:
					notS += " ~W" + str(n[0]) + "_" + str(n[1]) + " &"

				B = B[:-1] + ")"
				notB = notB[:-1] + ")"
				S = S[:-1] + ")"
				notS = notS[:-1] + ")"

				self.KB.tell(B)
				self.KB.tell(notB)
				self.KB.tell(S)
				self.KB.tell(notS)

	def safe(self):
		"""
		Use logic to determine the set of locations I can prove to be safe.
		"""

		safe_spots = set()
		for x in range(1, self.size + 1):
			for y in range(1, self.size + 1):
				#Current location
				loc = "" + str(x) + "_" + str(y)

				#Add current location spot to the safe_spots
				if resolution(self.KB, logic.expr("L" + loc)):
					safe_spots.add((x,y))

				#Not a pit or not a wumpus at current location
				if resolution(self.KB, logic.expr("~P" + loc)) and resolution(self.KB, logic.expr("~W" + loc)):
					safe_spots.add((x,y))

				# If no smell, and no breeze, then all neighbors are safe locations.
				no_smell = resolution(self.KB, logic.expr("~S" + loc))
				no_breeze = resolution(self.KB, logic.expr("~B" + loc))
				if (no_smell and no_breeze):
					for n in self.get_neighbors(x, y, self.size):
						#print "Adding " + str(n) + " to safe_spots"
						safe_spots.add(n)

		return safe_spots

	def not_unsafe(self):
		"""
		Use logic to determine the set of locations I can't prove to be unsafe
		"""
		not_unsafe_spots = set()
		for x in range(1, self.size + 1):
			for y in range(1, self.size + 1):

				#Current location
				loc = "" + str(x) + "_" + str(y)

				if not resolution(self.KB, logic.expr("L" + loc)):
					not_unsafe_spots.add((x,y))

				if resolution(self.KB, logic.expr("P" + loc)) or resolution(self.KB, logic.expr("W" + loc)):
					if not_unsafe_spots.__contains__((x,y)):
						not_unsafe_spots.remove((x,y))

				# If no smell, and no breeze, then all neighbors are safe locations.
				no_smell = resolution(self.KB, logic.expr("~S" + loc))
				no_breeze = resolution(self.KB, logic.expr("~B" + loc))
				if (no_smell and no_breeze):
					for n in self.get_neighbors(x, y, self.size):
						#print "Adding " + str(n) + " to not_unsafe_spots"
						not_unsafe_spots.add(n)

		return not_unsafe_spots

	def unvisited(self):
		"""
		Use logic to determine the set of locations I haven't visited yet.
		"""
		result = set()
		for x in range(1, self.size + 1):
			for y in range(1, self.size + 1):
				if not resolution(self.KB, logic.expr("L" + str(x) + "_" + str(y))):
					result.add((x,y))
		return result

	def get_neighbors(self, x, y, cave_size):
		NEIGHBOR_DELTAS = ((+1, 0), (-1, 0), (0, +1), (0, -1))
		"""
		Return a list of neighbors given the canvas size, and the current coordinates
		"""
		possible_neighbors = [(x + dx, y + dy) for dx, dy in NEIGHBOR_DELTAS]
		return [(x1, y1) for x1, y1 in possible_neighbors if 
			1 <= x1 <= cave_size and 1 <= y1 <= cave_size]


	def program(self,precept):
		self.perceive(precept)
		deltas = [(0,-1),(0,1),(-1,0),(1,0)]
		"""Return the next location to explore in the search for gold."""
		unvisited_locations = self.unvisited()
		safe_moves = self.safe().intersection(unvisited_locations)
		if safe_moves:
			location = min(safe_moves)
			print('Moving to safe location', location)
		else:
			not_unsafe_moves = self.not_unsafe().intersection(unvisited_locations)
			if not_unsafe_moves:
				location = min(not_unsafe_moves)
				print('Taking a risk; moving to a not-unsafe location', location)
			else:
				print('Nowhere left to go')
				raise GameOver(RESULT_GIVE_UP)
		x1,y1 = self.location
		x2,y2 = location
		delta = (x2-x1, y2-y1)
		if(deltas[0] == delta):
			action = "Left"
		elif(deltas[1] == delta):
			action = "Right"
		elif(deltas[2] == delta):
			action = "Up" 
		else:
			action = "Down"

		self.location = location

		return action

	def __call__(self):
		program(self)

	def perceive(self, precept):

		#left from explorer
		for perception in precept[0]: 
			if (str(perception) == "<Breeze>"):
				print('You feel a breeze to the left')					
				self.KB.tell('B%d_%d' % (self.location[0], self.location[1]-1))
			if (str(perception) == "<Stench>"):
				print('You smell something to the left')					
				self.KB.tell('S%d_%d' % (self.location[0], self.location[1]-1))
			if (str(perception) == "<Bump>"):
				print('You feel a wall to the left')					
				#self.KB.tell('S%d_%d' % (self.location[0], self.location[1]-1))

		#right from explorer
		for perception in precept[1]: 
			if (str(perception) == "<Breeze>"):
				print('You feel a breeze to the right')					
				self.KB.tell('B%d_%d' % (self.location[0], self.location[1]+1))
			if (str(perception) == "<Stench>"):
				print('You smell something to the right')					
				self.KB.tell('S%d_%d' % (self.location[0], self.location[1]+1))	
			if (str(perception) == "<Bump>"):
				print('You feel a wall to the right')					
				#self.KB.tell('S%d_%d' % (self.location[0], self.location[1]-1))			

		#up from explorer
		for perception in precept[2]: 
			if (str(perception) == "<Breeze>"):
				print('You feel a breeze from in front of you')					
				self.KB.tell('B%d_%d' % (self.location[0]-1, self.location[1]))
			if (str(perception) == "<Stench>"):
				print('You smell something from in front of you')					
				self.KB.tell('S%d_%d' % (self.location[0]-1, self.location[1]))	
			if (str(perception) == "<Bump>"):
				print('You feel a wall in front of you')					
				#self.KB.tell('S%d_%d' % (self.location[0], self.location[1]-1))

		#down from explorer
		for perception in precept[3]: 
			if (str(perception) == "<Breeze>"):
				print('You feel a breeze from behind you')					
				self.KB.tell('B%d_%d' % (self.location[0]+1, self.location[1]))
			if (str(perception) == "<Stench>"):
				print('You smell something from behind you')					
				self.KB.tell('S%d_%d' % (self.location[0]+1, self.location[1]))	
			if (str(perception) == "<Bump>"):
				print('You feel a wall from behind you')					
				#self.KB.tell('S%d_%d' % (self.location[0], self.location[1]-1))

		#current location of explorer
		for perception in precept[4]: 
			self.KB.tell('L%d_%d' % (self.location[0], self.location[1]))
			if (str(perception) == "<Breeze>"):
				print('You feel a breeze where you are')					
				self.KB.tell('B%d_%d' % (self.location[0], self.location[1]))
			if (str(perception) == "<Stench>"):
				print('You smell something where you are')					
				self.KB.tell('S%d_%d' % (self.location[0], self.location[1]))	
			if (str(perception) == "<Pit>"):
				print("You fell game over")
				#do soemthing to break
			else:
				self.KB.tell('~P%d_%d' % (self.location[0], self.location[1]))
			if (str(perception) == "<Wumpus>"):
				print("You are in wumpus room. dead.")
				return
				#do soemthing to break
			else:
				self.KB.tell('~W%d_%d' % (self.location[0], self.location[1]))
			if (str(perception) == "<Glitter>"):
				print("You found the gold! you win!")
				GameOver(2)
				return
				#do soemthing to break

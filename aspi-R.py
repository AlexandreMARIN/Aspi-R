from copy import *
#the grid
grid = None
#number of robots
nbRobots = None
#we have a 1-1 map to transform a letter into an integer
colorToIndex = None
indexToColor = None

solution = ""


#four robots at most!


def incrementPos(pos, dirct):
    """
    Given a position 'pos' and a direction 'dirct' in {N, S, W, E},
    we return the new matching position in the grid.
    """
    if dirct == "N":
        return (pos[0]-1, pos[1])
    if dirct == "W":
        return (pos[0], pos[1]-1)
    if dirct == "S":
        return (pos[0]+1, pos[1])
    #East
    return (pos[0], pos[1]+1)

def isThereAWall(ind_rob, pos_rob, dirct):#or a robot !
    """
    That function returns true iif a robot at pos_rob[ind_rob] cannot
    move one cell in the direction dirct because of an other robot or a wall.
    """
    other_pos = []
    curpos = pos_rob[ind_rob]
    for i in range(ind_rob):
        other_pos.append(pos_rob[i])
    for i in range(ind_rob+1, nbRobots):
        other_pos.append(pos_rob[i])
    
    if dirct == "N":
        if (grid[curpos[0]][curpos[1]]) & 1 == 1:
            return True
        else:
            for op in other_pos:
                if (curpos[0] == 1+op[0]) and (curpos[1] == op[1]):
                    return True
            return False
    if dirct == "E":
        if (grid[curpos[0]][curpos[1]] >> 1) & 1 == 1:
            return True
        else:
            for op in other_pos:
                if (curpos[0] == op[0]) and (curpos[1]+1 == op[1]):
                    return True
            return False
    if dirct == "S":
        if (grid[curpos[0]][curpos[1]] >> 2) & 1 == 1:
            return True
        else:
            for op in other_pos:
                if (curpos[0]+1 == op[0]) and (curpos[1] == op[1]):
                    return True
            return False
    #West
    if (grid[curpos[0]][curpos[1]] >> 3) & 1 == 1:
        return True
    else:
        for op in other_pos:
            if (curpos[0] == op[0]) and (curpos[1] == 1+op[1]):
                return True
    return False

def moveRobot(ind_rob, pos_rob, dirct):
    """
    That function returns the new position and the cells cleaned by the robot
    at the position 'pos', when it moves in the direction 'dirct'.
    """
    pos_rob[ind_rob] = incrementPos(pos_rob[ind_rob], dirct)
    cellsToRetrieve = [pos_rob[ind_rob]]
    while not(isThereAWall(ind_rob, pos_rob, dirct)):
        pos_rob[ind_rob] = incrementPos(pos_rob[ind_rob], dirct)
        cellsToRetrieve.append(pos_rob[ind_rob])

    return pos_rob[ind_rob], cellsToRetrieve

class NodeTree:
    """
    It represents a node of a tree.
    """

    def __init__(self, move, pos_rob, cellsToClean):
        """
        pos_rob: positions of the robots
        move: the move of the robot which leads to this node
        cellsToClean: cells which have not been cleaned yet before the move

        Given the move of a robot in the form of a string 'letter of a color'+'direction',
        we update pos_rob and cellsToClean.
        """
        global solution
        self.move = copy(move)
        self.sons = []
        self.pos_rob = deepcopy(pos_rob)
        self.cellsToClean = deepcopy(cellsToClean)
        
        #pos_rob
        if move!="":
            ind_rob = colorToIndex[move[0]]
            prev_pos=self.pos_rob[ind_rob]
            pos, cellsToRetrieve = moveRobot(ind_rob, self.pos_rob, move[1])#attention, changes!
            self.pos_rob[ind_rob] = pos
            #print("prevpos:", prev_pos, "move: ", move, "pos: ", pos)
            for cell in cellsToRetrieve:
                self.cellsToClean.discard(cell)
        if not(self.cellsToClean):
            print("last move: ", move, "last pos: ", pos_rob)
            solution = move


    def createSons(self):
        """
        It creates all the sons. Each son matches a new move and a new configuration.
        """
        global solution
        for ind_rob in range(nbRobots):
            for dirct in ["N", "W", "E", "S"]:
                move = indexToColor[ind_rob]+dirct
                if not(isThereAWall(ind_rob, self.pos_rob, dirct)):
                    self.sons.append(NodeTree(move, self.pos_rob, self.cellsToClean))
                    if solution:
                        solution = self.move+" "+solution
                        return#it is no use building more nodes...

    def newStage(self):
        """
        It increases the height of the tree by one, by building all the sons for each leaf.
        """
        global solution
        if not(self.sons):
            self.createSons()
            return
        for node in self.sons:
            node.newStage()
            if solution:
                solution = self.move+" "+solution
                return


class Aspi_R:
    """
    This class enables us to build the tree of all the possibilities (with a limit...)
    """

    def __init__(self, filename):
        """
        We read a file of name 'filename' which contains data we need.
        Then we prepare the grid, the root of the tree and some structures.
        """
        #
        global colorToIndex
        global indexToColor
        global nbRobots
        global grid
        file = open(filename, "r")
        line = file.readline()
        data = line.split(" ")
        nr = int(data[0])
        nc = int(data[1])
        nbRobots = int(data[2])
        grid = []
        self.cellsToClean = set()
        for i in range(nr):
            grid.append([])
            line = file.readline()
            for j in range(nc):
                self.cellsToClean.add((i, j))
                grid[-1].append(int(line[j], base=16))
                
        self.pos_rob = []
        colorToIndex = {}
        indexToColor = {}
        for i in range(nbRobots):
            line = file.readline()
            data = line.split(" ")
            colorToIndex[data[0]] = i
            indexToColor[i] = data[0]
            self.pos_rob.append((int(data[1]), int(data[2])))
            self.cellsToClean.remove(self.pos_rob[-1])
            
        file.close()
        self.root = NodeTree("", self.pos_rob, self.cellsToClean)

    def solve(self):
        """
        We find here the optimal sequence of moves.
        """
        global solution
        print(self.pos_rob)
        print(self.cellsToClean, "\n", nbRobots, "\n", grid)
        i = 0
        while not(solution):
            print(i)
            i = i+1
            self.root.newStage()
        print("solution:\n", solution)


#execution
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

problem = Aspi_R(args.file)
problem.solve()

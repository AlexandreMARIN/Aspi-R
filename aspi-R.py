from copy import *
#the grid
grid = None
#number of robots
nbRobots = None
#we have a 1-1 map to transform a letter into an integer
colorToIndex = None
indexToColor = None


seq_nodes = []
maxDepth = None


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
    global nbRobots
    curpos = pos_rob[ind_rob]
    
    if dirct == "N":
        if (grid[curpos[0]][curpos[1]]) & 1 == 1:
            return True, -1
        else:
            for ind in range(ind_rob):
                if (curpos[0] == 1+pos_rob[ind][0]) and (curpos[1] == pos_rob[ind][1]):
                    return True, ind
            for ind in range(ind_rob+1, nbRobots):
                if (curpos[0] == 1+pos_rob[ind][0]) and (curpos[1] == pos_rob[ind][1]):
                    return True, ind
            return False, -1
    if dirct == "E":
        if (grid[curpos[0]][curpos[1]] >> 1) & 1 == 1:
            return True, -1
        else:
            for ind in range(ind_rob):
                if (curpos[0] == pos_rob[ind][0]) and (curpos[1]+1 == pos_rob[ind][1]):
                    return True, ind
            for ind in range(ind_rob+1, nbRobots):
                if (curpos[0] == pos_rob[ind][0]) and (curpos[1]+1 == pos_rob[ind][1]):
                    return True, ind
            return False, -1
    if dirct == "S":
        if (grid[curpos[0]][curpos[1]] >> 2) & 1 == 1:
            return True, -1
        else:
            for ind in range(ind_rob):
                if (curpos[0]+1 == pos_rob[ind][0]) and (curpos[1] == pos_rob[ind][1]):
                    return True, ind
            for ind in range(ind_rob+1, nbRobots):
                if (curpos[0]+1 == pos_rob[ind][0]) and (curpos[1] == pos_rob[ind][1]):
                    return True, ind
            return False, -1
    #West
    if (grid[curpos[0]][curpos[1]] >> 3) & 1 == 1:
        return True, -1
    else:
        for ind in range(ind_rob):
            if (curpos[0] == pos_rob[ind][0]) and (curpos[1] == 1+pos_rob[ind][1]):
                return True, ind
        for ind in range(ind_rob+1, nbRobots):
            if (curpos[0] == pos_rob[ind][0]) and (curpos[1] == 1+pos_rob[ind][1]):
                return True, ind
    return False, -1

def moveRobot(rob, posRob, dirct):
    pos = [incrementPos(posRob[rob], dirct)]
    cannotMove, rob2 = isThereAWall(rob, posRob, dirct)
    while not(cannotMove):
        pos.append(incrementPos(pos[-1], dirct))
        cannotMove, rob2 = isThereAWall(rob, posRob, dirct)
    return pos, rob2

def getMoves(posRob):
    global nbRobots
    moves = {}
    for i in range(nbRobots):
        moves[i] = {}
        for dirct in ["N", "S", "W", "E"]:
            cannotMove, = isThereAWall(i, posRob, dirct)
            if not(cannotMove):
                (lastCleanedCells, rob) = moveRobot(i, posRob, dirct)
                move[i][dirct] = (lastCleanedCells, rob, set())
    return moves


class NodeTree:
    """
    It represents a node of a tree.
    """

    def __init__(self, movedRob, dirct, posRob, cellsToClean):
        """
        pos_rob: positions of the robots
        move: the move of the robot which leads to this node
        cellsToClean: cells which have not been cleaned yet before the move

        Given the move of a robot in the form of a string 'letter of a color'+'direction',
        we update pos_rob and cellsToClean.
        """
        global solution
        self.movedRob = movedRob
        self.dirct = dirct
        self.posRob = posRob
        self.cellsToClean = cellsToClean


    def createSons(self):
        """
        It creates all the sons. Each son matches a new move and a new configuration.
        """
        global solution
        movesSons = getMoves(self.posRob)

        for rob in range(nbRobots-1):
            for dirct in iter(movesSons[rob]):
                for dirct2 in iter(movesSons[rob+1]):
                    if (rob+1, dirct2) not in self.allowedMoves and movesSons[rob][dirct][1]!=rob+1 and movesSons[rob+1][dirct2][1]!=rob and movesSons[rob][dirct][0][-1] not in movesSons[rob+1][dirct2][0]  and movesSons[rob+1][dirct2][0][-1] not in movesSons[rob][dirct][0]:
                        movesSons[rob][dirct][2].add((rob+1, dirct2))
                        del movesSons[rob+1][dirct2]
                for rob2 in range(rob+2, nbRobots):
                    for dirct2 in iter(movesSons[rob2]):
                        if (rob2, dirct2) not in self.allowedMoves and movesSons[rob][dirct][1]!=rob2 and movesSons[rob2][dirct2][1]!=rob and movesSons[rob][dirct][0][-1] not in movesSons[rob2][dirct2][0]  and movesSons[rob2][dirct2][0][-1] not in movesSons[rob][dirct][0]:
                            del movesSons[rob2][dirct2]
        self.movesSons = movesSons

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
                
        self.posRob = {}
        colorToIndex = {}
        indexToColor = {}
        for i in range(nbRobots):
            line = file.readline()
            data = line.split(" ")
            colorToIndex[data[0]] = i
            indexToColor[i] = data[0]
            self.posRob[i] = (int(data[1]), int(data[2]))
            self.cellsToClean.remove(self.posRob[i])
            
        file.close()
        self.root = NodeTree(None, self.pos_rob, self.cellsToClean)#


    def solve(self):
        """
        We find here an optimal sequence of moves.
        """
        global solution
        i = 1
        while not(solution) and i<20:
            print(i)
            i = i+1
            self.root.createTree(i, [])
        print("solution:\n", solution)


#execution
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

problem = Aspi_R(args.file)
problem.solve()

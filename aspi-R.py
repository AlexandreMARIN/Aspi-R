from copy import *

#the grid
grid = None

#number of robots
nbRobots = None

#we have a 1-1 map to transform a letter into an integer
colorToIndex = None
indexToColor = None

#we need a sequence of nodes to represent a branch of the tree
seqNodes = []

#maximum depth for the search
maxDepth = None

#this variable will contain an optimal solution
solution = ""

#hypothesis:
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
    Input :
      ind_rob: index of the robot we want to move
      pos_rob: dict. containing positions of robots
      dirct : direction in {"N", "S", "W", "E"}
    That function returns true iif a robot at pos_rob[ind_rob] cannot
    move one cell in the direction dirct because of an other robot or a wall.
    If another robot is a hindrance, we return also its index.
    Thus we always return a pair (b, ind),
    where b is a Boolean value and ind is either -1 or an index of a robot if that robot is a hindrance.
    When ind=-1, a wall makes the current robot stop moving.
    """
    curpos = pos_rob[ind_rob]#current position
    
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
    """
    Input:
      rob : index of the robot we want to move
      posRob : dict. containing positions of all the robots
      dirct : a direction (as above)

    That function moves the robot 'rob' and returns
    a pair (p, r), where p is the new position of 'rob'
    and r is either -1 or the index of an other robot which acts as a wall.
    """
    pos = [incrementPos(posRob[rob], dirct)]
    prevPos = posRob[rob]
    posRob[rob] = pos[-1]
    cannotMove, rob2 = isThereAWall(rob, posRob, dirct)
    while not(cannotMove):
        pos.append(incrementPos(pos[-1], dirct))
        posRob[rob] = pos[-1]
        cannotMove, rob2 = isThereAWall(rob, posRob, dirct)
    posRob[rob] = prevPos
    return pos, rob2


def getMoves(posRob):
    """
    Input : posRob is a dict. containing positions of robots.
    Here we prepare and return a dict. associating each index of a robot with
    another dict., which itself associates a direction dirct with a 4-tuple
    of the form:
      (last cleaned cells, robot met during move (or -1), empty set, empty set).

    The entry dirct is valid for moves[rob] iif rob is allowed to move in the direction dirct.
    """
    moves = {}
    for i in range(nbRobots):
        moves[i] = {}
        for dirct in ["N", "S", "W", "E"]:
            cannotMove, rob = isThereAWall(i, posRob, dirct)
            if not(cannotMove):
                (lastCleanedCells, rob) = moveRobot(i, posRob, dirct)
                moves[i][dirct] = [lastCleanedCells, rob, set()]
    return moves


def buildTree(depth):
    """
    That function builds the tree containing all the possibilities
    'depth' is the current depth in the tree we explore.
    That function does not go beyond maxDepth and the first call must have the parameter 0.
    """
    global maxDepth
    global seqNodes

    if len(seqNodes[depth].cellsToClean) == 0:
        #we have just found a solution, not necessarily optimal
        maxDepth = depth - 1
        getSolution(depth)
        return

    if depth >= maxDepth:
        #we have gone too far !
        return
    #we create all the possible moves
    cN = seqNodes[depth]#current Node
    cN.createSons()
    sons = []
    for rob in iter(cN.movesSons):
        for dirct in iter(cN.movesSons[rob]):
            #we update information for that son of the current node
            posRob = deepcopy(cN.posRob)
            posRob[rob] = cN.movesSons[rob][dirct][0][-1]
            cellsToClean = deepcopy(cN.cellsToClean)
            for cell in cN.movesSons[rob][dirct][0]:#we discard cleaned cells because of the move of rob
                cellsToClean.discard(cell)
            sons.append(NodeTree(rob, dirct, posRob, cellsToClean, cN.movesSons[rob][dirct][2]))



    for mov in sorted(sons, key=lambda mov: ( (len(cN.cellsToClean) - len(mov.cellsToClean)) / (abs(cN.posRob[mov.movedRob][1]-mov.posRob[mov.movedRob][1])+abs(cN.posRob[mov.movedRob][0]-mov.posRob[mov.movedRob][0])) ), reverse=True):
        seqNodes[depth+1] = mov
        if isUseless(depth+1):
            continue
        buildTree(depth+1)
        if depth >= maxDepth:
            return


def isUseless(depth):
    """
    returns True iif the (depth+1)-th node in seqNodes if useless,
    i.e. a robot returns its initial place without cleaning cells.
    """
    nbcc = len(seqNodes[depth].cellsToClean)
    curpos = seqNodes[depth].posRob[seqNodes[depth].movedRob]
    for d in reversed(range(1, depth)):
        node = seqNodes[d]
        if len(node.cellsToClean) == nbcc:
            if node.posRob[node.movedRob] == curpos:
                return True
        else:
            return False
    return False

def getSolution(depth):
    """
    It builds a solution by retrieving information of 'seqNodes'
    in cells having an index in [1, depth].
    """
    global solution
    solution = ""
    for d in range(1, depth+1):
        solution = solution + " " + indexToColor[seqNodes[d].movedRob] + seqNodes[d].dirct


class NodeTree:
    """
    It represents a node of a tree.
    """

    def __init__(self, movedRob, dirct, posRob, cellsToClean, forbiddenMoves):
        """
        movedRob : the robot we move
        dirct : the direction of the move
        posRob: positions of robots
        cellsToClean: cells which have not been cleaned yet before the move
        forbiddenMoves: forbidden moves
        Those last two parameters are used in the next function.
        """
        self.movedRob = movedRob
        self.dirct = dirct
        self.posRob = posRob
        self.cellsToClean = cellsToClean
        self.forbiddenMoves = forbiddenMoves


    def createSons(self):
        """
        It creates all the moves associated with a son of the instance.
        """

        movesSons = getMoves(self.posRob)

        for mov in self.forbiddenMoves:#we discard forbidden moves
            movesSons[mov[0]].pop(mov[1], None)

        for rob in set(movesSons.keys())-{nbRobots-1}:#we rebuild all the possibilities given by movesSons()
            for dirct in list(iter(movesSons[rob])):
                for rob2 in set(movesSons.keys())-set(range(rob+1)):
                    for dirct2 in list(iter(movesSons[rob2])):
                        if movesSons[rob][dirct][1]!=rob2 and movesSons[rob2][dirct2][1]!=rob and movesSons[rob][dirct][0][-1] not in movesSons[rob2][dirct2][0] and movesSons[rob2][dirct2][0][-1] not in movesSons[rob][dirct][0]:
                            movesSons[rob2][dirct2][2].add((rob, dirct))


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
        self.root = NodeTree(None, None, self.posRob, self.cellsToClean, set())


    def solve(self):
        """
        We find here an optimal sequence of moves.
        """
        global maxDepth
        global seqNodes
        global solution
        maxDepth = 16
        seqNodes = [self.root] + [None]*(maxDepth)
        while not(solution):
            print("maxDepth:", maxDepth)
            buildTree(0)
            maxDepth = maxDepth+4
            seqNodes = seqNodes + [None]*4
        print("solution:\n", solution)


#execution
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("file") #don't forget the file !
args = parser.parse_args()

problem = Aspi_R(args.file)
problem.solve()

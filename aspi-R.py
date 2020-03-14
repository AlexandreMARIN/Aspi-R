from copy import *
#the grid
grid = None
#number of robots
nbRobots = None
#we have a 1-1 map to transform a letter into an integer
colorToIndex = None
indexToColor = None


seqNodes = []
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
    global nbRobots
    moves = {}
    for i in range(nbRobots):
        moves[i] = {}
        for dirct in ["N", "S", "W", "E"]:
            cannotMove, rob = isThereAWall(i, posRob, dirct)
            if not(cannotMove):
                (lastCleanedCells, rob) = moveRobot(i, posRob, dirct)
                moves[i][dirct] = [lastCleanedCells, rob, set(), set()]
    return moves

def buildTree(depth):
    global maxDepth
    global seqNodes

    if len(seqNodes[depth].cellsToClean) == 0:
        maxDepth = depth - 1
        getSolution(depth)
        #print("move:", seqNodes[depth].dirct, depth)
        return
    if depth >= maxDepth:
        return
    seqNodes[depth].createSons()
    for rob in iter(seqNodes[depth].movesSons):
        for dirct in iter(seqNodes[depth].movesSons[rob]):
            posRob = deepcopy(seqNodes[depth].posRob)
            posRob[rob] = seqNodes[depth].movesSons[rob][dirct][0][-1]
            cellsToClean = deepcopy(seqNodes[depth].cellsToClean)
            for cell in seqNodes[depth].movesSons[rob][dirct][0]:
                cellsToClean.discard(cell)
            #print("posRob: ", posRob)
            seqNodes[depth+1] = NodeTree(rob, dirct, posRob, cellsToClean, seqNodes[depth].movesSons[rob][dirct][2], seqNodes[depth].movesSons[rob][dirct][3])
            if isUseless(depth+1):
                continue
            buildTree(depth+1)
            if depth >= maxDepth:
                return

def isUseless(depth):
    nbcc = len(seqNodes[depth].cellsToClean)
    curpos = seqNodes[depth].posRob[seqNodes[depth].movedRob]
    for d in reversed(range(1, depth)):
        node = seqNodes[d]
        if len(node.cellsToClean) == nbcc:
            if node.posRob[node.movedRob] == curpos:
                #print("useless")
                return True
        else:
            return False
    return False

def getSolution(depth):
    global solution
    solution = ""
    for d in range(1, depth+1):
        solution = solution + " " + indexToColor[seqNodes[d].movedRob] + seqNodes[d].dirct

class NodeTree:
    """
    It represents a node of a tree.
    """

    def __init__(self, movedRob, dirct, posRob, cellsToClean, forbiddenMoves, allowedMoves):
        """
        pos_rob: positions of the robots
        move: the move of the robot which leads to this node
        cellsToClean: cells which have not been cleaned yet before the move

        Given the move of a robot in the form of a string 'letter of a color'+'direction',
        we update pos_rob and cellsToClean.
        """
        self.movedRob = movedRob
        self.dirct = dirct
        self.posRob = posRob
        self.cellsToClean = cellsToClean
        self.forbiddenMoves = forbiddenMoves
        self.allowedMoves = allowedMoves

    def createSons(self):
        """
        It creates all the sons. Each son matches a new move and a new configuration.
        """

        movesSons = getMoves(self.posRob)

        indepPairs = {}
        depMoves = set()
        #print(self.forbiddenMoves)
        for mov in self.forbiddenMoves:
            movesSons[mov[0]].pop(mov[1], None)

        for rob in set(movesSons.keys())-{nbRobots-1}:
            for dirct in list(iter(movesSons[rob])):
                for rob2 in set(movesSons.keys())-set(range(rob+1)):
                    for dirct2 in list(iter(movesSons[rob2])):
                        if movesSons[rob][dirct][1]!=rob2 and movesSons[rob2][dirct2][1]!=rob and movesSons[rob][dirct][0][-1] not in movesSons[rob2][dirct2][0] and movesSons[rob2][dirct2][0][-1] not in movesSons[rob][dirct][0]:
                            if (rob2, dirct2) in indepPairs:
                                indepPairs[(rob2, dirct2)].append((rob, dirct))
                            else:
                                indepPairs[(rob2, dirct2)] = [(rob, dirct)]
                        else:
                            depMoves.add((rob2, dirct2))
        #print("dM: ", depMoves)
        #print('iP: ', indepPairs)
        for (rob, dirct) in indepPairs.keys():
            for mov in indepPairs[(rob, dirct)]:
                if mov[1] in movesSons[mov[0]]:
                    movesSons[mov[0]][mov[1]][3].add((rob, dirct))
            if (rob, dirct) in depMoves:
                for mov in indepPairs.get((rob, dirct), []):
                    movesSons[rob][dirct][2].add(mov)
            else:
                if (rob, dirct) not in self.allowedMoves:
                    movesSons[rob].pop(dirct, None)

        #print("mS ", movesSons)
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
        self.root = NodeTree(None, None, self.posRob, self.cellsToClean, set(), set())


    def solve(self):
        """
        We find here an optimal sequence of moves.
        """
        global maxDepth
        global seqNodes
        global solution
        maxDepth = 14
        seqNodes = [self.root]
        seqNodes = seqNodes + [None]*(maxDepth)
        while not(solution)and maxDepth<24:
            print("maxDepth:", maxDepth)
            buildTree(0)
            maxDepth = maxDepth+4
            seqNodes = seqNodes + [None]*4
        print("solution:\n", solution)


#execution
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

problem = Aspi_R(args.file)
problem.solve()

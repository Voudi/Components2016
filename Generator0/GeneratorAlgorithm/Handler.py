import math
from Message import *
from SudokuGenerator import *
from Bridge import *

## Note
## Zur Zeit akzeptieren wir nur Sudokus die mindestes 9 * 9 Felder besitzen.
## Kleiner macht aus vielerlei Gründen keinen Sinn, hier ist uns aber nur wichtig,
## dass wir zu beginn eine fixe Zahl an Werten aus dem Sudoku löschen können.

class Handler():
    global senderAddress
    global bridge
    global reqDictionary

    senderAddress = ""

    """
        reqID:  Current request ID
        difficulty: difficultiy of sudoku
        finishedState: fully filled sudoku without empty fields
        cleanedNumbers: all index numbers of empty fields (in order)
        memorySet: all index numbers of empty fields
        firstID: id of the generate instruction (from gui)
    """
    reqDictionary={
        #'reqID123': (difficulty, finishedState, cleanedNumbers, memorySet, firstID)
    }

    def __init__(self, senderAddress):
        senderAddress = senderAddress
        bridge = Bridge()

    def getDictionary():
        return reqDictionary

    def handle(self, msg):
        # instruction: generate
        if(msg.instruction.startswith("generate")):
            print("case:generate")
            k = int(math.sqrt(len(msg.sudoku)))
            difficulty = msg.instruction[-2:-1]
            sudoku = generateFilledSudoku(k)

            # initial cleanup (remove 8 numbers)
            sudoku, cleanedNumbers = emptyField(sudoku,8)
            rID = Message.createGUID()
            reqDictionary[rID] = (difficulty, sudoku, cleanedNumbers, {}, msg.requestID)

            # send message to camel
            # TODO sender Address
            msgToSend = Message(requestID=rID, senderAddress=senderAddress, instruction="solve", sudoku=sudoku)
            #bridge.send(msgToSend)
            print(formattedString(sudoku))

        # instruction: solved one
        elif(msg.instruction == "solved:one"):
            print("case:solved:one")
            k = int(math.sqrt(len(msg.sudoku)))
            tmpDifficulty = reqDictionary[msg.requestID][0]

            # get number of 'empty' fields
            emptyCounter = 0
            for row in msg.sudoku:
                for elem in row:
                    if elem == 0:
                        emptyCounter = emptyCounter + 1

            percentCounter = (emptyCounter * 100) / (k*k)

            # check if we are done or if need still need to 'empty' fields (difficulty)
            if (tmpDifficulty == "1" and percentCounter < 0.7) or (tmpDifficulty == "2" and percentCounter < 0.5) \
               or (tmpDifficulty == "3" and percentCounter < 0.3):
                print("finished -> send to GUI")(requestID=Message.createGUID(), senderAddress=senderAddress, instruction="generate:[difficulty:1]", sudoku=sudoku)
                # if achieved -> sudoku finished for GUI -> send camel-msg
                msgToSend = Message(requestID=reqDictionary[msg.requestID][4], senderAddress=senderAddress, instruction="display", sudoku=sudoku)
                #bridge.send(msgToSend)
                del reqDictionary[msg.requestID]
                return

            # remove numbers
            sudoku, cleanedNumbers = emptyField(sudoku,1)
            (difficulty, finishedSudoku, oldNumbers, memorySet, firstID) = reqDictionary[msg.requestID]
            del reqDictionary[msg.requestID]
            cleanedNumbers = oldNumbers.extend(cleanedNumbers)
            rID = Message.createGUID()
            reqDictionary[rID] = (difficutly, finishedSudoku, cleanedNumbers, memorySet, firstID)

            # send camel-msg to broker (request to solve)
            msgToSend = Message(requestID=rID, senderAddress=senderAddress, instruction="solve", sudoku=sudoku)
            bridge.send(msgToSend)

        # instruction: solved many
        elif(msg.instruction == "solved: many"):
            print("case:solved:many")
            # recover previous state
            lastNumber = reqDictionary[msg.requestID][2].pop()
            (difficulty, finishedSudoku, oldNumbers, memorySet, firstID) = reqDictionary[msg.requestID]
            del reqDictionary[msg.requestID]
            sudoku = msg.sudoku
            sudoku[lastNumber[0]][lastNumber[1]] = finishedSudoku[lastNumber[0]][lastNumber[1]]

            # Check whether the number has already been removed
            if (len(memorySet) == len(sudoku)):
                lastNumber = reqDictionary[msg.requestID][2].pop()
                sudoku[lastNumber[0]][lastNumber[1]] = finishedSudoku[lastNumber[0]][lastNumber[1]]
                memorySet = {}

            # remove numbers and check if already removed
            sudoku, cleanedNumbers = emptyField(sudoku,1)
            memorySet = memorySet.add(cleanedNumbers)
            cleanedNumbers = oldNumbers.extend(cleanedNumbers)
            rID = Message.createGUID()
            reqDictionary[rID] = (difficutly, finishedSudoku, cleanedNumbers, memorySet, firstID)

            # send camel-msg to broker (request to solver)
            msgToSend = Message(requestID=rID, senderAddress=senderAddress, instruction="solve", sudoku=sudoku)
            #bridge.send(msgToSend)
        else:
            print("Some error occured!")

    if __name__ == "__main__":

        #Dump-Message
        requestID   = "12345"
        sender      = "sender"
        instruction = "generate[difficulty:1]"
        sudoku      = [[0]*9]*9
        message = Message(requestID,sender,instruction,sudoku)

        handle(message)

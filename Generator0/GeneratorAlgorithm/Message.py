import uuid
from flask import jsonify

class Message():

	def __init__ (self, requestID="-1", senderAddress="", instruction="solve", sudoku="[[]]"):
		self.requestID   = requestID
		self.sender      = "rest:post:/message?host=" + senderAddress + ":80/api"
		self.instruction = instruction
		self.sudoku      = sudoku

	def json (self):
		message = {
				'request-id': self.requestID,
				'sender': self.sender,
				'instruction': self.instruction,
				'sudoku': self.sudoku,
				}
		return jsonify({'message': message})

	def createGUID():
		return uuid.uuid1()

class Player:
    def __init__(self,name):
        self.name = name
        self.id = None

    def getName(self):
        return self.name

    def getID(self):
        return self.id

    def setName(self,name):
        self.name = name

    def setId(self, ID):
    	self.id = ID

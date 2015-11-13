class Player:
    def __init__(self,name):
        self.name = name
        self.seed = None
        self.id = None
        self.cid = None;

    def getCID(self):
        return self.cid

    def setCID(self,cid):
        self.cid = cid

    def getName(self):
        return self.name

    def getSeed(self):
        return self.seed

    def getID(self):
        return self.id

    def setName(self,name):
        self.name = name

    def setSeed(self,seed):
        self.seed = seed
    
    def setId(self, ID):
    	self.id = ID
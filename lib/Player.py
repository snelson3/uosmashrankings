class Player:
    def __init__(self,name):
        self.name = name
        self.id = None
        self.place = None

    def setPlace(self,pl):
        print(self.name + " get's place " + str(pl))
        self.place = pl

    def getName(self):
        return self.name

    def getID(self):
        return self.id

    def setName(self,name):
        self.name = name

    def setId(self, ID):
    	self.id = ID

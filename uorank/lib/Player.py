class Player:
    ''' Player object stores the ID/placing data for a player in the event '''
    def __init__(self,name):
        if name == None:
            raise Exception("Player must have a name")
        self.name = name
        self.id = None
        self.place = None

    def setPlace(self,pl):
        self.place = pl

    def getName(self):
        return self.name

    def getID(self):
        return self.id

    def setName(self,name):
        self.name = name

    def setId(self, ID):
        self.id = ID

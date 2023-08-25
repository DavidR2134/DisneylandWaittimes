class Ride:
    def __init__(self, name, isOpen, waitTime, lastUpdated, landID):
        self.name = name
        self.isOpen = isOpen
        self.waitTime = waitTime
        self.lastUpdated = lastUpdated
        self.landID = landID

    def __str__(self):
        return f"'{self.name}',{self.isOpen}, {self.waitTime}, '{self.lastUpdated}', {self.landID}"
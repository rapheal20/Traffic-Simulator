from Active_Lists.ActiveList import ActiveRoadsList, ActiveNodesDict, ActiveNodesSet

class roads():
    def __init__(self, roadID, coordinates, roadLength, lanes, oneway, speedLimit, unitVec, normal, startNode, endNode):
        self.road_id = roadID
        self.coordinates = coordinates #list of tuple
        self.lenght = roadLength #real
        self.lanes = max(1, round(lanes)) #integer
        self.speed_limit = speedLimit #integer
        self.oneway = oneway #Boolean
        self.UnitVector = unitVec
        self.NormalVector = normal
        self.StartNode = startNode
        self.EndNode = endNode
        self.cars_data = [[] for _ in range(self.lanes)]

        ActiveRoadsList[self.road_id] = self

    
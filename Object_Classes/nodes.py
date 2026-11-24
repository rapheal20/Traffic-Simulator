from Active_Lists.ActiveList import ActiveNodes

class nodes():


    def __init__(self, ID, coordinates, roads, type, connections, maxLanes, mainRoad ):
        self.NodeID = ID
        self.Coordinates = coordinates
        self.RoadNo = roads #number of roads it connects
        self.Type = type
        self.Connections = connections #list of road ids it connects
        self.MaxLanes = maxLanes
        self.MainRoad = mainRoad

        ActiveNodes[self.NodeID] = self

        
       
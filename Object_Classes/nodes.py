from Object_Classes.roads import roads
# from roads import roads
from Active_Lists.ActiveList import ActiveNodesDict
import heapq

class nodes():


    def __init__(self, ID, coordinates, roads, type, connections, maxLanes, mainRoad ):
        self.NodeID = ID
        self.Coordinates = coordinates
        self.RoadNo = roads #number of roads it connects
        self.Type = type
        self.Connections = connections #list of road ids it connects
        self.MaxLanes = maxLanes
        self.MainRoad = mainRoad





       
        ActiveNodesDict[self.NodeID] = self

        
       







        

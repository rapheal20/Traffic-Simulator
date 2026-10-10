from Object_Classes.roads import roads
# from roads import roads
import heapq

class nodes():


    def __init__(self, map_position, intType, roads, connections):
        self.postion = map_position
        self.intersection_type = intType
        # 0 = 1 road merging into another
        # 1 = roundabout
        # self.connecting_roads = roads #dicionary
        # #{'North' : "AA01", 'South': "BB12", 'East': "EE89", 'West' : 'BC76'}
        # #dictionary format is direction : Road id
        # self.road_connections = connections
        # # {
        # #     "AA01": "N02", this tells that if a car choses to go on th eroad AA01 then it will reach N02
        # #     "AA02": "N03",
        # #     "BB01": "N04",
        # #     "BB02": "N05"
        # # }

        self.roadsConnected = roads #List
        #this tells which roads are connected to each other using this node
        # ['AA01', 'BB01']





        

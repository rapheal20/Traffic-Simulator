from Object_Classes.roads import roads
from Object_Classes.car import car
from Object_Classes.nodes import nodes

from Active_Lists.ActiveCars import ActiveCarsNow
from Active_Lists.ActiveRoads import ActiveRoadsList
from Active_Lists.ActiveNodes import ActiveNodesSet, ActiveNodesDict




# # Road IDs, (x, y), length, lanes, orientation
# # Horizontal roads: length = 60 m, width = 3 lanes
road1 = roads("AA01", (0, 0), 100, 3, 0, 60, "East", [0, 250, 500], None, {'N01':25, "N02":100})
road2 = roads("AA02", (0, 71.6), 100, 3, 0, 60, "East", [0, 250, 500], None, {'N03':25, "N04":50, "N05":100})
road3 = roads("AA03", (0, 143.2), 100, 3, 0, 60, "East", [0, 250, 500], None, {'N06':50, "N07":100})

# # Vertical roads: length = 60 m, width = 2 lanes
road4 = roads("BB01", (25, 11.6), 60, 2, 1, 60, "South", [0, 250, 500], None, {'N02':0, "N03":60})
road5 = roads("BB02", (50, 83.2), 60, 2, 1, 60, "South", [0, 250, 500], None, {'N04':0, "N07":60})
road6 = roads("BB03", (100, 0), 154.8, 3, 1, 60, "South", [0, 250, 500], None, {'N02':0, "N05":71.6, "N07":143.2})


# # node1 = nodes("N01", )

# # (ActiveNodesSet)
# # print(ActiveNodesSet)


# # for roadObj in (ActiveRoadsList.values()):
# #     roadID = roadObj.road_id
# #     nodes_in_road = list(roadObj.nodes.keys())

# #     sorted_nodes = sorted(roadObj.nodes, key=roadObj.nodes.get)
# #     # iterates through the dictionary of nodes and arranges them in ascending order

# #     # print(sorted_nodes)
# #     for i in range(len(sorted_nodes)):
# #         currentNode = sorted_nodes[i]

# #         if currentNode not in ActiveNodesDict:
# #             ActiveNodesDict[currentNode] = {}
# #         # makes the main dictionary object for the node

# #         if roadObj.direction == "East" or roadObj.direction == "South":
# #             if i + 1 < len(sorted_nodes):
# #                 nextNode = sorted_nodes[i+1]
# #                 ActiveNodesDict[currentNode][nextNode] = roadID



# #         elif roadObj.direction == "West" or roadObj.direction == "North":
# #             if i - 1 >= 0:
# #                 prevNode = sorted_nodes[i+1]
# #                 ActiveNodesDict[currentNode][prevNode] = roadID


# # print(ActiveNodesDict)

# # for roadObj1 in (ActiveRoadsList.values()):
# #     road1ID = roadObj1.road_id
# #     for roadObj2 in (ActiveRoadsList.values()):
# #         road2ID = roadObj2.road_id
# #         if road1ID != road2ID:
# #             # road1Nodes = list((roadObj1.nodes).keys())
# #             # road2Nodes = list((roadObj2.nodes).keys())

# #             # sorted_nodes = sorted(roadObj.nodes, key=roadObj.nodes.get)
# #             road1Nodes = sorted(roadObj1.nodes, key=roadObj1.nodes.get)
# #             road2Nodes = sorted(roadObj2.nodes, key=roadObj2.nodes.get)
# #             # print(road1Nodes, road2Nodes)
# #             for node1 in road1Nodes:
# #                 if node1 in road2Nodes:
# #                     print(node1, road1ID, road2ID)

















# # for roadObj in (ActiveRoadsList.values()): #iterates through all the roads
# #     ActiveNodes = list((roadObj.nodes).keys())
# #     for roadNode in ActiveNodes: #takes one road and iterates through its nodes
        
#         # for KeyNode in ActiveNodesSet: #iterates through all nodes on the map
#         #     ActiveNodesDict.setdefault(KeyNode, {})

# #             if KeyNode != roadNode:
# #                 for otherRoadObj in (ActiveRoadsList.values()): #iterates through all the roads
# #                     if otherRoadObj.road_id != roadObj.road_id: #if the 2 roads are different
# #                         otherActiveNodes = list((otherRoadObj.nodes).keys()) 
# #                         for otherRoadNode in otherActiveNodes: #takes the other road and iterates through its nodes
# #                             if otherRoadNode == roadNode:
# #                                 ActiveNodesDict[KeyNode][roadNode] = roadObj.road_id



# # print(ActiveNodesDict)



# # # ROAD AA01 — 3 lanes
# # ROAD AA01 — 100 m, 3 lanes
# car("A01", "AA01", 5, 0, 8, 0)
# car("A02", "AA01", 12, 0, 6, 0)
# car("A03", "AA01", 25, 0, 10, 0)
# car("A04", "AA01", 38, 1, 12, 0)
# car("A05", "AA01", 45, 1, 7, 0)
# car("A06", "AA01", 58, 1, 9, 0)
# car("A07", "AA01", 70, 2, 15, 0)
# car("A08", "AA01", 78, 2, 5, 0)
# car("A09", "AA01", 90, 2, 11, 0)

# # ROAD AA02 — 100 m, 3 lanes
# car("A10", "AA02", 4, 0, 7, 0)
# car("A11", "AA02", 14, 0, 9, 0)
# car("A12", "AA02", 27, 0, 13, 0)
# car("A13", "AA02", 8, 1, 6, 0)
# car("A14", "AA02", 21, 1, 10, 0)
# car("A15", "AA02", 35, 1, 8, 0)
# car("A16", "AA02", 50, 1, 12, 0)
# car("A17", "AA02", 16, 2, 5, 0)
# car("A18", "AA02", 33, 2, 9, 0)

# # ROAD AA03 — 100 m, 3 lanes
# car("A19", "AA03", 6, 0, 10, 0)
# car("A20", "AA03", 18, 0, 7, 0)
# car("A21", "AA03", 31, 0, 11, 0)
# car("A22", "AA03", 44, 1, 6, 0)
# car("A23", "AA03", 57, 1, 9, 0)
# car("A24", "AA03", 71, 1, 13, 0)
# car("A25", "AA03", 15, 2, 8, 0)
# car("A26", "AA03", 29, 2, 5, 0)
# car("A27", "AA03", 46, 2, 10, 0)

# # ROAD BB01 — 60 m, 2 lanes
# car("B01", "BB01", 3, 0, 6, 0)
# car("B02", "BB01", 11, 0, 8, 0)
# car("B03", "BB01", 21, 0, 5, 0)
# car("B04", "BB01", 34, 0, 9, 0)
# car("B05", "BB01", 7, 1, 12, 0)
# car("B06", "BB01", 19, 1, 7, 0)
# car("B07", "BB01", 32, 1, 10, 0)
# car("B08", "BB01", 46, 1, 6, 0)

# # ROAD BB02 — 60 m, 2 lanes
# car("B09", "BB02", 4, 0, 8, 0)
# car("B10", "BB02", 13, 0, 5, 0)
# car("B11", "BB02", 25, 0, 11, 0)
# car("B12", "BB02", 39, 0, 7, 0)
# car("B13", "BB02", 8, 1, 6, 0)
# car("B14", "BB02", 22, 1, 9, 0)
# car("B15", "BB02", 36, 1, 5, 0)
# car("B16", "BB02", 49, 1, 12, 0)

# # ROAD BB03 — 154.8 m, 3 lanes
# car("B17", "BB03", 5, 0, 7, 0)
# car("B18", "BB03", 18, 0, 10, 0)
# car("B19", "BB03", 34, 0, 6, 0)
# car("B20", "BB03", 51, 1, 8, 0)
# car("B21", "BB03", 68, 1, 5, 0)
# car("B22", "BB03", 85, 1, 11, 0)
# car("B23", "BB03", 103, 2, 7, 0)
# car("B24", "BB03", 121, 2, 9, 0)
# car("B25", "BB03", 140, 2, 6, 0)




# #nodes
# road1 = roads("AA01", (100, 0), 100, 2, 1, 60, True, [0, 250, 500], None)  # North
# road2 = roads("AA02", (100, 200), 100, 2, 1, 60, True, [0, 250, 500], None)  # South
# road3 = roads("AA03", (0, 100), 100, 2, 0, 60, True, [0, 250, 500], None)  # West
# road4 = roads("AA04", (200, 100), 100, 2, 0, 60, True, [0, 250, 500], None)  # East

# from Object_Classes.nodes import road1,road2



# road1 = roads(
#                 roadID= 'AA01',
#                 cordinates= (0,25),
#                 roadLength = 60,
#                 lanes = 2,
#                 orientation=0,
#                 speedLimit = 60,
#                 oneWay = True,
#                 locationsAvailable = [{ "X" :0}],
#                 trafficLight = 60,
#                 nodes= {
#                     "N01": 0,
#                     "N02" : 25,
#                     "N03" : 52.4
#                     }
#                 )

# road2 = roads(
#                 roadID= 'BB01',
#                 cordinates= (25,32.6),
#                 roadLength = 60,
#                 lanes = 2,
#                 orientation=1,
#                 speedLimit = 60,
#                 oneWay = True,
#                 locationsAvailable = [{ "Z" :60}],
#                 trafficLight = 50,
#                 nodes={
#                     "N02" : 0,
#                     "N04" : 60}
#                 )

# road3 = roads(
#                 roadID= 'CC01',
#                 cordinates= (52.4,32.6),
#                 roadLength = 60,
#                 lanes = 2,
#                 orientation=1,
#                 speedLimit = 60,
#                 oneWay = True,
#                 locationsAvailable = [{ "Y" :60}],
#                 trafficLight = 50,
#                 nodes={
#                     "N03" : 0,
#                     "N05" : 60}
#                 )




# road4 = roads(
#                 roadID= 'DD01',
#                 cordinates= (52.4,32.6),
#                 roadLength = 60,
#                 lanes = 2,
#                 orientation=1,
#                 speedLimit = 60,
#                 oneWay = True,
#                 locationsAvailable = [{ "Y" :60}],
#                 trafficLight = 50,
#                 nodes={
#                     "N03" : 0,
#                     "N05" : 60}
#                 )

# graph = {
#     "N01" : {"N02" :"AA01", "N03" : "AA01"},
#     "N02" : {"N01" :"AA01", "N04" : "BB01", "N03":'AA01'},
#     "N03" : {"N01" :"AA01", "N05" : "CC01", "N02":'AA01'},
#     "N04" : {"N02" :"BB01"},
#     "N05" : {"N03" :"CC01"}
# }





car1 = car("A01", "AA01", 5, 0, 8, 0, "N01", "N05")
print(car1.route)
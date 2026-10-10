from Object_Classes.roads import roads
from Object_Classes.car import car

from Active_Lists.ActiveCars import ActiveCarsNow
from Active_Lists.ActiveRoads import ActiveRoadsList




# # Road IDs, (x, y), length, lanes, orientation
# # Horizontal roads: length = 60 m, width = 3 lanes
# road1 = roads("AA01", (0, 0), 100, 3, 0, 60, True, [0, 250, 500], None)
# road2 = roads("AA02", (0, 71.6), 100, 3, 0, 60, True, [0, 250, 500], None)
# road3 = roads("AA03", (0, 143.2), 100, 3, 0, 60, True, [0, 250, 500], None)

# # Vertical roads: length = 60 m, width = 2 lanes
# road4 = roads("BB01", (25, 11.6), 60, 2, 1, 60, True, [0, 250, 500], None)
# road5 = roads("BB02", (50, 83.2), 60, 2, 1, 60, True, [0, 250, 500], None)
# road6 = roads("BB03", (100, 0), 154.8, 3, 1, 60, True, [0, 250, 500], None)


# # ROAD AA01 — 3 lanes
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



road1 = roads(
                roadID= 'AA01',
                cordinates= (0,25),
                roadLength = 60,
                lanes = 2,
                orientation=0,
                speedLimit = 60,
                oneWay = True,
                locationsAvailable = [{ "X" :0}],
                trafficLight = 60,
                nodes= {
                    "N01": 0,
                    "N02" : 25,
                    "N03" : 52.4
                    }
                )

road2 = roads(
                roadID= 'BB01',
                cordinates= (25,32.6),
                roadLength = 60,
                lanes = 2,
                orientation=1,
                speedLimit = 60,
                oneWay = True,
                locationsAvailable = [{ "Z" :60}],
                trafficLight = 50,
                nodes={
                    "N02" : 0,
                    "N04" : 60}
                )

road3 = roads(
                roadID= 'CC01',
                cordinates= (52.4,32.6),
                roadLength = 60,
                lanes = 2,
                orientation=1,
                speedLimit = 60,
                oneWay = True,
                locationsAvailable = [{ "Y" :60}],
                trafficLight = 50,
                nodes={
                    "N02" : 0,
                    "N05" : 60}
                )

graph = {
    "N01" : {"N02" : "AA01", "N03" : "AA01"},
    "N02" : {"N01" :"AA01", "N04" : "BB01"},
    "N03" : {"N01" :"AA01", "N05" : "CC01"},
    "N04" : {"N02" :"BB01"},
    "N05" : {"N03" :"CC01"}
}


def pathFinder(graph, start, destination):
    NodeDist = {}
    for node in graph.keys():
        if node != start:
            NodeDist[node] = float("inf")
        else:
            NodeDist[node] = 0
    print(NodeDist)


pathFinder(graph, "N01", "N04")
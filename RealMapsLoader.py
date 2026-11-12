import osmnx as ox
import statistics as st


# place_name = "Cambridge, Massachusetts, USA"
# graph = ox.graph_from_place(place_name, network_type='drive')
# gets the map of the place from name for cars

# takes the center from the tuple and then takes a curcle of raduis 400m
graph = ox.graph_from_point((40.7580, -73.9855), dist=400, network_type='drive')


projectedGraph = ox.project_graph(graph)
#converts the graph form latitide and longitude to XY coordiantes(needed for pygames)


# print(nodes)
# print((projectedGraph.edges(data=True)))

#.nodes gives a dict with all the node ids and their data
#if we use data=True then its a dict with data else just a list of node ids

minX, minY = float('inf'), float('inf') #gives the valueof infinity
maxX, maxY = float('-inf'),float('-inf')
for node_id, data in projectedGraph.nodes(data=True):
    X_value = (data['x'])
    Y_value = (data['y'])

    if X_value > maxX:
        maxX = X_value
    if X_value < minX:
        minX = X_value

    if Y_value > maxY:
        maxY = Y_value
    if Y_value < minY:
        minY = Y_value
    


#finding the mimmum and maximum values of X and Y
# this tell us the scale we will use for our map

mapWidth = maxX - minX
mapHeight = maxY - minY

ScreenWidth = 1000
ScreenHeight = 1366
margin = 50 #to make a border

scale = min(((ScreenWidth - (2*margin))/mapWidth), ((ScreenHeight - (2*margin))/mapHeight))
#calculates number of pixels that represent 1 m
# uses the smaller one to avoid any distortion

# print(scale)
# scale = 5
screen_nodes = {}
'''
screen_nodes = {
    3424545 : [(x, y), 4]
}
'''


for node_id, data in projectedGraph.nodes(data=True):
    pixelX = margin + (data['x']-minX)*scale
    # takes the x coordinate, subtracts the minium X value to get the relative postion ie from 0 of the screen
    # multiplies iwth scale and adds margin to make sure it goes with the screen
    pixelY = margin + (data['y']-minY)*scale

    StreetsConnected = data['street_count']
    screen_nodes[node_id] = [(int(pixelX), int(pixelY)), StreetsConnected]

# print(projectedGraph.edges(data=True))

# print(screen_nodes)

#u              v
# (290240415, 4166731643, {'osmid': 26482715, 'highway': 'secondary', 'junction': 'roundabout', 'lanes': '2', 'maxspeed': '50',
# 'name': 'Landi Kotal Chowk', 'oneway': True, 'reversed': False, 'length': np.float64(23.978761416110444),
# 'geometry': <LINESTRING (67.055 24.937, 67.055 24.937, 67.055 24.937, 67.055 24.937)>})

# data for edges/roads in in the form of tuple. the 1st 2 valeus are the starting and ending nodes and 3rd is data


# Node IDS
# 4166731804 - 4
FinalLaneCounts = {}

for u, v, data in projectedGraph.edges(data=True):
    if u in screen_nodes and v in screen_nodes:
        wayLanes = {}

        #replaced osmid with road name as the id was only unique for roads conencting a segment
        name = data.get('name') #every continous road segment shares the same osmid 
        LaneNo = data.get('lanes', 1)

        # isinstance checks if the given object is of the given datatype
        if isinstance(LaneNo, list):
            try:
                LaneNo = int(LaneNo[0])
            except:
                LaneNo = 1
        else:
            try:
                LaneNo = int(LaneNo)
            except:
                LaneNo = 1

        if isinstance(name, list):
            name = name[0]

        if name not in wayLanes:
            wayLanes[name] = []
        wayLanes[name].append(LaneNo)

        
        for name, laneList in wayLanes.items():
            MostCommonLanes = int(st.mode(laneList))
            FinalLaneCounts[name] = MostCommonLanes


# print(FinalLaneCounts)



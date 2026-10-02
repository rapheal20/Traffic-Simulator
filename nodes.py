


class nodes():


    def __init__(self, map_position, intType, roads):
        self.postion = map_position
        self.intersection_type = intType
        # 0 = 1 road merging into another
        # 1 = roundabout
        self.connecting_roads = roads #dicionary
        #{'North' : "AA01", 'South': "BB12", 'East': "EE89", 'West' : 'BC76'}
        #dictionary format is direction : Road id

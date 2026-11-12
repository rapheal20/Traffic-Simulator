import heapq

class Router:
    #roads is ActiveRoadList
    #goes over each road and stores it under ints startNode
    def __init__(self, roads):
        self.roads = roads
        self.out = {}
        for road_ID, road_OBJ in roads.items():
            self.out.setdefault(road_OBJ.StartNode, []).append((road_ID, road_OBJ.EndNode))
        
    #act for the preferences
    def _cost(self, road, preference):
        if preference == 0:
            return road.lenght
        return road.lenght / max(road.speed_limit / 3.6, 1.0)

    # 0 is distance
    # 1 is time

    def _roads_between(self, start_node, end_node, preference):
        if start_node == end_node:
            return []

        best = {start_node : 0.0}   #holds the cheapest route with infinity as default
        came_from = {}      #stores previous node and road used to arrive
        done = set()        #already visited nodes
        heap = [(0.0, start_node)]

        while heap:
            cost, u = heapq.heappop(heap)   #takes the cheapest unfinished entry
            if u in done:       #skips entires that are already done
                continue
            done.add(u)
            if u == end_node:       #route found
                break

            for road_id, v in self.out.get(u, []):
                if v in done:
                    continue

                new_cost = cost + self._cost(self.roads[road_id], preference)
                if new_cost < best.get(v, float('inf')):    #if 2 routes found then choces the shorter one
                    best[v] = new_cost
                    came_from[v] = (u, road_id)
                    heapq.heappush(heap, (new_cost, v))

        if end_node not in came_from: #unreachable, heap emptied without ever reaching
            return None

        path, node = [], end_node
        while node != start_node:
            node, road_id = came_from[node]
            path.append(road_id)
        return path[::-1] #remakes the list in reverse so that they in travel order

    def route(self, start_road, dest_road, prefernce):
        if start_road == dest_road:
            return [start_road]

        a = self.roads[start_road]
        b = self.roads[dest_road]
        middle = self._roads_between(a.EndNode, b.StartNode, prefernce)
        if middle is None:
            return None
        if not middle and a.StartNode == b.EndNode and a.EndNode == b.StartNode:
            return None #stops an instand U-turn
        return [start_road] + middle + [dest_road]
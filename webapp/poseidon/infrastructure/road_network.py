"""
This class implements the top-level functions that maintain road networks in memory. The road network should be
represented in three different ways called Views:

1. tileView: A tile -> set of blue_edge_id mapping. The tile is a 1km x 1km region that is represented by the latitude, longitude of
its center. In python, we store this as a dictionary of lists. {(latitude, longitude): [edge_id_1, edge_id_2...], ...}
2. SegmentView: A networkx Graph object where the nodes are the blue nodes (points along a road) and the edges are the blue edges.
A blue edge is a fundamental unit of the road that is assumed to be a straight line segment.
3. SettlementView: A networkx Graph object where the nodes are settlements and edges are roads that connect these settlements.
The "red" edges each have two sets as attributes: The set of blue nodes along the inter-settlement road, and the set of
blue edges that form up that road.
"""

import networkx as nx 
import csv 
import math
from geo_location import GeoLocation
import pickle


class RoadNetwork:

    BOUNDING_DIST = 2               # 2 km bounding box distance for cities
    BASE_PATH = "../../dat/"
    SEGMENT_NODE_FILE = "cal.cnode.csv"
    SEGMENT_EDGE_FILE = "cal.cedge.csv"
    SEGMENT_PICKLE = "cal_segment.gpickle"
    SETTLE_NODE_FILE = "cal.csv"
    SETTLE_PICKLE = "cal_settle.gpickle"
    SHORTEST_PATH_PICKLE = "settle_shortest_paths.pickle"
    TILE_PICKLE = "cal_tile.gpickle"


    # Merges segment nodes of each settlement of sid
    @classmethod
    def merge_segment_nodes_of_settlemnt(cls, G_segment, G_settle, sid):
        seg_nodes =  list(G_settle.nodes()[sid]['seg'])
        #print (sid, seg_nodes)
        merged_node = str(seg_nodes[0])
        if len(seg_nodes) > 0:
            for j in range(1, len(seg_nodes)):
                G_segment = nx.contracted_nodes(G_segment, merged_node, str(seg_nodes[j]))
        return G_segment, merged_node

    def __init__(self, should_load_from_files=False):
        if should_load_from_files:
            min_lat = 400
            max_lat = -400
            min_long = 400
            max_long = -400
            # load segment view from node and edge csv
            G_segment = None
            '''
            print ("Building segment view ...")
            G_segment = nx.Graph()
            with open(self.BASE_PATH + self.SEGMENT_NODE_FILE) as csv_f:
                csv_r = csv.reader(csv_f, delimiter=',')
                for row in csv_r:
                    lat = float(row[2])
                    lng = float(row[1])
                    nid = row[0]            # for some reason if I make nid = int(row[0]), node count doubles
                    G_segment.add_node(nid, pos=GeoLocation.from_degrees(lat, lng),  mappedToCity=False)     
                    min_lat = min(lat, min_lat)
                    max_lat = max(lat, max_lat)
                    min_long = min(lng, min_long)
                    max_long = max(lng, max_long)
            with open(self.BASE_PATH + self.SEGMENT_EDGE_FILE) as csv_f:
                csv_r = csv.reader(csv_f, delimiter=',')
                for row in csv_r:
                    G_segment.add_edge(row[1], row[2], d=row[3])
            print ("Done;", nx.number_of_nodes(G_segment), "segments")
            '''
            
            '''
            print ("Min lat: ", min_lat)
            print ("Min long: ", min_long)
            print ("Max lat: ", max_lat)
            print ("Max long: ", max_long)
            '''
            
            G_tile = None
            # create tile view from segment view
            '''
            print ("Building tile view ...")
            G_tile = nx.Graph()
            delta = 0.01
            cnt = 0
            while min_lat <= max_lat:
                while min_long <= max_long:
                    # tile boundaries
                    SW_loc = GeoLocation.from_degrees(min_lat, min_long)
                    NE_loc = GeoLocation.from_degrees(min_lat + delta, min_long + delta)
                    edges = set()   # edges from segment view
                    # take every edge
                    eid = 0
                    for e in G_segment.edges():
                        u = G_segment.node()[e[0]]['pos']
                        v = G_segment.node()[e[1]]['pos']

                        # check if this edge intersects this tile
                        if GeoLocation.line_intersects_box(u, v, SW_loc, NE_loc):
                            edges.add(eid)
                        eid += 1
                    G_tile.add_node((SW_loc, NE_loc), seg_edges=edges)
                    min_long += delta
                min_lat += delta 
                cnt += 1
                if cnt % 1000 == 0:
                    print ("Processed", cnt, "tiles")
            print ("Done;", nx.number_of_nodes(G_tile), "tiles")
            nx.write_gpickle(G_tile, self.BASE_PATH + self.TILE_PICKLE)
            '''


            # create settlement view from segment view
            G_settle = None
            '''
            print ("Building settlement view ...")
            G_settle = nx.Graph()
            with open(self.BASE_PATH + self.SETTLE_NODE_FILE) as csv_f:
                csv_r = csv.DictReader(csv_f, delimiter=',')
                k = 0
                for row in csv_r:
                    lat = float(row['lat'])
                    lng = float(row['lng'])
                    loc = GeoLocation.from_degrees(lat, lng)
                    SW_loc, NE_loc = loc.bounding_locations(self.BOUNDING_DIST)
                    
                    #print (SW_loc.deg_lat, SW_loc.deg_lon, NE_loc.deg_lat, NE_loc.deg_lon)

                    # find all nodes that are within this box
                    segment_nodes_in = []  # would contain which segment nodes are in this box
                    for i in range(nx.number_of_nodes(G_segment)):
                        v = G_segment.nodes()[str(i)]
                        v_loc = v['pos']    #
                        v_mapped = v['mappedToCity']
                        if not v_mapped and v_loc.within_bounds(SW_loc, NE_loc) :
                            #print (v_loc, "in", SW_loc, NE_loc)
                            segment_nodes_in.append(i)
                            G_segment.nodes()[str(i)]['mappedToCity'] = True
            
                    # if no nodes inside this box, discard city
                    if (len(segment_nodes_in) > 0):
                        G_settle.add_node(k, name=row['city'], box=(SW_loc, NE_loc), seg=set(segment_nodes_in), pop=row['population'], density=row['density'])
                        k += 1
            
            print ("Done;",nx.number_of_nodes(G_settle), "settlements")
            
            nx.write_gpickle(G_segment, self.BASE_PATH + self.SEGMENT_PICKLE)
            nx.write_gpickle(G_settle, self.BASE_PATH + self.SETTLE_PICKLE)
            '''

            # find the edges that connect settlement A to B
            # would store the resulting graph to file and reload
            
            G_segment = nx.read_gpickle(self.BASE_PATH + self.SEGMENT_PICKLE)
            G_settle = nx.read_gpickle(self.BASE_PATH + self.SETTLE_PICKLE)

            # run dfs
            n_settle = nx.number_of_nodes(G_settle)
            n_segment = nx.number_of_nodes(G_segment)
            print ("Running dfs on %d settlements ..." % n_settle)
            for i in range(n_settle):
                G_segment_2 = G_segment.copy()
                print (nx.number_of_nodes(G_segment_2), nx.number_of_edges(G_segment_2))
                # merge all nodes in src city to single node
                G_segment_2, src = RoadNetwork.merge_segment_nodes_of_settlemnt(G_segment_2, G_settle, i)
                print ("SRC:", src)
                no_path = 0
                for j in range(i+1, n_settle):
                    G_segment_3 = G_segment_2.copy()
                    # merge all nodes in dst city to single node
                    G_segment_3, dst = RoadNetwork.merge_segment_nodes_of_settlemnt(G_segment_3, G_settle, j)
            
                    # delete all nodes belonging to cities that are not src or dst
                    for k in range(n_settle):
                        if k != i and k != j:
                            seg_nodes = G_settle.nodes()[k]['seg']
                            for node in seg_nodes:
                                G_segment_3.remove_node(str(node))
                            #print (nx.number_of_nodes(G_segment_3), nx.number_of_edges(G_segment_3))
                    
                    try:
                        p = nx.dijkstra_path(G_segment_3, source=src, target=dst)
                        print (p)
                    except:
                        no_path += 1

                    if (j % 100 == 0):
                        print ("Processed %d nodes" % j)

                print ("No path: %d" % no_path)
                break           

        else:
            G_segment = nx.read_gpickle(self.BASE_PATH + self.SEGMENT_PICKLE)
            G_settle = nx.read_gpickle(self.BASE_PATH + self.SHORTEST_PATH_PICKLE)
            G_tile = nx.read_gpickle(self.BASE_PATH + self.TILE_PICKLE)

        self.tileView = G_tile
        self.segmentView = G_segment
        self.settlementView = G_settle

    

    # This function should return the pertinent settlementView for a given segmentView. Useful to apply damages.
    # Should follow a different methodology from what we use to create the settlement view since all we have to
    # do here is edge deletion. To be completed by: Harish
    def get_recalculated_settlement_view_from_segment_view(self, revised_segment_view):
        pass

    # This function takes a given set of tiles (damaged) and deletes the corresponding edges from the segmentView.
    # Useful for applying damages. To be completed by: Harish
    def get_recalculated_segment_view(self, damaged_road_tiles):
        pass


# test driver code
r = RoadNetwork(True)

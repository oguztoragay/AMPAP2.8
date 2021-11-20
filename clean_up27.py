from shapely import geometry, ops
from shapely.ops import nearest_points
from shapely.geometry import Point, LineString
from GSminimal import re_Generate
import numpy as np
import itertools
import pickle
from statistics import mean

def clean_up(w, h, r_ound, step_results):
    PML, Nd, nna = geometry_extraction(w, h, r_ound, step_results)
    line_index = [k for k in PML.keys() if (PML[k].inn == True)]
    print(len(line_index))
    # print('Number of crossing locations: %d' % num_intersections)
    # print('Number of removed nodes: %d' % number_removed_nodes)
    return PML, Nd, nna

def geometry_extraction(w, h, r_ound, step_results):
    # read every necessary data which is base ground structure and the solution of previous round
    # f_name = str('%dx%d_Step1_%d_results.pickle' % (w, h, r_ound))
    # pickle_in = open(f_name, "rb");    sol = pickle.load(pickle_in)
    # {'volume': vol, 'a': a, 'u': u, 'Cn': Cn, 'Nd': Nd, 'PML': PML}
    Cn = step_results['Cn'];    a = step_results['a'];    u = step_results['u']
    PML = step_results['PML'];  Nd = step_results['Nd']
    print(len(Cn))
    # f0_name = str('%dx%d_Step1_ground.pickle' % (w, h))
    # pickle0_in = open(f0_name, "rb");    ground = pickle.load(pickle0_in)
    # node_ = ground[0];  elements_ = ground[1]
    line_index_for_check = [k for k in Cn.keys() if (a[k] > 0.1)]
    remained_lines_shapely = []
    for i in line_index_for_check:
        # for each appearing elements generate the shapely item
        node1 = [Nd[Cn[i].orient[0]].x, Nd[Cn[i].orient[0]].y]
        node2 = [Nd[Cn[i].orient[1]].x, Nd[Cn[i].orient[1]].y]
        remained_lines_shapely.append([geometry.LineString([node1, node2]), a[i]])
    crossing_lines_shapely = {}
    num_intersections = 0
    for i, j in itertools.combinations(remained_lines_shapely, 2):
        # check if the remained lines have intersections, extract the pair of crossing lines
        insect = i[0].intersects(j[0])
        touch = i[0].touches(j[0])
        if insect == True and touch == False:
            crossing_lines_shapely[num_intersections] = (i, j, i[0].intersection(j[0]))
            num_intersections += 1
    list_value = [10 * kk for kk in list(range(0, w, 1))]
    for l1 in crossing_lines_shapely.keys():
        # finding the nearest ground structure node to the crossing of two line string.
        l = crossing_lines_shapely[l1]
        crossing_node = l[2]
        x_ = min(list_value, key=lambda list_value: abs(list_value - crossing_node.x))
        y_ = min(list_value, key=lambda list_value: abs(list_value - crossing_node.y))
        nearest_node_coordinates = (x_, y_)
        l += (nearest_node_coordinates,)  # append to the pair of crossing lines, the node which is closest to the intersection
        crossing_lines_shapely[l1] = l
    tamiz = crossing_more(crossing_lines_shapely)
    for i in crossing_lines_shapely:
        # added the crosseing members to tabu list by making .inn for them False
        line1_fp = []; line1_pf = []; line1_lp = []; line1_pl = []; line2_fp = []; line2_pf = []; line2_lp = []; line2_pl = []
        line1 = crossing_lines_shapely[i][0][0]
        line2 = crossing_lines_shapely[i][1][0]
        point_ = Point(crossing_lines_shapely[i][3])
        # c1 = line1.distance(point_)
        # c2 = line2.distance(point_)
        c1 = crossing_lines_shapely[i][0][1]
        c2 = crossing_lines_shapely[i][1][1]
        # if c1 > c2:
        if c1 < c2:
            line1_no = shapely_to_ground(line1, Nd, PML)
            PML[list(line1_no)[0]].inn = False
            PML[list(line1_no)[0]].okay = 0
            first = list(line1.coords[0])
            last = list(line1.coords[-1])
            fp = first + [point_.x, point_.y]
            pf = [point_.x, point_.y] + first
            lp = last + [point_.x, point_.y]
            pl = [point_.x, point_.y] + last
            line1_fp = [i for i in PML.keys() if PML[i].bounds == fp]
            line1_pf = [i for i in PML.keys() if PML[i].bounds == pf]
            line1_lp = [i for i in PML.keys() if PML[i].bounds == lp]
            line1_pl = [i for i in PML.keys() if PML[i].bounds == pl]
        else:
            line2_no = shapely_to_ground(line2, Nd, PML)
            PML[list(line2_no)[0]].inn = False
            PML[list(line2_no)[0]].okay = 0
            first = list(line2.coords[0])
            last = list(line2.coords[-1])
            fp = first + [point_.x, point_.y]
            pf = [point_.x, point_.y] + first
            lp = last + [point_.x, point_.y]
            pl = [point_.x, point_.y] + last
            line2_fp = [i for i in PML.keys() if PML[i].bounds == fp]
            line2_pf = [i for i in PML.keys() if PML[i].bounds == pf]
            line2_lp = [i for i in PML.keys() if PML[i].bounds == lp]
            line2_pl = [i for i in PML.keys() if PML[i].bounds == pl]
        to_be_added = line1_fp + line1_pf + line1_lp + line1_pl + line2_fp + line2_pf + line2_lp + line2_pl
        for i in to_be_added:
            PML[i].inn = True
    return PML, Nd, num_intersections

def shapely_to_ground(i, Nd, PML):
    # convert the shapely line to a dictionary key in Elements which needs to be off in the ground structure.
    node1 = [i.xy[0][0], i.xy[1][0]]
    node2 = [i.xy[0][1], i.xy[1][1]]
    node1_name = [k for k in Nd.keys() if (Nd[k].x == node1[0] and Nd[k].y == node1[1])]
    node2_name = [k for k in Nd.keys() if (Nd[k].x == node2[0] and Nd[k].y == node2[1])]
    orientation = [node1_name[0], node2_name[0]]
    line_to_off = dict(filter(lambda item: orientation == item[1].orient, PML.items())).keys()
    return line_to_off

def crossing_more(l):
    lines_dic = {}
    k_ey = 0
    pure_off = {}
    for i in l:
        for j in l[i][:2]:
            l1_ = [sh for sh in l.keys() if j == l[sh][0] or j == l[sh][1]]
            lines_dic[k_ey] = (str(j), len(l1_))
            k_ey += 1
            # if len(l1_) == 1:
            #     pure_off += tuple(str(j))
            print(str(j) + ' appears in: ' + str(l1_))
    pure_off = set(val for dic in [lines_dic] for val in dic.values())
    return pure_off


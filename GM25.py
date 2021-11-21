from shapely import geometry, ops
from shapely.geometry import Point
from shapely.ops import cascaded_union
import numpy as np
import itertools
import pickle

def evaluate_result(w, h, tabu_list):
    f_name = str('%dx%d_results.pickle' % (w, h))
    pickle_in = open(f_name, "rb")
    sol = pickle.load(pickle_in)
    Cn = sol[0]; a = sol[1]; u = sol[2]; PML = sol[3]; Nd = sol[5]
    shap_node, lines, hull, index_for_not_in = geometry_extraction(Cn, a, PML, Nd)
    remained_nodes, nna, mm_tabu, PML, tabu_list = new_node_coords(Nd, lines, PML, shap_node, tabu_list, index_for_not_in)
    # remained_nodes, removed_nodes_list = \
    # remained_nodes,  mm = clean_nodes(remained_nodes, nna)
    print('Number of crossing locations with new added nodes: %d' % nna)
    print('Number of crossing locations added to the Tabu list: %d' % len(tabu_list))
    # print('Number of removed nodes: %d' % number_removed_nodes)
    return remained_nodes, nna, mm_tabu, PML, tabu_list

def geometry_extraction(Cn, a, PML, Nd):
    # inputs from the previous ground structure and the solution of previous round
    lines = []
    shap_node = set()
    index_for_in = {k: a[k] for k in Cn.keys() if (a[k] > 0.001)}  # lines to be checked for intersections
    index_for_not_in = []
    for i in index_for_in:
        if index_for_in[i] > 0.01:
            node_x = [Nd[Cn[i].orient[0]].x, Nd[Cn[i].orient[0]].y]
            node_y = [Nd[Cn[i].orient[1]].x, Nd[Cn[i].orient[1]].y]
            line_to_add = geometry.LineString([node_x, node_y])
            line_to_add.r = index_for_in[i]
            lines.append(line_to_add)
            shap_node.add((node_x[0], node_x[1]))
            shap_node.add((node_y[0], node_y[1]))
        else:
            index_for_not_in.append(i)
    shap_node = [Point(i) for i in shap_node]
    multi_line = geometry.MultiLineString([i for i in lines])
    merged_line = ops.linemerge(multi_line)
    hull = merged_line.convex_hull
    for i in Nd.keys():
        Nd[i].inside = int(hull.contains(Point([Nd[i].x, Nd[i].y])) or hull.touches(Point([Nd[i].x, Nd[i].y])))
        Nd[i].base = 1
    return shap_node, lines, hull, index_for_not_in

def new_node_coords(Nd, lines, PML, shap_node, tabu_list, index_for_not_in):
    for i in index_for_not_in:
        tabu_list[i] = PML[i]
    print('Number of lines before clean-up: %d' % (len(lines)))
    lines = clean_remaining_lines(lines)
    print('Number of lines after clean-up: %d' % (len(lines)))
    remained_nodes = []
    for i in Nd.keys():
        remained_nodes.append([Nd[i].x, Nd[i].y, Nd[i].load, Nd[i].tip, Nd[i].inside, Nd[i].base])
    crossing_lines_shapely = {}
    inters_idx = 0
    for i, j in itertools.combinations(lines, 2):
        insect = i.intersects(j)
        touch = i.touches(j)
        if insect == True and touch == False:
            inter_sect_coord = i.intersection(j).coords[0]
            faseleha = [np.sqrt((inter_sect_coord[0]-Nd[i].coord[0])**2 + (inter_sect_coord[1]-Nd[i].coord[1])**2) for i in Nd.keys()]
            val, idx = min((val, idx) for (idx, val) in enumerate(faseleha))
            crossing_lines_shapely[inters_idx] = (i, j, i.intersection(j).coords[0], val, idx)
            inters_idx += 1
    number_nodes_added = 0
    mored = {}
    mm_node = 0
    mm_tabu = 0
    for i in crossing_lines_shapely.items():
        if i[1][3] > 3:
            mored[mm_node] = list(i[1][2])
            mm_node += 1
            remained_nodes.append([i[1][2][0], i[1][2][1], 0, 3, 1, 0])
        else:
            line1 = i[1][0]
            line2 = i[1][1]
            point_ = Point(i[1][2])
            c1 = line1.r
            c2 = line2.r
            if c1 < c2:
                mm_tabu += 1
                line1_no = shapely_to_ground(line1, Nd, PML)
                tabu_list[list(line1_no)[0]] = PML[list(line1_no)[0]]
                PML[list(line1_no)[0]].inn = False
                PML[list(line1_no)[0]].okay = 0
            elif c1 > c2:
                mm_tabu += 1
                line2_no = shapely_to_ground(line2, Nd, PML)
                tabu_list[list(line2_no)[0]] = PML[list(line2_no)[0]]
                PML[list(line2_no)[0]].inn = False
                PML[list(line2_no)[0]].okay = 0
            else:
                mm_tabu += 2
                line1_no = shapely_to_ground(line1, Nd, PML)
                line2_no = shapely_to_ground(line2, Nd, PML)
                tabu_list[list(line1_no)[0]] = PML[list(line1_no)[0]]
                tabu_list[list(line2_no)[0]] = PML[list(line2_no)[0]]
                PML[list(line1_no)[0]].inn = False
                PML[list(line1_no)[0]].okay = 0
                PML[list(line2_no)[0]].inn = False
                PML[list(line2_no)[0]].okay = 0
    # tabu_list = tabu_list + [PML[i] for i in index_for_not_in]
    return remained_nodes, mm_node, mm_tabu, PML, tabu_list

def clean_remaining_lines(x):
    remove = []
    for i in x:
        i.angle = np.rad2deg(np.arctan2(abs(i.xy[1][1]-i.xy[1][0]), abs(i.xy[0][1]-i.xy[0][0])))
    for i, j in itertools.combinations(x, 2):
        if i.angle == j.angle:
            if i.within(j):
                remove.append(j)
            elif j.within(i):
                remove.append(i)
            else:  continue
    for i, j in itertools.combinations(x, 2):
        if cascaded_union(i.intersection(j)).length > 0.1 and i.angle == j.angle:
            if i.length > j.length:
                remove.append(i)
            else:
                remove.append(j)
    res = []
    rem = [res.append(x) for x in remove if x not in res]
    ret = []
    rem = [ret.append(y) for y in x if y not in res]
    return ret

def shapely_to_ground(i, Nd, PML):
    # convert the shapely line to a dictionary key in Elements which needs to be off in the ground structure.
    node1 = [i.xy[0][0], i.xy[1][0]]
    node2 = [i.xy[0][1], i.xy[1][1]]
    node1_name = [k for k in Nd.keys() if (Nd[k].x == node1[0] and Nd[k].y == node1[1])]
    node2_name = [k for k in Nd.keys() if (Nd[k].x == node2[0] and Nd[k].y == node2[1])]
    orientation = [node1_name[0], node2_name[0]]
    line_to_off = dict(filter(lambda item: orientation == item[1].orient, PML.items())).keys()
    return line_to_off


# evaluate_result(5, 5, {})

from shapely import geometry, ops
from shapely.geometry import Point
from GSminimal import re_Generate
from shapely.ops import cascaded_union
import numpy as np
import itertools
import pickle
from statistics import mean
import sklearn
from numpy import unique
from collections import Counter
from numpy import where
from sklearn.datasets import make_classification
from sklearn.cluster import KMeans
from collections import OrderedDict

def evaluate_result(w, h, r_ound, step_results, tabu_list):
    PML = step_results['PML']; Nd = step_results['Nd']
    # remained_nodes, hull, remained_lines, remrem1, mm, nna = \
    shap_node, lines, hull = geometry_extraction(w, h, PML, Nd)
    remained_nodes, nna, PML, tabu_list = new_node_coords(Nd, lines, PML, shap_node, tabu_list)
    # remained_nodes, removed_nodes_list = \
    # remained_nodes,  mm = clean_nodes(remained_nodes, nna)
    print('Number of crossing locations with new added nodes: %d' % nna)
    print('Number of crossing locations added to the Tabu list: %d' % len(tabu_list))
    # print('Number of removed nodes: %d' % number_removed_nodes)
    return remained_nodes, nna, PML, tabu_list

def geometry_extraction(w, h, PML, Nd):
    # inputs from the previous ground structure and the solution of previous round
    f_name = str('%dx%d_results.pickle' % (w, h))
    pickle_in = open(f_name, "rb")
    sol = pickle.load(pickle_in)
    Cn = sol[0];    a = sol[1];    u = sol[2]
    # -----------------------------------------
    lines = []
    shap_node = set()
    index_for_in = {k: a[k] for k in Cn.keys() if (a[k] > 0.05)}  # lines to be checked for intersections
    for i in index_for_in:
        node_x = [Nd[Cn[i].orient[0]].x, Nd[Cn[i].orient[0]].y]
        node_y = [Nd[Cn[i].orient[1]].x, Nd[Cn[i].orient[1]].y]
        line_to_add = geometry.LineString([node_x, node_y])
        line_to_add.r = index_for_in[i]
        lines.append(line_to_add)
        shap_node.add((node_x[0], node_x[1]))
        shap_node.add((node_y[0], node_y[1]))
    shap_node = [Point(i) for i in shap_node]
    multi_line = geometry.MultiLineString([i for i in lines])
    merged_line = ops.linemerge(multi_line)
    hull = merged_line.convex_hull
    for i in Nd.keys():
        Nd[i].inside = int(hull.contains(Point([Nd[i].x, Nd[i].y])) or hull.touches(Point([Nd[i].x, Nd[i].y])))
        Nd[i].base = 1
    # remained_nodes, mm = new_node_coords(node_, lines, r_ound, PML, Nd)
    return shap_node, lines, hull

def new_node_coords(Nd, lines, PML, shap_node, tabu_list):
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
    mm = 0
    # tabu_list = {}
    for i in crossing_lines_shapely.items():
        if i[1][3] > 2:
            mored[mm] = list(i[1][2])
            mm += 1
            remained_nodes.append([i[1][2][0], i[1][2][1], 0, 3, 1, 0])
            # line1 = geometry.LineString([i.coords[0], [x_add, y_add]]);     line1.r = i.r
            # line2 = geometry.LineString([[x_add, y_add], i.coords[1]]);     line2.r = i.r
            # line3 = geometry.LineString([j.coords[0], [x_add, y_add]]);     line3.r = j.r
            # line4 = geometry.LineString([[x_add, y_add], j.coords[1]]);     line4.r = j.r
            # lines_added.append([line1, line2, line3, line4])
            # lines.append(line1);    lines.append(line2);    lines.append(line3);    lines.append(line4)
        else:
            # nearest_node_coordinates = Nd[idx].coord
            # tamiz = crossing_more(crossing_lines_shapely)
            # line1_fp = [];  line1_pf = [];  line1_lp = [];  line1_pl = [];  line2_fp = [];  line2_pf = [];  line2_lp = [];  line2_pl = []
            line1 = i[1][0]
            line2 = i[1][1]
            point_ = Point(i[1][2])
            # c1 = line1.distance(point_)
            # c2 = line2.distance(point_)
            c1 = line1.r
            c2 = line2.r
            # if c1 > c2:
            if c1 < c2:
                mm += 1
                line1_no = shapely_to_ground(line1, Nd, PML)
                tabu_list[list(line1_no)[0]] = PML[list(line1_no)[0]]
                PML[list(line1_no)[0]].inn = False
                PML[list(line1_no)[0]].okay = 0
                # first = list(line1.coords[0])
                # last = list(line1.coords[-1])
                # fp = first + [point_.x, point_.y]
                # pf = [point_.x, point_.y] + first
                # lp = last + [point_.x, point_.y]
                # pl = [point_.x, point_.y] + last
                # line1_fp = [i for i in PML.keys() if PML[i].bounds == fp]
                # line1_pf = [i for i in PML.keys() if PML[i].bounds == pf]
                # line1_lp = [i for i in PML.keys() if PML[i].bounds == lp]
                # line1_pl = [i for i in PML.keys() if PML[i].bounds == pl]
            else:
                mm += 1
                line2_no = shapely_to_ground(line2, Nd, PML)
                tabu_list[list(line2_no)[0]] = PML[list(line2_no)[0]]
                PML[list(line2_no)[0]].inn = False
                PML[list(line2_no)[0]].okay = 0
            #     first = list(line2.coords[0])
            #     last = list(line2.coords[-1])
            #     fp = first + [point_.x, point_.y]
            #     pf = [point_.x, point_.y] + first
            #     lp = last + [point_.x, point_.y]
            #     pl = [point_.x, point_.y] + last
            #     line2_fp = [i for i in PML.keys() if PML[i].bounds == fp]
            #     line2_pf = [i for i in PML.keys() if PML[i].bounds == pf]
            #     line2_lp = [i for i in PML.keys() if PML[i].bounds == lp]
            #     line2_pl = [i for i in PML.keys() if PML[i].bounds == pl]
            # to_be_added = line1_fp + line1_pf + line1_lp + line1_pl + line2_fp + line2_pf + line2_lp + line2_pl
    # for mm in mored:
    #     if mm in lines:
    #         lines.remove(mm)
    # remained_lines = lines
    # remrem = clean_remaining_lines(remained_lines)
    # remrem1 = []
    # for i in remrem:
    #     n_1 = [i.coords[0][0], i.coords[0][1]]
    #     n_2 = [i.coords[1][0], i.coords[1][1]]
    #     rr = i.r
    #     remrem1.append([n_1, n_2, rr])
    return remained_nodes, mm, PML, tabu_list

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

# def clean_nodes(y, nna):
#     X = [i[:2] for i in y]
#     kmeans = KMeans(n_clusters=len(y)-nna, random_state=2).fit(X)
#     l_abel = kmeans.labels_
#     for i in y:
#             i.append(l_abel[y.index(i)])
#     dup = {item: count for item, count in Counter(l_abel).items() if count > 1}
#     s = kmeans.cluster_centers_
#     added_nodes = []
#     for i in dup.keys():
#         # print(i)
#         added_nodes.append(list(s[i])+[0, 3, 1, 0])
#     deleted_nodes = []
#     for i in y:
#         if i[-1] in dup.keys():
#             deleted_nodes.append(i)
#         else:
#             pass
#     y = [i for i in y if i not in deleted_nodes]
#     y = y + added_nodes
#     return y, deleted_nodes

def shapely_to_ground(i, Nd, PML):
    # convert the shapely line to a dictionary key in Elements which needs to be off in the ground structure.
    node1 = [i.xy[0][0], i.xy[1][0]]
    node2 = [i.xy[0][1], i.xy[1][1]]
    node1_name = [k for k in Nd.keys() if (Nd[k].x == node1[0] and Nd[k].y == node1[1])]
    node2_name = [k for k in Nd.keys() if (Nd[k].x == node2[0] and Nd[k].y == node2[1])]
    orientation = [node1_name[0], node2_name[0]]
    line_to_off = dict(filter(lambda item: orientation == item[1].orient, PML.items())).keys()
    return line_to_off

# def crossing_more(l):
#     lines_dic = {}
#     k_ey = 0
#     pure_off = {}
#     for i in l:
#         for j in l[i][:2]:
#             l1_ = [sh for sh in l.keys() if j == l[sh][0] or j == l[sh][1]]
#             lines_dic[k_ey] = (str(j), len(l1_))
#             k_ey += 1
#             # if len(l1_) == 1:
#             #     pure_off += tuple(str(j))
#             print(str(j) + ' appears in: ' + str(l1_))
#     pure_off = set(val for dic in [lines_dic] for val in dic.values())
#     return pure_off

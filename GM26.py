from shapely import geometry, ops
from shapely.geometry import Point
from shapely.ops import cascaded_union
import numpy as np
import itertools
import pickle

def evaluate_result(w, h, r_ound):
    f_name = str('%dx%d_results.pickle' % (w, h))
    pickle_in = open(f_name, "rb")
    sol = pickle.load(pickle_in)
    Cn = sol[0]; a = sol[1]; u = sol[2]; PML = sol[3]; Nd = sol[5]
    sh_nodes, sh_lines = shapely_geometry_extraction(Cn, a, Nd, r_ound)
    remained_nodes, nna = new_node_coords(Nd, sh_lines, r_ound)
    return remained_nodes, nna

def shapely_geometry_extraction(Cn, a, Nd, r_ound):
    sh_lines = []
    sh_nodes = set()
    index_for_in = {k: a[k] for k in Cn.keys() if (a[k] > 0.12)}  # lines to be checked for intersections
    for i in index_for_in:
        node_x = [Nd[Cn[i].orient[0]].x, Nd[Cn[i].orient[0]].y]
        node_y = [Nd[Cn[i].orient[1]].x, Nd[Cn[i].orient[1]].y]
        line_to_add = geometry.LineString([node_x, node_y])
        line_to_add.r = index_for_in[i]
        sh_lines.append(line_to_add)
    for i in Nd:
        sh_nodes.add(Nd[i].coord)
    sh_nodes = [Point(i) for i in sh_nodes]
    return sh_nodes, sh_lines

def new_node_coords(Nd, sh_lines, r_ound):
    print('Number of lines before clean-up: %d' % (len(sh_lines)))
    sh_lines = clean_remaining_lines(sh_lines)
    print('Number of lines after clean-up: %d' % (len(sh_lines)))
    remained_nodes = []
    for i in Nd.keys():
        if Nd[i].tip < 3:
            remained_nodes.append([Nd[i].x, Nd[i].y, Nd[i].load, Nd[i].tip, 1, 1])
    crossing_lines = {}
    inters_idx = 0
    for i, j in itertools.combinations(sh_lines, 2):
        insect = i.intersects(j)
        touch = i.touches(j)
        if insect == True and touch == False:
            inter_sect_coord = i.intersection(j).coords[0]
            inter_sect_coord = [np.round(i, 1) for i in inter_sect_coord]
            faseleha = [np.sqrt((inter_sect_coord[0]-Nd[i].coord[0])**2 + (inter_sect_coord[1]-Nd[i].coord[1])**2) for i in Nd.keys()]
            val, idx = min((val, idx) for (idx, val) in enumerate(faseleha))
            if val > 0.5:
                crossing_lines[inters_idx] = (i, j, i.intersection(j).coords[0])
                inters_idx += 1
    for i in crossing_lines:
        remained_nodes.append([crossing_lines[i][2][0], crossing_lines[i][2][1], 0, 3, 0, 0])
    remained_nodes, nna = clean_remaining_nodes(remained_nodes)
    return remained_nodes, nna

def clean_remaining_nodes(x):
    print('Number of nodes before clean-up: %d' % (len(x)))
    y = []
    main_gs_nodes = []
    newly_added_nodes = []
    for i in x:
        if i[3] != 3:
            y.append(i)
            main_gs_nodes.append(i)
        else:
            newly_added_nodes.append(i)
    sss = []
    while len(newly_added_nodes):
        combined = []
        temp_list = []
        temp_node = newly_added_nodes.pop(0)
        temp_list.append(temp_node)
        for jj in temp_list:
            for j in newly_added_nodes:
                if np.sqrt((jj[0] - j[0]) ** 2 + (jj[1] - j[1]) ** 2) < 2:
                    temp_list.append(j)
                    newly_added_nodes.pop(newly_added_nodes.index(j))
                    # combined.append(jj)
                    # newly_added_nodes.pop(newly_added_nodes.index(j))
                # mored += 1
        added_x = np.mean([temp_list[i][0] for i in range(len(temp_list))], axis=0)
        added_y = np.mean([temp_list[i][1] for i in range(len(temp_list))], axis=0)
        sss.append([added_x, added_y, temp_node[2], temp_node[3], temp_node[4]])
    remained_nodes = sss
    sss1 = []
    mored1 = 0
    new_generated_nodes1 = []
    while len(remained_nodes):
        # temp_list = []
        temp_node = remained_nodes.pop(0)
        # added_x = temp_node[0]
        # added_y = temp_node[1]
        # temp_list.append(temp_node)
        # for j in main_gs_nodes:
        if any([True for j in main_gs_nodes if np.sqrt((temp_node[0] - j[0]) ** 2 + (temp_node[1] - j[1]) ** 2) < 1]):
            break
        else:
            new_generated_nodes1.append(temp_node)
                # temp_list.append(j)
                # mored1 += 1
                # added_x = np.mean([temp_list[i][0] for i in range(len(temp_list))], axis=0)
                # added_y = np.mean([temp_list[i][1] for i in range(len(temp_list))], axis=0)
                # remained_nodes.pop(remained_nodes.index(j))
                # new_generated_nodes1.append([added_x, added_y, temp_node[2], temp_node[3], temp_node[4]])
        # sss1.append([added_x, added_y, temp_node[2], temp_node[3], temp_node[4]])
    remained_nodes = main_gs_nodes + new_generated_nodes1
    print('Number of nodes after clean-up: %d' % (len(remained_nodes)))
    print('aaaaaaaaaaaa   MORED  aaaaaaaaaaaaaaaaaaaa', mored1)
    return remained_nodes, len(remained_nodes) - len(x)

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

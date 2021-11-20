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

# def update_GS(wt, ht, fixed, load_node, load_value, ff, foldername):
def update_GS(w, h, r_ound):
    remained_nodes, hull, remained_lines, remrem1, mm, nna = geometry_extraction(w, h, r_ound)
    remained_nodes, removed_nodes_list = clean_nodes(remained_nodes, nna)
    print('Number of crossing locations: %d' % nna)
    # print('Number of removed nodes: %d' % number_removed_nodes)
    return remained_nodes, removed_nodes_list, hull, remained_lines, remrem1, mm, nna

def geometry_extraction(w, h, r_ound):
    # inputs from the previous ground structure and the solution of previous round
    f_name = str('%dx%d_results.pickle' % (w, h))
    pickle_in = open(f_name, "rb")
    sol = pickle.load(pickle_in)
    Cn = sol[0];    a = sol[1];    u = sol[2]
    f0_name = str('%dx%d_ground.pickle' % (w, h))
    pickle0_in = open(f0_name, "rb")
    ground = pickle.load(pickle0_in)
    node_ = ground[0];    elements_ = ground[1]
    # -----------------------------------------
    lines = []
    shap_node = set()
    index_for_in = {k: a[k] for k in Cn.keys() if (a[k] > 0.1)}
    for i in index_for_in:
        node_x = [node_[Cn[i].orient[0]].x, node_[Cn[i].orient[0]].y]
        node_y = [node_[Cn[i].orient[1]].x, node_[Cn[i].orient[1]].y]
        line_to_add = geometry.LineString([node_x, node_y])
        line_to_add.r = index_for_in[i]
        lines.append(line_to_add)
        shap_node.add((node_x[0], node_x[1]))
        shap_node.add((node_y[0], node_y[1]))
    shap_node = [Point(i) for i in shap_node]
    multi_line = geometry.MultiLineString([i for i in lines])
    merged_line = ops.linemerge(multi_line)
    hull = merged_line.convex_hull
    for i in node_.keys():
        node_[i].inside = int(hull.contains(Point([node_[i].x, node_[i].y])) or hull.touches(Point([node_[i].x, node_[i].y])))
        node_[i].base = 1
    remained_nodes, remained_lines, remrem1, mm, nna = new_node_coords(node_, lines, r_ound)
    return remained_nodes, hull, remained_lines, remrem1, mm, nna

def new_node_coords(node_, lines, r_ound):
    # if r_ound > 1:
    print('Number of lines before clean-up: %d' % (len(lines)))
    lines = clean_rem(lines)
    print('Number of lines after clean-up: %d' % (len(lines)))
    remained_nodes = []
    for i in node_.keys():
        remained_nodes.append([node_[i].x, node_[i].y, node_[i].load, node_[i].tip, node_[i].inside, node_[i].base])
    mored = {}
    mm = -1
    lines_added = []
    lines_to_remove = []
    number_nodes_added = 0
    for i, j in itertools.combinations(lines, 2):
        insect = i.intersects(j)
        touch = i.touches(j)
        if insect == True and touch == False:
            number_nodes_added += 1
            lines_to_remove.append(i)
            lines_to_remove.append(j)
            mm += 1
            x_add = i.intersection(j).x
            y_add = i.intersection(j).y
            mored[mm] = [x_add, y_add]
            remained_nodes.append([x_add, y_add, 0, 3, 1, 0])
            line1 = geometry.LineString([i.coords[0], [x_add, y_add]]);     line1.r = i.r
            line2 = geometry.LineString([[x_add, y_add], i.coords[1]]);     line2.r = i.r
            line3 = geometry.LineString([j.coords[0], [x_add, y_add]]);     line3.r = j.r
            line4 = geometry.LineString([[x_add, y_add], j.coords[1]]);     line4.r = j.r
            lines_added.append([line1, line2, line3, line4])
            lines.append(line1);    lines.append(line2);    lines.append(line3);    lines.append(line4)
            for mm in mored:
                if mm in lines:
                    lines.remove(mm)
    remained_lines = lines
    remrem = clean_rem(remained_lines)
    remrem1 = []
    for i in remrem:
        n_1 = [i.coords[0][0], i.coords[0][1]]
        n_2 = [i.coords[1][0], i.coords[1][1]]
        rr = i.r
        remrem1.append([n_1, n_2, rr])
    return remained_nodes, remained_lines, remrem1, mm, number_nodes_added

def clean_rem(x):
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

def clean_nodes(y):
    removed_nodes = []
    removed_nodes_list = []
    number_removed_nodes = 0
    number_added_nodes = 0
    for i, j in itertools.combinations(y, 2):
        if np.sqrt((i[1]-j[1])**2 + (i[0]-j[0])**2) < 2:
            removed_nodes.append([i, j])
            # removed_nodes.append(j)
            # number_removed_nodes += 1
    # removed_nodes = set(tuple(i) for i in removed_nodes)
    kks = set(tuple(i) for i in list(itertools.chain(*removed_nodes)))
    print('Very close node pairs: %d, Number of unique nodes in all pairs: %d' % (len(removed_nodes), len(kks)))
    C = my_cluster(kks)
    while len(C):
        i = C.pop()
        x_ = mean([j[0] for j in i])
        y_ = mean([j[1] for j in i])
        for ss in i:
            m = [m1 for m1 in y if m1[0]==ss[0] and m1[1]==ss[1]]
            y.remove(m[0])
            removed_nodes_list.append(m[0])
            number_removed_nodes += 1
        y.append([x_, y_, 0, 3, 1, 0])
        number_added_nodes += 1
        # y.remove(i_1);        y.remove(i_2)
        # number_removed_nodes += 2
    return y, removed_nodes_list, number_removed_nodes

def my_cluster(kks):
    coords = [i[:2] for i in kks]
    C = []
    while len(coords):
        locus = coords.pop()
        cluster = [x for x in coords if np.sqrt((locus[1]-x[1])**2 + (locus[0]-x[0])**2) <= 2]
        C.append(cluster + [locus])
        for x in cluster:
            coords.remove(x)
    return C

# update_GS(7, 7, 12, 45, [0, 25], 12.5, 'foldername')
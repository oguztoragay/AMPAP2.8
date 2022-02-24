# from shapely import geometry, ops
# from shapely.geometry import Point
# from shapely.ops import cascaded_union
# import numpy as np
# import itertools
import operator
import pickle
from collections import defaultdict

# def clean_elements(w, h, x):
#     remove = []
#     shapely_l = {}
#     f_name = str('%dx%d_ground.pickle' % (w, h))
#     pickle_in = open(f_name, "rb")
#     sol = pickle.load(pickle_in)
#     Cn = sol[0];    a = sol[1];    u = sol[2];    PML = sol[3];    Nd = sol[5]
#     index_for_in = {k: a[k] for k in Cn.keys() if (a[k] > 0.1)}.keys()
#     for i in x.keys():
#         if i in index_for_in: x[i].optim = 1
#         shapely_l[i] = geometry.LineString(x[i].orientplus)
#         shapely_l[i].angle = np.rad2deg(x[i].theta)
#     print(len(shapely_l))
#     for i, j in itertools.combinations(shapely_l, 2):
#         if shapely_l[i].angle == shapely_l[j].angle and shapely_l[i].intersection(shapely_l[j]).length:
#             if shapely_l[i].within(shapely_l[j]):
#                 remove.append(j)
#             elif shapely_l[j].within(shapely_l[i]):
#                 remove.append(i)
#             # else:  continue
#         if cascaded_union(shapely_l[i].intersection(shapely_l[j])).length > 0.1 and shapely_l[i].angle == shapely_l[j].angle:
#             if shapely_l[i].length > shapely_l[j].length:
#                 remove.append(j)
#             else:
#                 remove.append(i)
#             # remove2 = []
#     # for i, j in itertools.combinations(shapely_l, 2):
#     #     if cascaded_union(shapely_l[i].intersection(shapely_l[j])).length > 0.1 and shapely_l[i].angle == shapely_l[j].angle:
#     #         if shapely_l[i].length > shapely_l[j].length:
#     #             remove2.append(j)
#     #         else:
#     #             remove2.append(i)
#     # remove = remove+remove2
#     x = {k: v for k, v in x.items() if k not in remove}
#     return x
def clean_elements1(w, h):
    remove = []
    shapely_l = {}
    f_name = str('%dx%d_ground.pickle' % (w, h))
    pickle_in = open(f_name, "rb")
    new_ground = pickle.load(pickle_in)
    Nd = new_ground[0]
    PML = new_ground[1]
    poped = 0
    remove_list = []
    for node_ in Nd.keys():
        tip = Nd[node_].tip
        # which = 1 if tip == 3 else 0
        K1 = [i for i in Nd[node_].where if (node_ == PML[i].orient[0])]  # element starts from node_
        K2 = [i for i in Nd[node_].where if (node_ == PML[i].orient[1])]  # element ends in node_
        Kall = [K1, K2]
        for i in range(2):
            K = Kall[i]
            angles = [PML[i].angle for i in K]
            for dup in list_duplicates(angles):
                inha = [K[i] for i in dup]
                mored = {i: PML[i].length for i in inha}
                s_list = list(dict(sorted(mored.items(), key=operator.itemgetter(1), reverse=True)).keys())[:-1]
                for k in s_list:
                    remove_list.append(k)
    remove_list = list(set(remove_list))
    for i in remove_list:
        PML.pop(i)
    return Nd, PML, remove_list
def list_duplicates(seq):
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    return (locs for key, locs in tally.items() if len(locs) > 1)

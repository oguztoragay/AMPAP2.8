import numpy as np
from itertools import chain
from math import gcd, ceil
import operator
def violation(PML, Nd, st, u, vol, a, itr, c_f):
    UCn = dict(filter(lambda elem: elem[1].inn == False and elem[1].okay == 1, PML.items()))  # list of all unchecked potential members in the ground structure
    pro = UCn.keys()
    if itr != 1:
        remain_key = {k: v for k, v in a.items() if (v > 0.1)}.keys()
        remain_nodes_ = [[PML[i].nodei.name, PML[i].nodej.name] for i in remain_key]
        remain_nodes = set(chain.from_iterable(remain_nodes_))
        pro = {k: v for k, v in UCn.items() if (UCn[k].nodei.name in remain_nodes or UCn[k].nodej.name in remain_nodes)}.keys()
    u = sum(u.values(), [])
    new_length = {};    elongation = {};    stress = {};     bunabax = {}
    for i in UCn.keys() & pro:
        dof1 = UCn[i].dof
        dal = [u[j] for j in dof1]  # Displacement values for each member of Unchecked elements list
        new_length[i] = np.sqrt(((dal[3] + UCn[i].nodej.x) - (dal[0] + UCn[i].nodei.x)) ** 2 + ((dal[4] + UCn[i].nodej.y) - (dal[1] + UCn[i].nodei.y)) ** 2)
        elongation[i] = (new_length[i] - UCn[i].length)
        stress[i] = (elongation[i] / UCn[i].length) * 109000
        bunabax[i] = (elongation[i] / UCn[i].length)
    vioCn1 = {k: v for k, v in stress.items() if (v > st or v < -st)}
    vioCn2 = {k: v for k, v in elongation.items() if (v > 0.001 or v < -0.001)}
    vioCn3 = elongation
    vioCn4 = bunabax
    vioCn_abs = {k: abs(v) for k, v in vioCn1.items()}
    vioSort = dict(sorted(vioCn_abs.items(), key=operator.itemgetter(1), reverse=True))
    num = ceil(min(len(vioSort), 0.1*len(PML), 50))
    c_f.write("Iter: %d, violate: %d, selected: %d\n" % (itr, len(vioSort.keys()), num))
    print("Iter: %d, violate: %d, selected: %d" % (itr, len(vioSort.keys()), num))
    for i in range(num):
        PML[list(vioSort.keys())[i]].inn = True
    return num

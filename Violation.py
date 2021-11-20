import numpy as np
from itertools import chain
from math import gcd, ceil
import operator
def violation(PML, Nd, st, u, vol, a, itr, c_f):
    Cn = dict(filter(lambda elem: elem[1].inn == False and elem[1].okay == 1, PML.items()))  # list of all unchecked potential members in the ground structure
    pro = Cn.keys()
    # print(len(pro))
    # print(len(PML))
    # print(len(dict(filter(lambda elem: elem[1].okay == 1, PML.items()))))
    if itr != 1:
        remain_key = {k: v for k, v in a.items() if (v > 0.05)}.keys()
        remain_nodes_ = [[PML[i].nodei.name, PML[i].nodej.name] for i in remain_key]
        remain_nodes = set(chain.from_iterable(remain_nodes_))
        # for i in remain_nodes:
        #     if abs(u[Nd[i].dofs[0]]) < 0.1 and abs(u[Nd[i].dofs[1]]) < 0.1:
        #         remain_nodes.discard(i)
        pro = {k: v for k, v in Cn.items() if (Cn[k].nodei.name in remain_nodes or Cn[k].nodej.name in remain_nodes)}.keys()
    u = sum(u.values(), [])
    y = {};    elongation = {};    stress = {};     bunabax = {}
    for i in Cn.keys() & pro:
        dof1 = Cn[i].dof
        dal = [u[j] for j in dof1]
        y[i] = np.sqrt(((dal[3] + Cn[i].nodej.x) - (dal[0] + Cn[i].nodei.x)) ** 2 + ((dal[4] + Cn[i].nodej.y) - (dal[1] + Cn[i].nodei.y)) ** 2)
        elongation[i] = (y[i] - Cn[i].length)
        stress[i] = (elongation[i] / Cn[i].length) * 109000
        bunabax[i] = (elongation[i] / Cn[i].length)
    vioCn1 = {k: v for k, v in stress.items() if (v > st or v < -st)}
    vioCn2 = {k: v for k, v in elongation.items() if (v > 0.001 or v < -0.001)}
    vioCn3 = elongation
    vioCn4 = bunabax
    vioCn_abs = {k: abs(v) for k, v in vioCn4.items()}
    vioSort = dict(sorted(vioCn_abs.items(), key=operator.itemgetter(1), reverse=True))
    num = ceil(min(len(vioSort), len(vioSort)*0.1, 500))
    c_f.write("Iter: %d, violate: %d, selected: %d\n" % (itr, len(vioSort.keys()), num))
    print("Iter: %d, violate: %d, selected: %d" % (itr, len(vioSort.keys()), num))
    for i in range(num):
        PML[list(vioSort.keys())[i]].inn = True
    return num == 0

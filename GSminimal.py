"""  Modified on June 09 to cover the GS for paper 2"""

import numpy as np
from math import gcd, ceil
import itertools
from scipy.sparse import csr_matrix, csc_matrix
from shapely.geometry import Point, LineString, Polygon
import math
import pickle
import time
dim = 2;    ndof = 3

__all__ = ['Generate', 'Node', 'CElement', 're_Generate']
# --------------------------------------------------------------------------------------
class Generate:  # Ground structure generator
    def __init__(self, wt, ht, fix_nodes, load_nodes, load_values, Wtotal, Htotal, *args):
        mystart = time.time()
        width = Wtotal;     height = Htotal;     PML = []
        poly = Polygon([(0, 0), (width, 0), (width, height), (0, height)])
        convex = True if poly.convex_hull.area == poly.area else False
        xv, yv = np.meshgrid([x * (width / (wt - 1)) for x in range(wt)], [y * (height / (wt - 1)) for y in range(ht)])
        xv = xv.flatten(); yv = yv.flatten()
        Nd = np.vstack((xv, yv, np.arange(len(xv)))).T
        name_iter = -1
        for i, j in itertools.combinations(range(len(Nd)), 2):
            dx, dy = abs(Nd[i][0] - Nd[j][0]), abs(Nd[i][1] - Nd[j][1])
            angle = np.rint(math.degrees(math.atan2(dy, dx)))
            if gcd(int(dx), int(dy)) <= int(width / (wt - 1)):
                if 45 < angle < 90 or 90 < angle < 135 or (angle == 0 and dx <= width / (wt - 1)) or (
                        angle == 90 and dy <= height / (ht - 1)) or (
                        (angle == 45 or angle == 135) and dx <= width / (wt - 1)):
                    seg = [] if convex else LineString([Nd[i], Nd[j]])
                    if convex or poly.contains(seg) or poly.boundary.contains(seg):
                        name_iter += 1
                        PML.append([i, j, np.sqrt(dx ** 2 + dy ** 2), False, name_iter])
        PML = np.array(PML)
        self.nodes = {}  # Dictionary of Node instances to be filled
        self.celements = {}  # Dictionary of continuous Element instances to be filled
        for i in range(len(Nd)):
            if i in load_nodes:
                l_n = 2;                l_v = load_values
            elif i in fix_nodes:
                l_n = 1;                l_v = 0
            elif i > wt*ht:
                l_n = 3;                l_v = 0
            else:
                l_n = 0;                l_v = 0
            self.nodes[i] = Node(i, Nd[i][0], Nd[i][1], l_n, l_v)
            totalnode = len(self.nodes)
        pml = 0
        for i in PML:
            temp_celement = CElement(self.nodes[i[0]], self.nodes[i[1]], totalnode, i[4], 0)
            self.nodes[i[0]].where.append(pml)
            self.nodes[i[1]].where.append(pml)
            self.celements[pml] = temp_celement
            pml += 1
        myfinish = time.time()
        f_name = str('%dx%d_ground.pickle' % (wt, ht))
        pickle_out = open(f_name, "wb")
        pickle.dump([self.nodes, self.celements], pickle_out)
        pickle_out.close()
        mytime = round((myfinish - mystart), 4)
        print('Ground Structure is Generated in %d seconds.' % mytime)
# --------------------------------------------------------------------------------------
class Node:
    def __init__(self, node_name, x, y, tip, load_value):
        self.name = node_name;        self.x = x;        self.y = y
        self.tip = tip;        self.load = load_value
        self.dof = self._dof
        self.where = []
        self.f = self._f
        self.inn = self._inn
        self.coord = (self.x, self.y)
    @property
    def _dof(self):
        s = self.name * ndof
        return [s, s + 1, s + 2]

    @property
    def _f(self):
        if self.tip != 2:
            return [0, 0, 0]
        else:
            return [self.load[0], self.load[1], 0]

    @property
    def _inn(self):
        return True
# --------------------------------------------------------------------------------------
class CElement:
    def __init__(self, nodei, nodej, totalnode, name, li):
        E = 109000
        self.nodei = nodei;        self.nodej = nodej
        self.tip = 0;        self.okay = 1;         self.optim = li
        self.orient = [self.nodei.name, self.nodej.name]
        self.orientplus = [self.nodei.coord, self.nodej.coord]
        self.bounds = [self.nodei.x, self.nodei.y, self.nodej.x, self.nodej.y]
        self.dof = np.concatenate([nodei.dof, nodej.dof], axis=None)
        self.length = self._length;        self.theta = self._theta
        self.cosan = self._cosan;        self.sinan = self._sinan
        ddt = [self.cosan, self.sinan, -self.sinan, self.cosan, 1, self.cosan, self.sinan, -self.sinan, self.cosan, 1]
        rowt = [0, 0, 1, 1, 2, 3, 3, 4, 4, 5]
        colt = [0, 1, 0, 1, 2, 3, 4, 3, 4, 5]
        transform = csc_matrix((ddt, (colt, rowt)), shape=(6, 6))
        dd = [1, 1, 1, 1, 1, 1]
        row = self.dof
        col = [0, 1, 2, 3, 4, 5]
        self.name = name
        b1g = csr_matrix((dd, (row, col)), shape=(totalnode*ndof, 6)).dot(transform.dot(np.array([[-1, 0, 0, 1, 0, 0]]).T))
        b2g = csr_matrix((dd, (row, col)), shape=(totalnode*ndof, 6)).dot(transform.dot(np.array([[0, 2 / self.length, 1, 0, -2 / self.length, 1]]).T))
        b3g = csr_matrix((dd, (row, col)), shape=(totalnode*ndof, 6)).dot(transform.dot(np.array([[0, 0, -1, 0, 0, 1]]).T))
        ke1 = E / self.length
        ke2 = (3 * E) / (4 * np.pi * self.length)
        ke3 = E / (4 * np.pi * self.length)
        self.KE = [ke1, ke2, ke3]
        self.B = csr_matrix([b1g.T.flatten(), b2g.T.flatten(), b3g.T.flatten()])
        self.inn = self._inn

    @property
    def _length(self):
        return np.sqrt((self.nodej.y - self.nodei.y) ** 2 + (self.nodej.x - self.nodei.x) ** 2)

    @property
    def _theta(self):
        return np.arctan2((self.nodej.y - self.nodei.y), (self.nodej.x - self.nodei.x))

    @property
    def _cosan(self):
        return (self.nodej.x - self.nodei.x) / self.length

    @property
    def _sinan(self):
        return (self.nodej.y - self.nodei.y) / self.length

    @property
    def _inn(self):
        return False
# --------------------------------------------------------------------------------------
class re_Generate:  # Ground structure generator after adding the new nodes and removing the ones which are not inside the convex-hull from "GM".
    def __init__(self, wt, ht, fix_nodes, load_nodes, load_values, ff, foldername, remained_nodes, tabu_list, nna):
        mystart1 = time.time()
        PML = []
        # poly = hull
        convex = True #if poly.convex_hull.area == poly.area else False
        # xv, yv = np.meshgrid([x * (width / (wt - 1)) for x in range(wt)], [y * (height / (wt - 1)) for y in range(ht)])
        xv = []; yv = []
        node_names = []
        sss = []
        mored = 0
        while len(remained_nodes):
            temp_list = []
            sss.append(remained_nodes.pop(0))
            for i in sss:
                temp_list.append(i)
                for j in remained_nodes:
                    if np.sqrt((i[0] - j[0])**2 + (i[1] - j[1])**2) < 2:
                        temp_list.append(j)
                        mored += 1
        remained_nodes = sss


        for i in remained_nodes:
            # if i[4]:
            xv.append(i[0])
            yv.append(i[1])
            node_names.append([remained_nodes.index(i), i[3], i[2]])
        # xv = xv.flatten(); yv = yv.flatten()
        name_iter = -1
        Nd = np.vstack((xv, yv, np.arange(len(xv)))).T
        tabu_list = [tabu_list[i].bounds for i in tabu_list.keys()]
        print(tabu_list)
        for i, j in itertools.combinations(range(len(Nd)), 2):
            t_abu = list(np.concatenate([Nd[i][:2], Nd[j][:2]]))
            if t_abu in tabu_list:
                print('... times of tabu', t_abu)
                continue
            else:
                dx, dy = abs(Nd[i][0] - Nd[j][0]), abs(Nd[i][1] - Nd[j][1])
                angle = np.rint(math.degrees(math.atan2(dy, dx)))
                if gcd(int(dx), int(dy)) <= int(10):
                    if 45 < angle < 90 or 90 < angle < 135 or (angle == 0 and dx <= 10) or (angle == 90 and dy <= 10) or \
                            ((angle == 45 or angle == 135) and dx <= 10):
                        seg = [] if convex else LineString([Nd[i], Nd[j]])
                        if convex:#or poly.contains(seg) or poly.boundary.contains(seg)
                            name_iter += 1
                            PML.append([i, j, np.sqrt(dx ** 2 + dy ** 2), False, name_iter])
        PML = np.array(PML)
        remrem2 = {}
        # for i in remrem1:
        #     k1 = [j1[2] for j1 in Nd if i[0][0] == j1[0] and i[0][1] == j1[1]]
        #     k2 = [j2[2] for j2 in Nd if i[1][0] == j2[0] and i[1][1] == j2[1]]
        #     remrem2[k1[0], k2[0]] = i[2]
        self.nodes = {}  # Dictionary of Node instances to be filled
        self.celements = {}  # Dictionary of continuous Element instances to be filled
        for i in range(len(Nd)):
            self.nodes[i] = Node(i, Nd[i][0], Nd[i][1], node_names[i][1], node_names[i][2])
        totalnode = len(self.nodes)
        pml = 0
        for i in PML:
            if (i[0], i[1]) in remrem2:
                kaka = remrem2[(i[0], i[1])]
            else:
                kaka = 0
            temp_celement = CElement(self.nodes[i[0]], self.nodes[i[1]], totalnode, i[4], kaka) #has_key([i[0], i[1]]
            self.nodes[i[0]].where.append(pml)
            self.nodes[i[1]].where.append(pml)
            self.celements[pml] = temp_celement
            pml += 1
        myfinish1 = time.time()
        f_name = str('%dx%d_ground.pickle' % (wt, ht))
        pickle_out = open(f_name, "wb")
        pickle.dump([self.nodes, self.celements], pickle_out)
        pickle_out.close()
        mytime = round((myfinish1 - mystart1), 4)
        print('Ground Structure is Updated in %d seconds.' % mytime)

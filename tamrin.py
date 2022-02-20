import numpy as np
from collections import Counter, OrderedDict
import pickle
import GSminimal as GS
instances = {460: (13, 5, [0, 1, 2], [7], [1, 0])}
for i in instances.keys():
    w, h, fixed, load_node, load_values = instances[i]
    Wtotal = 10 * (instances[i][0] - 1)
    Htotal = 10 * (instances[i][1] - 1)
    GS.Generate(w, h, fixed, load_node, [10,0], Wtotal, Htotal)
    f_name = str('%dx%d_ground.pickle' % (w, h))
    pickle_in = open(f_name, "rb")
    ground1 = pickle.load(pickle_in)
    Nd = ground1[0];    PML = ground1[1];    r_ound = 1;    stop = False
N_= {i:list(Nd[i].coord) for i in Nd.keys()}

NN = ['%f/%f/%i' % (N_[i][0]/10, N_[i][1]/10, i) for i in N_.keys()]
print(NN)
S = [PML[i].orient for i in PML.keys()]
SS = ['%d/%d' % (i[0], i[1]) for i in S]
print(SS)
# for i in S:
#     print(i[0],'/',i[1],',')
kk = np.zeros(w*h)
for j in range(w*h):
    for k in S:
        if k[0] == j:
            kk[j] += 1
# print(sum(kk))
# print(sum(kk)/2)
# for i in range(len(kk)):
#     print(i, ': ', kk[i])
print(sum(kk))
# print(list(Counter(kk).keys())) # equals to list(set(words))
# print(list(Counter(kk).values())) # counts the elements' frequency
# for i in OrderedDict(sorted(Counter(kk).items())):
#     print(int(i), Counter(kk)[i])
# print('tamam')
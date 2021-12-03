import numpy as np
from collections import Counter, OrderedDict
import pickle
instances = {25: (7, 7, [0, 1], [5], [1, 0])}
for i in instances.keys():
    w, h, fixed, load_node, load_values = instances[i]
    f_name = str('%dx%d_ground.pickle' % (w, h))
    pickle_in = open(f_name, "rb")
    ground1 = pickle.load(pickle_in)
    Nd = ground1[0];    PML = ground1[1];    r_ound = 1;    stop = False

S = [PML[i].orient for i in PML.keys()]
kk = np.zeros(w*h)
for j in range(w*h):
    for k in S:
        if k[0] == j or k[1] == j:
            kk[j] += 1
print(sum(kk))
print(sum(kk)/2)
# for i in range(len(kk)):
#     print(i, ': ', kk[i])
# print(list(Counter(kk).keys())) # equals to list(set(words))
# print(list(Counter(kk).values())) # counts the elements' frequency
for i in OrderedDict(sorted(Counter(kk).items())):
    print(int(i), Counter(kk)[i])
# print('tamam')
#### Updated on 01/14/2022
import os
import datetime
import pickle
import GSminimal as GS
from GM25 import evaluate_result
from Frameopt import frameopt
from pdf2gif import make_gif_for_me
# from clean_up27 import *
from DRAW import general_darw

instances = {33:(3, 11, [0,1,2], [31], [1, 0])}
for i in instances.keys():
    Wtotal = 10*(instances[i][0]-1);  Htotal = 10*(instances[i][1]-1);  ll = 1
    w, h, fixed, load_node, load_values = instances[i]
    today = str(datetime.date.today())
    foldername = 'C:/Users/ozt0008/Desktop/rere/' + today + '/meeting/' + str(i) + '/1/'
    if not os.path.isdir(foldername):
        os.makedirs(foldername)
    c_f = open(foldername + 'Output_record ' + str(i) + '.txt', 'w+')
    load_values = [ll*f for f in load_values]  # Magnitude of loads in x and y directions
    ff = max(map(abs, load_values)) /0.5  # Max possible stress
    GS.Generate(w, h, fixed, load_node, load_values, Wtotal, Htotal)  # Generating ground structure and pickle the GS
    f_name = str('%dx%d_ground.pickle' % (w, h))
    pickle_in = open(f_name, "rb")
    ground1 = pickle.load(pickle_in)
    Nd = ground1[0];    PML = ground1[1];    r_ound = 1;    stop = False
    c_f.write('<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>\n')
    c_f.write('0000000000000  (Instance: %d, Load: %d)  0000000000000\n' % (i, ll))
    c_f.write('<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>\n')
    tabu_list = {}
    mm_tabu_list = [0]
    while not stop:  # While loop begins here and continues until stop == True
        step_results = frameopt(Nd, PML, ff, foldername, Wtotal, w, h, c_f, r_ound)
        remained_nodes, nna, mm_tabu, PML, tabu_list = evaluate_result(w, h, tabu_list)
        mm_tabu_list.append(len(tabu_list))
        c_f.write('\n<><><><><><><><><><><><><><><>( Round: %d )<><><><><><><><><><><><><><><>\n' % r_ound)
        c_f.write('<><><><><><><><><><><><><><><>(  Step: 1 )<><><><><><><><><><><><><><><>\n\n')
        if nna != 0:
            r_ound += 1
            GS.re_Generate(w, h, fixed, load_node, load_values, ff, foldername, remained_nodes, tabu_list, nna)
            f_name = str('%dx%d_ground.pickle' % (w, h))
            pickle_in = open(f_name, "rb")
            new_ground = pickle.load(pickle_in)
            Nd = new_ground[0]
            PML = new_ground[1]
        elif nna == 0 and mm_tabu_list[-1] != mm_tabu_list[-2]:  # mm_tabu_list[-2] != mm_tabu_list[-1]
            r_ound += 1
            # GS.re_Generate(w, h, fixed, load_node, load_values, ff, foldername, remained_nodes, tabu_list, nna)
            continue
        else:
            stop = True
            # general_darw(Nd, step_results['Cn'], step_results['a'], step_results['volume'], 0, foldername, 0, 0, 1, 2, w, h)
            print(mm_tabu_list)
            print('This is the end of process')
    c_f.close()
    make_gif_for_me(foldername)

# 3: (3, 3, [0, 2], [7], [0, 1])
# 4: (4, 4, [0, 3], [13], [0, 1])
# 5: (5, 5, [0, 4], [22], [0, 1])
# 7: (7, 7, [0, 6], [45], [0, 1])
# 9: (9, 9, list(range(0, 72, 9)), [44], [0, 1])
# 11: (11, 11, list(range(0, 121, 11)), [65], [0, 1])
# 15: (15, 15, list(range(0, 225, 30)), [104], [0, -1]),
# 15: (15, 15, list(range(0, 15, 2)), [218], [1, 0])
# 15: (15, 15, list(range(0, 61, 30)), [44], [0, -1])
# 25: (25, 25, list(range(0, 625, 100)), [24], [0, -1])
# 25: (25, 25, list(range(0, 25, 6)), [624], [1, 0]),
# 25: (25, 25, list(range(0, 625, 100)), [324], [0, -1])

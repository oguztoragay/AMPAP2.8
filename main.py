import os
import datetime
import GSminimal as GS
from GM25 import evaluate_result
from Frameopt import frameopt
import pickle
from pdf2gif import make_gif_for_me
from clean_up27 import *

instances = {9: (9, 9, [0,9,18,27,36,45,54,63,72], [44], [0, 1])}
for i in instances.keys():
    Wtotal = 10*(instances[i][0]-1);  Htotal = 10*(instances[i][1]-1);  ll = 25
    w, h, fixed, load_node, load_values = instances[i]
    today = str(datetime.date.today())
    foldername = 'C:/Users/ozt0008/Desktop/rere/' + today + str(i) + '/'
    if not os.path.isdir(foldername):
        os.makedirs(foldername)
    c_f = open(foldername + 'Output_record ' + str(i) + '.txt', 'w+')
    load_values = [ll*f for f in load_values]  # Magnitude of loads in x and y directions
    ff = max(map(abs, load_values)) / 2 # Max possible stress
    GS.Generate(w, h, fixed, load_node, load_values, Wtotal, Htotal)  # Generating ground structure and pickle the GS
    f_name = str('%dx%d_ground.pickle' % (w, h))
    pickle_in = open(f_name, "rb")
    ground1 = pickle.load(pickle_in)
    Nd = ground1[0];    PML = ground1[1]
    r_ound = 1;    stop = False
    c_f.write('<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>\n')
    c_f.write('0000000000000  (Instance: %d, Load: %d)  0000000000000\n' % (i, ll))
    c_f.write('<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>\n')
    tabu_list = {}
    while not stop: # While loop begins here and continues until stop == True
        step_results = frameopt(Nd, PML, ff, foldername, Wtotal, w, h, c_f, r_ound)
        remained_nodes, nna, PML, tabu_list = evaluate_result(w, h, r_ound, step_results, tabu_list)
        c_f.write('\n<><><><><><><><><><><><><><><>( Round: %d )<><><><><><><><><><><><><><><>\n' % r_ound)
        c_f.write('<><><><><><><><><><><><><><><>(  Step: 1 )<><><><><><><><><><><><><><><>\n\n')
        # step_results = frameopt(Nd, PML, ff, foldername, Wtotal, w, h, c_f, r_ound) #  Step: 1 in Round: r_ound
        # for i in step_results['PML'].keys(): # to chamge the tabu remove these two lines
        #     step_results['PML'][i].okay = 1 # to chamge the tabu remove these two lines
        # Cn_, Nd_, nna = clean_up(w, h, r_ound, step_results)
        if nna != 0:
            r_ound += 1
            GS.re_Generate(w, h, fixed, load_node, load_values, ff, foldername, remained_nodes, tabu_list, nna)
            f_name = str('%dx%d_ground.pickle' % (w, h))
            pickle_in = open(f_name, "rb")
            new_ground = pickle.load(pickle_in)
            Nd = new_ground[0]
            PML = new_ground[1]
        else:
            stop = True
            # c_f.write('\nNumber of new nodes to be added to the GS: %d\n' % nna)
            # c_f.write('Total final number of nodes in the GS: %d\n' % len(remained_nodes))
            # c_f.write('This is the end of process. Total final weight: %f\n' % round(step1_results['volume'], 4))
            print('This is the end of process')
    c_f.close()
    make_gif_for_me(foldername)


# instances = {2: (3, 3, [0, 2], [7], [0, 1]), 41: (4, 4, [0, 3], [13], [0, 1]), 42: (4, 4, [0, 4, 8, 12], [7], [0, 1]),
#              5: (5, 5, [0, 4], [22], [0, 1]), 7: (7, 7, [0, 6], [45], [0, 1]),
#              11: (11, 11, list(range(0, 121, 11)), [65], [0, 1]),
#              251: (25, 25, list(range(0, 625, 100)), [24], [0, -1]), 252: (25, 25, list(range(0, 25, 6)), [624], [1, 0]),
#              253: (25, 25, list(range(0, 625, 100)), [324], [0, -1])}
# 15: (15, 15, list(range(0, 225, 30)), [104], [0, -1])
# 15: (15, 15, list(range(0, 15, 2)), [218], [1, 0])
#  9: (9, 9, [0,9,18,27,36,45,54,63,72], [44], [0, 1])
# shomarehashun avaz mishe vasate 2 ta round uno dorost kon
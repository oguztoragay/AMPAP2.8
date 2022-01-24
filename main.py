#### Updated on 01/14/2022 for various horizontal and vertical node numbers
import os
import datetime
import pickle
import GSminimal as GS
from GM26 import evaluate_result
from Frameopt import frameopt
from pdf2gif import make_gif_for_me
from DRAW import general_darw

instances = {210: (3, 7, [0, 1, 2], [18], [1, 0])}

for i in instances.keys():
    Wtotal = 10*(instances[i][0]-1);  Htotal = 10*(instances[i][1]-1);  ll = 30  # ll:Load magnitude
    w, h, fixed, load_node, load_values = instances[i]
    today = str(datetime.date.today())
    foldername = 'C:/Users/ozt0008/Desktop/rere/' + today + '/toplanti/' + str(i) + '/19/'
    if not os.path.isdir(foldername):
        os.makedirs(foldername)
    c_f = open(foldername + 'Output_record ' + str(i) + '.txt', 'w+')
    load_values = [ll*f for f in load_values]  # Load magnitude in x and y directions
    ff = max(map(abs, load_values)) / 100  # Max possible stress
    # -------- Generating the ground structure from which the base GS will be selected ----------
    GS.Generate(w, h, fixed, load_node, load_values, Wtotal, Htotal)
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
        step_results, vio = frameopt(Nd, PML, ff, foldername, Wtotal, w, h, c_f, r_ound)
        remained_nodes, nna = evaluate_result(w, h, r_ound)
        # mm_tabu_list.append(len(tabu_list))
        print('\n<><><><><><><><><><><><><><><>( Round: %d )<><><><><><><><><><><><><><><>\n' % r_ound)
        c_f.write('\n<><><><><><><><><><><><><><><>( Round: %d )<><><><><><><><><><><><><><><>\n\n' % r_ound)
        if nna != 0:
            print('------------------------------------------------  ', nna)
            r_ound += 1
            GS.re_Generate(w, h, fixed, load_node, load_values, ff, foldername, remained_nodes, tabu_list, nna)
            f_name = str('%dx%d_ground.pickle' % (w, h))
            pickle_in = open(f_name, "rb")
            new_ground = pickle.load(pickle_in)
            Nd = new_ground[0]
            PML = new_ground[1]
        else:
            stop = True
            print('This is the end of process')
    c_f.close()
    make_gif_for_me(foldername)

# 3: (3, 3, [0, 2], [7], [0, 1])
# 4: (4, 4, [0, 3], [13], [0, 1])
# 5: (5, 5, [0, 4], [22], [0, 1])
# 7: (7, 7, [0, 6], [45], [0, 1])
# 9: (9, 9, list(range(0, 72, 9)), [44], [0, 1])
# 9: (9, 9, list(range(0, 9, 1)), [76], [1, 0])
# 11: (11, 11, list(range(0, 121, 11)), [65], [0, 1])
# 15: (15, 15, list(range(0, 225, 30)), [104], [0, -1]),
# 15: (15, 15, list(range(0, 15, 2)), [218], [1, 0])
# 15: (15, 15, list(range(0, 61, 30)), [44], [0, -1])
# 25: (25, 25, list(range(0, 625, 100)), [24], [0, -1])
# 25: (25, 25, list(range(0, 25, 6)), [624], [1, 0]),
# 25: (25, 25, list(range(0, 625, 100)), [324], [0, -1])
# -------------------------------------------------------
# 21: (3, 7, [0, 1, 2], [19], [1, 0])
# 45: (5, 9, [0, 1, 3, 4], [42], [1, 0])
# 77: (7, 11, [0, 1, 5, 6], [73], [1, 0])
# 140: (7, 20, [0, 1, 2, 3, 4, 5, 6], [136], [0, 1])

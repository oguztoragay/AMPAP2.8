#### Updated on 01/14/2022 for various horizontal and vertical node numbers
import os
import datetime
import pickle
import time

import GSminimal as GS
from GM26 import evaluate_result
from Frameopt import frameopt
from pdf2gif import make_gif_for_me
import numpy as np
import functools
import operator
from clean_elements import clean_elements1
from DRAW import general_darw
# -------------------------------------------------------------------
instances = {9: (3, 3, [0, 2], [7], [0, 1])}
load_magnit = [100] #list(range(100, 401, 20))
# -------------------------------------------------------------------
for ins in instances.keys():
    results_data = {}
    for l in load_magnit:
        if ins < 45: Wtotal = 50; Htotal = 50
        else:
            Wtotal = 40 #10*(instances[ins][0]-1)
            Htotal = 80 #10*(instances[ins][1]-1)
        ll = l # ll:Load magnitude 25
        w, h, fixed, load_node, load_values = instances[ins]
        today = str(datetime.date.today())
        foldername = 'C:/Users/oguzt/Desktop/rere/Experiments/' + today + '/' + str(ins) + '/' + str(l) + '/'
        if not os.path.isdir(foldername):
            os.makedirs(foldername)
        c_f = open(foldername + 'Output_record ' + str(ins) + '.txt', 'w+')
        c_f2 = open('C:/Users/oguzt/Desktop/rere/Experiments/' + today + '/' + str(ins) + '/' + 'Total_output_record' + str(ins)+'.txt', 'w+')
        load_values = [ll*f for f in load_values]  # Load magnitude in x and y directions
        ff = max(map(abs, load_values)) / 1  # Max possible stress
    # -------- Generating the ground structure from which the base GS will be selected ----------
        run_1 = time.time()
        GS.Generate(w, h, fixed, load_node, load_values, Wtotal, Htotal)
        f_name = str('%dx%d_ground.pickle' % (w, h))
        pickle_in = open(f_name, "rb")
        ground1 = pickle.load(pickle_in)
        Nd = ground1[0];    PML = ground1[1];    r_ound = 1;    stop = False
        c_f.write('<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>\n')
        c_f.write('0000000000000  (Instance: %d, Load: %d)  0000000000000\n' % (ins, ll))
        c_f.write('<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>\n')
        tabu_list = {}
        mm_tabu_list = [0]
        hazf = []
        while not stop:  # While loop begins here and continues until stop == True
            step_results, vio = frameopt(Nd, PML, ff, foldername, Wtotal, w, h, c_f, r_ound, hazf)
            remained_nodes, nna = evaluate_result(w, h, r_ound)
            print('\n<><><><><><><><><><><><><><><>( Round: %d )<><><><><><><><><><><><><><><>\n' % r_ound)
            c_f.write('\n<><><><><><><><><><><><><><><>( Round: %d )<><><><><><><><><><><><><><><>\n\n' % r_ound)
            if nna != 0:
                print('------------------------------------------------  ', nna)
                r_ound += 1
                GS.re_Generate(w, h, fixed, load_node, load_values, ff, foldername, remained_nodes, tabu_list, nna, Wtotal, Htotal)
                Nd, PML, hazf = clean_elements1(w, h)
            else:
                stop = True
                c_f.write('<><><><><><><><><><><><><><>< Results Report ><><><><><><><><><><><><><><>\n')
                c_f.write('\n<><><><><><><><><><><><><><>< Nodes Report ><><><><><><><><><><><><><><><>\n')
                for i in Nd.keys():
                    x, y = [round(i, 2) for i in Nd[i].coord]
                    xdir, ydir, rot = [round(i, 3) for i in step_results['u'][i]]
                    c_f.write('Node: %d \t X: %s \t Y: %s \t XDis: %s \t\t YDis: %s \t\t Rotat: %s \n' % (i, x, y, xdir, ydir, rot))
                run_time = time.time() - run_1
                results_data[l] = [run_time, step_results['volume']]
                new_length = {}
                c_f.write('\n<><><><><><><><><><><><><><>< Elements Report ><><><><><><><><><><><><><><>\n')
                for i in step_results['a'].keys():
                    if step_results['a'][i] > 0.05:
                        orient = step_results['PML'][i].orient
                        dal = [step_results['u'][j] for j in orient]
                        dal = functools.reduce(operator.iconcat, dal, [])
                        new_length[i] = np.sqrt(((dal[3] + step_results['PML'][i].nodej.x) - (dal[0] + step_results['PML'][i].nodei.x)) ** 2 + ((dal[4] + step_results['PML'][i].nodej.y) - (dal[1] + step_results['PML'][i].nodei.y)) ** 2)
                        stress = ((new_length[i] - step_results['PML'][i].length) / step_results['PML'][i].length) * 109000
                        c_f.write('Element: %d \t Orient: %s \t CS: %s \t stress: %s \n' % (i, orient, round(step_results['a'][i], 4), round(stress, 4)))
                general_darw(step_results['Nd'], step_results['Cn'], step_results['a'], step_results['volume'], 0, foldername, 0, 0, 1, 3, w, h, l)
        c_f2.write('Load Mag: \t Sol_time: \t Weight: \n')
        for i in results_data.keys():
            c_f2.write('%d \t %s \t %s \n' % (i, results_data[i][0], results_data[i][1]))
        c_f2.close()
        c_f.close()
        make_gif_for_me(foldername)

# ------------------- Experiments for the paper:
# 9: (3, 3, [0, 2], [7], [0, 1]) # don't forget to check the size
# 16: (4, 4, [0, 3], [14], [0, 1]) # don't forget to check the size
# 25: (5, 5, [0, 4], [22], [0, 1]) # don't forget to check the size
# 450: (5, 9, [1, 3], [42], [1, 0]) # Coarse
# 451: (9, 17, [2, 6], [148], [1, 0]) # Normal
# 452: (17, 33, [4, 12], [552], [1, 0]) # Fine
# 650: (13, 5, [0, 12], [4, 8], [0, -1]) # horizontal bridge
# 651: (5, 13, [0, 60], [20, 40], [-1, 0]) # vertical bridge

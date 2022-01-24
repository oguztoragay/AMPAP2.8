import numpy as np
from DRAW import Draw_GROUND_dashed, Draw_mod, general_darw
from NLP import nlp
from Violation import violation
import pickle
import itertools

def frameopt(Nd, PML, st, foldername, Wtotal, wt, ht, c_f, r_ound):
    index_for_in = {k: v for k, v in PML.items() if (v.length <= (Wtotal / (wt - 1)) * (np.sqrt(2)) and v.okay)}.keys() # minimal GS is chosen here (only neighbur nodes)
    if r_ound == 1:
        for p in index_for_in:
            PML[p].inn = True
    if r_ound > 1:
        f_name = str('%dx%d_results.pickle' % (wt, ht))
        pickle_in_update = open(f_name, "rb")
        picpic = pickle.load(pickle_in_update)
        gs_past = picpic[0]
        gs_past_bounds = [gs_past[i].bounds for i in gs_past.keys()]
        gs_past_bounds_set = set(map(tuple, gs_past_bounds))
        PML_modified_bounds = [PML[i].bounds for i in PML.keys()]
        PML_modified_bounds_set = set(map(tuple, PML_modified_bounds))
        PML_modified = {tuple(PML[d].bounds): PML[d] for d in PML.keys()}
        remained_ground_bound = PML_modified_bounds_set & gs_past_bounds_set
        for p in remained_ground_bound:
            PML_modified[p].inn = True
        PML_additional = []
        new_added_nodes = {x1: x2 for x1, x2 in Nd.items() if (Nd[x1].tip == 3)}.keys()
        for new_nd in new_added_nodes:
            ori_ = Nd[new_nd].coord
            for i in PML_modified.keys():
                if (ori_ == (i[0], i[1]) or ori_ == (i[2], i[3])):  # and PML_modified[i].length < 20
                    PML_modified[i].inn = True
        PML = {int(PML_modified[d].name): PML_modified[d] for d in PML_modified.keys()}
        volume_ = picpic[4]
    general_darw(Nd, PML, [], 0, 0,  foldername, 0, 0, 0, 1, wt, ht)
    volume = [100000]
    results_key = ['volume', 'a', 'u', 'Cn', 'Nd', 'PML']
    step1_results = dict.fromkeys(results_key)
    for itr in range(1, 50):
        Cn = dict(filter(lambda elem: elem[1].inn == True, PML.items()))
        print('Total elements in PML: %d, Itr: %d, selected elements: %d' % (len(PML.keys()), itr, len(Cn)))
        c_f.write('\nTotal elements in GS: %d, Itr: %d, Elements in reduced GS: %d' % (len(PML.keys()), itr, len(Cn)))
        vol, a, u, data1, timer = nlp(Nd, Cn, st, 'ipopt')
        # if vol < volume[-1]:
        step1_results.update({'volume': vol, 'a': a, 'u': u, 'Cn': Cn, 'Nd': Nd, 'PML': PML})
        c_f.write("\nModel generation total time: %f\n" % round(timer.timers['all'].total_time, 3))
        volume.append(vol)
        c_f.write("---> Total mems: %d, Itr: %d, mems: %d, vol: %f, time:%f, condition:%s\n" % (len(PML.keys()), itr, len(Cn), vol, np.round(data1['Time'], 3), data1['Term_con']))
        print("Total mems: %d, Itr: %d, mems: %d, vol: %f, time:%f, condition:%s\n" % (len(PML.keys()), itr, len(Cn), vol, np.round(data1['Time'], 3), data1['Term_con']))
        general_darw(Nd, Cn, a, vol, data1['Time'], foldername, itr, r_ound, 1, 2, wt, ht)
        if abs(volume[-1]-volume[-2]) < 0.001*volume[-2]:
            c_f.write("Termination condition: %s\n" % 'No more reduction in the volume.')
            print('from condition 1');  break
        vio_check = violation(PML, Nd, st, u, vol, a, itr, c_f)
        if vio_check == 0:
            c_f.write("Termination condition: %s\n" % 'No violating potential memeber.')
            print('from condition 2');  break
    f_name = str('%dx%d_results.pickle' % (wt, ht))
    pickle_out = open(f_name, "wb")
    pickle.dump([step1_results['Cn'], step1_results['a'], step1_results['u'], step1_results['PML'], step1_results['volume'], step1_results['Nd']], pickle_out)
    pickle_out.close()
    return step1_results, vio_check

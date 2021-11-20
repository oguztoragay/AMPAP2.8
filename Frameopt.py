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
        # picpic_modified = {tuple(gs_past[d].bounds): gs_past[d] for d in gs_past.keys()}
        # picpic_modified_key_list = [i for i in picpic_modified.keys()]


        PML_modified_bounds = [PML[i].bounds for i in PML.keys()]
        PML_modified_bounds_set = set(map(tuple, PML_modified_bounds))


        PML_modified = {tuple(PML[d].bounds): PML[d] for d in PML.keys()}
        # PML_modified_key_list = [i for i in PML_modified.keys()]
        # hala = PML_modified_bounds_set.symmetric_difference(gs_past_bounds_set)
        # ssss = len(hala)
        # remained_from_prev = set(picpic_modified_key_list) & set(PML_modified_key_list)
        # remained_from_prev = set(map(tuple, gs_past_bounds)) & set(map(tuple, PML_modified_bounds))
        # my_list = [ii for ii in picpic_modified_key_list for jj in PML_modified_key_list if ((ii[0]==jj[0]) and (ii[1]==jj[1]) and (ii[2]==jj[2]) and (ii[3]==jj[3]))]
        remained_ground_bound = PML_modified_bounds_set & gs_past_bounds_set
        for p in remained_ground_bound:
            PML_modified[p].inn = True
        PML_additional = []
        new_added_nodes = {x1: x2 for x1, x2 in Nd.items() if (Nd[x1].tip == 3)}.keys()
        for new_nd in new_added_nodes:
            ori_ = Nd[new_nd].coord
            for i in PML_modified.keys():
                if ori_ == (i[0], i[1]) or ori_ == (i[2], i[3]):
                    PML_modified[i].inn = True
        PML = {int(PML_modified[d].name): PML_modified[d] for d in PML_modified.keys()}
        volume_ = picpic[4]
    general_darw(Nd, PML, [], 0, 0,  foldername, 0, 0, 0, 1)
    volume = [100000]
    results_key = ['volume', 'a', 'u', 'Cn', 'Nd', 'PML']
    step1_results = dict.fromkeys(results_key)
    for itr in range(1, 10):
        Cn = dict(filter(lambda elem: elem[1].inn == True, PML.items()))
        print('Total mems: %d, Itr: %d, mems: %d' % (len(PML.keys()), itr, len(Cn)))
        c_f.write('\nTotal mems in GS: %d, Itr: %d, mems in reduced GS: %d' % (len(PML.keys()), itr, len(Cn)))
        vol, a, u, data1, timer = nlp(Nd, Cn, st, 'ipopt')
        if vol < volume[-1]:
            step1_results.update({'volume': vol, 'a': a, 'u': u, 'Cn': Cn, 'Nd': Nd, 'PML': PML})
        c_f.write("\nModel generation total time: %f\n" % round(timer.timers['all'].total_time, 3))
        volume.append(vol)
        c_f.write("---> Total mems: %d, Itr: %d, mems: %d, vol: %f, time:%f, condition:%s\n" % (len(PML.keys()), itr, len(Cn), vol, np.round(data1['Time'], 3), data1['Term_con']))
        print("Total mems: %d, Itr: %d, mems: %d, vol: %f, time:%f, condition:%s\n" % (len(PML.keys()), itr, len(Cn), vol, np.round(data1['Time'], 3), data1['Term_con']))
        general_darw(Nd, Cn, a, vol, data1['Time'], foldername, itr, r_ound, 1, 2)
        if abs(volume[-1]-volume[-2]) < 0.001*volume[-2]:
            c_f.write("Termination condition: %s\n" % 'No more reduction in the volume.')
            print('az 1');  break
        if violation(PML, Nd, st, u, vol, a, itr, c_f):
            c_f.write("Termination condition: %s\n" % 'No violating potential memeber.')
            print('az 2');  break
    f_name = str('%dx%d_results.pickle' % (wt, ht))
    pickle_out = open(f_name, "wb")
    pickle.dump([step1_results['Cn'], step1_results['a'], step1_results['u'], step1_results['PML'], step1_results['volume']], pickle_out)
    pickle_out.close()
    return step1_results

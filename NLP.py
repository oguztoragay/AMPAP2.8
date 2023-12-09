# 01/27/2021
# 06/22/2021 Modified for the second paper
# 11/17/2021 Bonmin option added to the code
import os
os.environ['PARDISOLICMESSAGE'] = '1'
os.environ['OMP_NUM_THREADS'] = '24'
import numpy as np
import pyomo.environ
from pyomo.environ import *
import itertools
from pyomo import environ as pym
from shapely.geometry import LineString
from pyomo.opt import SolverFactory
from pyomo.opt import SolverManagerFactory
from pyomo.util.infeasible import log_infeasible_constraints
import pandas as pd
import time
from pyomo.common.timing import HierarchicalTimer
import os

def nlp(Nd, Cn, smax, solver_name):
    E = 109000;    dmax = 0.095;    r2_set = [0.2, 0.3, 0.5]
    timer = HierarchicalTimer()
    timer.start('all')
    boundary = set(dict(filter(lambda elem: elem[1].tip == 1, Nd.items())).keys())
    nfree = set(np.concatenate([Nd[i].dof for i in boundary]))
    load_node = set(dict(filter(lambda elem: elem[1].tip == 2, Nd.items())).keys())
    load_node_dof = [Nd[i].dof for i in load_node]
    load_value = [Nd[i].load for i in load_node]
    f = np.ravel([Nd[i].f for i in Nd.keys()])
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    m = ConcreteModel()
    m.LN = set(Nd.keys())
    m.LE = set(Cn.keys())
    m.dofs = set(np.ravel([Nd[i].dof for i in Nd.keys()]))
    m.nfree = nfree & m.dofs
    m.free = m.dofs - m.nfree
    m.E = E;    m.dmax = dmax;    m.amin = np.pi * (r2_set[0] ** 2);    m.amax = np.pi * (r2_set[2] ** 2);    m.Smax = smax
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def lerule(m, i):
        return Cn[i].length
    m.d = Var(m.dofs, initialize=0, bounds=(-m.dmax, m.dmax))
    for i in m.nfree:
        m.d[i].fix(0)
    m.a = Var(m.LE, bounds=(0, m.amax), initialize=m.amax)
    m.le = Param(m.LE, rule=lerule)
    m.M = Param(initialize=1000000)
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # os.environ['NEOS_EMAIL'] = 'ozt0008@auburn.edu'
    def obj_rule(m):
        return sum(m.a[i] * m.le[i] for i in m.LE)
    m.z = Objective(rule=obj_rule, sense=minimize)
    # -------------------------------------------------------------CONSTRAINTS---------------------------------------------------------------------------
    timer.start('Cons1')
    m.cons1 = ConstraintList()
    for satr in m.free:
        m.ps = set(Nd[np.floor(satr / 3)].where) & m.LE
        temp1 = 0
        for i in m.ps:
            b_one = Cn[i].B[0].toarray().flatten();            b_one_index = np.asarray(b_one.nonzero()).flatten()
            b_two = Cn[i].B[1].toarray().flatten();            b_two_index = np.asarray(b_two.nonzero()).flatten()
            b_thr = Cn[i].B[2].toarray().flatten();            b_thr_index = np.asarray(b_thr.nonzero()).flatten()
            temp1 += (Cn[i].KE[0] * m.a[i] ** 1) * (b_one[satr] * sum(b_one[di0] * m.d[di0] for di0 in b_one_index)) + \
                     (Cn[i].KE[1] * m.a[i] ** 2) * (b_two[satr] * sum(b_two[di1] * m.d[di1] for di1 in b_two_index)) + \
                     (Cn[i].KE[2] * m.a[i] ** 2) * (b_thr[satr] * sum(b_thr[di2] * m.d[di2] for di2 in b_thr_index))
        m.cons1.add(temp1 - f[satr] == 0)
    timer.stop('Cons1')
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    timer.start('Cons2')
    m.cons2 = ConstraintList()
    for i in m.LE:
        dofz = Cn[i].dof
        d_list = [m.d[i] for i in dofz]
        lenprime = (((d_list[3] + Cn[i].nodej.x) - (d_list[0] + Cn[i].nodei.x)) ** 2 + (
            (d_list[4] + Cn[i].nodej.y) - (d_list[1] + Cn[i].nodei.y)) ** 2)**0.5
        # strain = (lenprime**0.5 - Cn[i].length) / Cn[i].length
        # m.cons2.add((strain*m.E) - smax <= 0)
        # m.cons2.add((strain*m.E) + smax >= 0)
        m.cons2.add(lenprime - Cn[i].length <= 0.2 * Cn[i].length)
        m.cons2.add(lenprime - Cn[i].length >= -0.2 * Cn[i].length)
    timer.stop('Cons2')
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # timer.start('Cons3')
    # m.cons3 = Constraint(expr=m.z <= limit)
    # timer.stop('Cons3')
    # # --------------------------------------------------------------------------------------------------------------------------------------------------
    timer.start('Cons4')
    m.cons4 = ConstraintList()
    for i in m.free:
        m.cons4.add(m.d[i] - dmax <= 0)
        m.cons4.add(m.d[i] + dmax >= 0)
    timer.stop('Cons4')
    # # --------------------------------------------------------------------------------------------------------------------------------------------------
    timer.start('Cons7')
    m.cons7 = ConstraintList()
    for i, j in itertools.combinations(m.LE, 2):
        seg1 = LineString([[Cn[i].nodei.x, Cn[i].nodei.y], [Cn[i].nodej.x, Cn[i].nodej.y]])
        seg2 = LineString([[Cn[j].nodei.x, Cn[j].nodei.y], [Cn[j].nodej.x, Cn[j].nodej.y]])
        int_pt = seg1.intersects(seg2)
        toucher = seg1.touches(seg2)
        if int_pt == True and toucher == False:
            m.cons7.add(m.a[i] * m.a[j] <= 0)
        else:
            Constraint.Skip
    timer.stop('Cons7')
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # timer.start('importing')
    # # Ipopt bound multipliers (obtained from solution)
    # m.ipopt_zL_out = Suffix(direction=Suffix.IMPORT)
    # m.ipopt_zU_out = Suffix(direction=Suffix.IMPORT)
    # # Ipopt bound multipliers (sent to solver)
    # m.ipopt_zL_in = Suffix(direction=Suffix.EXPORT)
    # m.ipopt_zU_in = Suffix(direction=Suffix.EXPORT)
    # # Obtain dual solutions from first solve and send to warm start
    # m.dual = Suffix(direction=Suffix.IMPORT_EXPORT)
    # timer.stop('importing')
    timer.stop('all')
    # print(timer)

    # # --------------------------------------------------------------------------------------------------------------------------------------------------
    # solver = SolverFactory('bonmin', executable='C:/Users/ozt0008/Desktop/CoinAll-1.6.0-win64-intel11.1/CoinAll-1.6.0-win64-intel11.1/bin/bonmin.exe', tee=True)
    # solver = SolverFactory(solver_name, executable='C:/Program Files/Ipopt/bin/ipopt.exe', tee=False)
    solver = SolverFactory('ipopt', tee=True)
    solver.options['constr_viol_tol'] = 1e-6
    solver.options['tol'] = 1e-6 #10**-(itr+2)
    solver.options['acceptable_tol'] = 1e-6
    solver.options['acceptable_iter'] = 10
    # solver.options['linear_solver'] = 'pardiso'
    solver.options['max_iter'] = 10000
    solver.options['obj_scaling_factor'] = 0.1
    solver.options['print_level'] = 0
    # solver.options['print_user_options'] = 'yes'
    # solver.options['print_advanced_options'] = 'yes'
    solver.options['nlp_scaling_method'] = 'gradient-based'
    # if itr > 1:
    #     m.ipopt_zL_in.update(m.ipopt_zL_out)
    #     m.ipopt_zU_in.update(m.ipopt_zU_out)
    # solver.options['warm_start_init_point'] = 'yes'
    # solver.options['warm_start_bound_push'] = 1e-6
    # solver.options['warm_start_mult_bound_push'] = 1e-6
    # solver.options['mu_init'] = 1e-6
    # solver.options['warm_start_entire_iterate'] = 'yes'
    # solver.options['mu_strategy'] = 'adaptive'
    # solver.options['mu_oracle'] = 'loqo'
    # solver.options['adaptive_mu_globalization'] = 'obj-constr-filter'
    # solver.options['line_search_method '] = 'cg-penalty'
    solver.options['print_frequency_iter'] = 100
    solver.options['least_square_init_primal'] = 'yes'
    solver.options['least_square_init_duals'] = 'yes'
    # NLPstart = time.time()
    solution = solver.solve(m, tee=False, keepfiles=True)
    # m.ipopt_zL_out = Suffix(direction=Suffix.IMPORT)
    # m.ipopt_zU_out = Suffix(direction=Suffix.IMPORT)
    # TNLP = np.round(time.time()-NLPstart, 3)
    # data1_nlp = solution.Problem._list
    data1_nlp = {}
    data1_nlp['Time'] = solution.solver[0]['Time']
    print("Time: %f, Termination: %s, Obj. Value: %f" % (np.round(solution.solver[0]['Time'], 4), solution.solver[0]['Termination condition'], value(m.z)))
    data1_nlp['Term_con'] = solution.solver[0]['Termination condition']
    # log_infeasible_constraints(m)
    weight = value(m.z)
    print('\n ************** NLP is done with status "{}"! Weight is "{}" and solver is "{}"**************.'.format(
            solution.solver.termination_condition, np.round(weight, 4), 'Ipopt + pardiso'))
    Y = {}
    for i in m.LE:
        Y[i] = m.a[i].value
    # print('-------------------------------------------( NODES )-------------------------------------------')
    toprint2 = pd.DataFrame(index=Nd.keys(), columns=['y', 'U1', 'U2', 'UR3'])
    dis = {}
    for i in Nd.keys():
        dofz = Nd[i].dof
        dis[i] = [m.d[dofz[0]].value, m.d[dofz[1]].value, m.d[dofz[2]].value]
        toprint2.loc[i] = [1, dis[i][0], dis[i][1], dis[i][2]]
    # print(toprint2)
    return weight, Y, dis, data1_nlp, timer

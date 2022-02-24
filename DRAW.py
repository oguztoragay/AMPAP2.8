import matplotlib.pyplot as plt
import matplotlib.colors as colors
import networkx as nx
import numpy as np
from My_count import count

@count
def general_darw(nodes, celements, X, volume, t_ime, foldername, itr, r_ound, s_tep, which_one, wt, ht, u):
    ss = str(general_darw.counter)
    draw_number = ss.zfill(5)
    size_ = (wt, ht)
    a0 = 0
    if which_one == 1:
        Draw_GROUND_dashed(nodes, celements, foldername, draw_number, size_, a0)
    elif which_one == 2:
        Draw_mod(nodes, celements, X, volume, t_ime, foldername, itr, r_ound, s_tep, draw_number, size_, u)
    else:
        Draw_mod_final(nodes, celements, X, volume, t_ime, foldername, itr, r_ound, s_tep, draw_number, size_, u)

def Draw_GROUND_dashed(nodes, elements, foldername, draw_number, size_, a0):
    fig, ax = plt.subplots(figsize=size_)
    G = nx.Graph()
    pos = {}
    node_names = {}
    node_colors = []
    for i in nodes.keys():
        G.add_node(i)
        pos.update({i: [nodes[i].x, nodes[i].y]})
        node_names.update({i: nodes[i].name})
        if nodes[i].tip == 1:  # boundary
            node_colors.append('b')
        elif nodes[i].tip == 2:  # load node
            if nodes[i].load[1] > 0 or nodes[i].load[0] > 0:
                node_colors.append('g')
                x_load = nodes[i].x
                y_load = nodes[i].y
            else:
                node_colors.append('r')
                x_load = nodes[i].x
                y_load = nodes[i].y
        elif nodes[i].tip == 3:  # added nodes
            node_colors.append('lime')
        else:
            node_colors.append('k')
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=1, node_size=25, node_shape='o', linewidths=0)
    for i in elements.keys():
        i_pos1 = elements[i].nodei.name
        i_pos2 = elements[i].nodej.name
        if elements[i].inn == True:  G.add_edge(i_pos1, i_pos2)
    nx.draw_networkx_edges(G, pos, edge_color='lightgrey', width=1, ax=ax, style='solid')
    plt.axis('off')
    plt.suptitle(draw_number + ' - GS', fontsize=10)
    plt.show()
    png_name = draw_number
    fig.savefig(str(foldername + '/' + draw_number + '.pdf'), bbox_inches='tight')
    fig.savefig(str(foldername + '/' + png_name + '.png'))

def Draw_mod(nodes, celements, X, volume, t_ime, foldername, itr, r_ound, s_tep, draw_number, size_, u):
    X_dic = [i for i, k in X.items() if k > 0.05]
    nodeset1 = []
    nodeset2 = []
    for i in X_dic:
        nodeset1.append(celements[float(i)].nodei.name)
        nodeset2.append(celements[float(i)].nodej.name)
    sts = {}
    for i in X_dic:
        nodes_ = [celements[float(i)].nodei.name, celements[float(i)].nodej.name]
        dal = [u[j] for j in nodes_]
        dal = [item for sublist in dal for item in sublist] # Displacement values for each member of Unchecked elements list
        sts[i] = ((np.sqrt(((dal[3] + celements[i].nodej.x) - (dal[0] + celements[i].nodei.x)) ** 2 + ((dal[4] + celements[i].nodej.y) - (dal[1] + celements[i].nodei.y)) ** 2) - celements[i].length))/celements[i].length
    node_list = list(set(nodeset1) | set(nodeset2))
    ## Drawing the Nodes ----------------------------
    fig, ax = plt.subplots(figsize=size_)
    G = nx.Graph()
    pos = {}
    node_names = {}
    node_colors = []
    for i in nodes.keys():
        G.add_node(i)
        pos.update({i: [nodes[i].x, nodes[i].y]})
        node_names.update({i: nodes[i].name})
        if nodes[i].tip == 1:  # boundary
            node_colors.append('b')
        elif nodes[i].tip == 2:  # load point
            if max(nodes[i].load) > 0: node_colors.append('g')
            else: node_colors.append('r')
        elif nodes[i].tip == 3:  # added nodes
            node_colors.append('lime')
        else:
            if i in node_list: node_colors.append('k')
            else: node_colors.append('lightgrey')
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=1, node_size=5, node_shape='o', linewidths=0)
    nx.draw_networkx_labels(G, pos, node_names)
    ## Drawing the Edges ----------------------------
    edge_w = {}
    edge_c = {}
    shum = 0
    for i in celements.keys():
        if i in X_dic and X[i] > 0:
            shum += 1
            i_pos1 = celements[i].nodei.name
            i_pos2 = celements[i].nodej.name
            G.add_edge(i_pos1, i_pos2)
            edge_w.update({(i_pos1, i_pos2): 5 * X[i]})
            if sts[i] > 0:
                edge_c.update({(i_pos1, i_pos2): 'b'})
            elif sts[i] < 0:
                edge_c.update({(i_pos1, i_pos2): 'r'})
        else:
            i_pos1 = celements[i].nodei.name
            i_pos2 = celements[i].nodej.name
            G.add_edge(i_pos1, i_pos2)
            edge_w.update({(i_pos1, i_pos2): 0})
            edge_c.update({(i_pos1, i_pos2): 'lightgrey'})
    edge_c = list(edge_c.values())
    edge_w = list(edge_w.values())
    nx.draw_networkx_edges(G, pos, edge_color=edge_c, width=edge_w, ax=ax, alpha=1)
    # print('shum is:', shum)
    plt.axis('off')
    plt.suptitle('|ST:' + str(round(t_ime, 4)) + '|W:' + str(round(volume, 4)) + '|R:' + str(r_ound) + '|S:' + str(s_tep) + '|I:' + str(itr), fontsize=10)
    plt.show()
    png_name = draw_number
    fig.savefig(str(foldername + '/' + png_name + '.pdf'), bbox_inches='tight')
    fig.savefig(str(foldername + '/' + png_name + '.png'))

def Draw_mod_final(nodes, celements, X, volume, t_ime, foldername, itr, r_ound, s_tep, draw_number, size_, u):
    X_dic = [i for i, k in X.items() if k > 0.01]
    nodeset1 = []
    nodeset2 = []
    for i in X_dic:
        nodeset1.append(celements[float(i)].nodei.name)
        nodeset2.append(celements[float(i)].nodej.name)
    node_list = list(set(nodeset1) | set(nodeset2))
    ## Drawing the Nodes ----------------------------
    fig, ax = plt.subplots(figsize=size_)
    G = nx.Graph()
    pos = {}
    node_colors = []
    for i in range(len(nodes)):
        G.add_node(i)
        pos.update({i: [nodes[i][0], nodes[i][1]]})
        if nodes[i][3] == 1:  # boundary
            node_colors.append('b')
        elif nodes[i][3] == 2:  # load point
            if max(nodes[i][2]) > 0 : node_colors.append('g')
            else: node_colors.append('r')
        elif nodes[i][3] == 3:  # added nodes
            node_colors.append('lime')
        else:
            if i in node_list: node_colors.append('k')
            else: node_colors.append('lightgrey')
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=1, node_size=30, node_shape='o', linewidths=0)
    ## Drawing the Edges ----------------------------
    edge_w = {}
    edge_c = {}
    shum = 0
    for i in celements.keys():
        if i in X_dic and X[i] > 0.12:
            shum += 1
            i_pos1 = celements[i].nodei.name
            i_pos2 = celements[i].nodej.name
            G.add_edge(i_pos1, i_pos2)
            edge_w.update({(i_pos1, i_pos2): 5 * X[i]})
            edge_c.update({(i_pos1, i_pos2): 'k'})  # colcol
        # else:
        #     i_pos1 = celements[i].nodei.name
        #     i_pos2 = celements[i].nodej.name
        #     G.add_edge(i_pos1, i_pos2)
        #     edge_w.update({(i_pos1, i_pos2): 0})
        #     edge_c.update({(i_pos1, i_pos2): 'lightgrey'})
    edge_c = list(edge_c.values())
    edge_w = list(edge_w.values())
    nx.draw_networkx_edges(G, pos, edge_color=edge_c, width=edge_w, ax=ax, alpha=1)
    print('shum is:', shum)
    plt.axis('off')
    plt.suptitle('|ST:' + str(round(t_ime, 4)) + '|W:' + str(round(volume, 4)) + '|R:' + str(r_ound) + '|S:' + str(s_tep) + '|I:' + str(itr), fontsize=10)
    plt.show()
    png_name = draw_number
    fig.savefig(str(foldername + '/' + png_name + '.pdf'), bbox_inches='tight')
    fig.savefig(str(foldername + '/' + png_name + '.png'))
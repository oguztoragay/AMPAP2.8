import matplotlib.pyplot as plt
import matplotlib.colors as colors
import networkx as nx
from My_count import count

size_ = (7, 7)
@count
def general_darw(nodes, celements, X, volume, t_ime, foldername, itr, r_ound, s_tep, which_one):
    ss = str(general_darw.counter)
    draw_number = ss.zfill(5)
    if which_one == 1:
        Draw_GROUND_dashed(nodes, celements,foldername, draw_number)
    else:
        Draw_mod(nodes, celements, X, volume, t_ime, foldername, itr, r_ound, s_tep, draw_number)

def Draw_GROUND_dashed(nodes, elements, foldername, draw_number):
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
            if nodes[i].load[1] > 0:
                node_colors.append('g')
                x_load = nodes[i].x
                y_load = nodes[i].y
            else:
                node_colors.append('r')
                x_load = nodes[i].x
                y_load = nodes[i].y
        elif nodes[i].tip == 3:  # added nodes
            node_colors.append('y')
        else:
            node_colors.append('k')
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=1, node_size=25, node_shape='o', linewidths=0)
    for i in elements.keys():
        i_pos1 = elements[i].nodei.name
        i_pos2 = elements[i].nodej.name
        if elements[i].inn == True:  G.add_edge(i_pos1, i_pos2)
    nx.draw_networkx_edges(G, pos, edge_color='lightgrey', width=2, ax=ax, style='dashed')
    plt.axis('off')
    plt.suptitle('Ground Structure '+draw_number, fontsize=10)
    plt.show()
    png_name = draw_number
    fig.savefig(str(foldername + '/' + 'Ground Structure ' + draw_number + '.pdf'), bbox_inches='tight')
    fig.savefig(str(foldername + '/' + png_name + '.png'))

def Draw_mod(nodes, celements, X, volume, t_ime, foldername, itr, r_ound, s_tep, draw_number):
    # colors_list = list(['k', 'k', 'k'])
    # if s_tep == 1:
    #     colors_list = list(colors.TABLEAU_COLORS.values())
    # colcol = colors_list[itr]
    burdan = celements
    # Xdic = X
    X_dic = [i for i, k in X.items() if k > 0.2]
    nodeset1 = []
    nodeset2 = []
    for i in X_dic:
        nodeset1.append(burdan[float(i)].nodei.name)
        nodeset2.append(burdan[float(i)].nodej.name)
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
        if nodes[i].tip == 1:  # boundary
            node_colors.append('b')
        elif nodes[i].tip == 2:  # load point
            if max(nodes[i].load) > 0: node_colors.append('g')
            else: node_colors.append('r')
        elif nodes[i].tip == 3:  # added nodes
            node_colors.append('y')
        else:
            if i in node_list: node_colors.append('k')
            else: node_colors.append('lightgrey')
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=1, node_size=30, node_shape='o', linewidths=0)
    edge_widths = {};    edge_colors = {};    edge_styles = {};
    for i in burdan.keys():
        i_pos1 = burdan[i].nodei.name
        i_pos2 = burdan[i].nodej.name
        G.add_edge(i_pos1, i_pos2)
        if i in X_dic:
            edge_widths.update({(i_pos1, i_pos2): 5 * X[i]})
            edge_colors.update({(i_pos1, i_pos2): 'k'}) # colcol
            edge_styles.update({(i_pos1, i_pos2): 'solid'})
        else:
            edge_widths.update({(i_pos1, i_pos2): 0.3})
            edge_colors.update({(i_pos1, i_pos2): 'lightgrey'})
            edge_styles.update({(i_pos1, i_pos2): 'solid'})
    edge_colors1 = list(edge_colors.values())
    edge_styles1 = list(edge_styles.values())
    edge_widths1 = list(edge_widths.values())
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors1, width=edge_widths1, ax=ax, style=edge_styles1, alpha=1)
    plt.axis('off')
    plt.suptitle('|Stime:' + str(round(t_ime, 4)) + '|Weight:' + str(round(volume, 4)) + '|R:' + str(r_ound) + '|S:' + str(s_tep) + '|I:' + str(itr), fontsize=10)
    plt.show()
    png_name = draw_number
    fig.savefig(str(foldername+'/' + draw_number + '.pdf'), bbox_inches='tight')
    fig.savefig(str(foldername + '/' + png_name + '.png'))


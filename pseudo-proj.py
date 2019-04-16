#!/usr/bin/python3

import sys
from conllu import conllu_sentences


def head_distance(id, h_list):
    """If an id's head id is 0, its head distance is 1. 1 is the smallest head distance
      Larger head_distance means lower in the hierarchy"""
    h_dist = 0
    head_id = h_list[id - 1]
    while head_id != 0:
        h_dist += 1
        head_id = h_list[head_id - 1]
    h_dist += 1
    return h_dist


def is_non_proj(h1, d1, h2, d2):
    if h1 == h2 or h1 == d2 or h2 == d1:  # same head, head connecting to the other's dependency , projective
        return False
    elif h1 < d1:
        h_in_range = h1 < h2 < d1
        d_in_range = h1 < d2 < d1
        if h_in_range != d_in_range:
            return True
    elif h1 > d1:
        h_in_range = d1 < h2 < h1
        d_in_range = d1 < d2 < h1
        if h_in_range != d_in_range:
            return True
    else:
        return False


def get_new_head(h, h_list):
    new_h = h_list[h-1]
    return new_h


def get_non_proj_list(sent):
    """ Return a list of list of crossing edge pairs, if 'sent' is non-projective.
    The prior condition is that the current_dep_id is always less than dep_id.
        Then there is only 4 types of crossing edges.
        1) current dependency is a right arc, when head_id is
        inside the range of current_head_id and current_dep_id, there is a crossing edge.
        2) current dependency is a left arc, and the head of current dependency is between two dependency ids.
        There is a crossing edge when head id is inside the rage of current_dep_id and current_head_id.
        3) & 4) current dependency is a left arc, and the current_head_id is bigger than the dep_id.
        There is a crossing edge when head_id is not inside the range of current_dep_id and current_head_id.
    """
    head_list = s.head()
    head_dep_list = []
    cross_list = []
    for dep_idx, current_head_id in enumerate(head_list):
        if current_head_id == 0:
            continue
        dep_id = dep_idx + 1
        head_dep_list.append((current_head_id, dep_id))

    for i, (current_head_id, current_dep_id) in enumerate(head_dep_list):
        current_tuple = (current_head_id, current_dep_id)
        for (head_id, dep_id) in head_dep_list[i:]:  # current_dep_id < dep_id
            other_tuple = (head_id, dep_id)
            if current_head_id == head_id:#same head, projective
                continue
            #  1)
            elif current_head_id < current_dep_id and current_head_id < head_id < current_dep_id:
                cross_list.append([current_tuple, other_tuple])# add pair of crossing edge to cross_list
            #  2)
            elif current_dep_id < current_head_id < dep_id and current_dep_id < head_id < current_head_id:
                cross_list.append([current_tuple, other_tuple])
            #  3) & 4)
            elif current_head_id > dep_id and (head_id < current_dep_id or current_head_id < head_id):
                cross_list.append([current_tuple, other_tuple])
    return cross_list


if __name__ == '__main__':
    # check file name
    assert (".conllu" in sys.argv[1]), "Incorrect file! Please use a .conllu file."
    for s in conllu_sentences(sys.argv[1]):
        list_head = s.head()
        id_list = [i for i in range(1, len(list_head) + 1)]
        head_dist_list = []#compute a head distance list and use it
        for i in id_list:
            head_dist_list.append(head_distance(i, list_head))
        list_cross = get_non_proj_list(s)

        if len(list_head) != 0 and len(list_cross) != 0:
            dist_sum = []
            for [(h1, d1), (h2, d2)] in list_cross:
                head_sum = head_dist_list[h1 - 1] + head_dist_list[h2 - 1]
                dist_sum.append(head_sum)
            # store the edge updates. updated edge as key, list of all the head used as value.
            edge_update = dict()
            while max(dist_sum) != 0:
                max_idx = dist_sum.index(max(dist_sum))
                [(h1, d1), (h2, d2)] = list_cross[max_idx]  # get a pair of crossing edge in the lowest hierachy
                old_e1 = (h1, d1)
                old_e2 = (h2, d2)

                # check for cross edge update. Update head.
                if (h1, d1) in edge_update.keys():
                    length = len(edge_update[(h1, d1)])
                    h1 = edge_update[(h1, d1)][length-1]

                if (h2, d2) in edge_update.keys():
                    length = len(edge_update[(h2, d2)])
                    h2 = edge_update[(h2, d2)][length - 1]

                # check for non projective,
                while is_non_proj(h1, d1, h2, d2): #continue as long as the pair of edges is still crossing
                    # get head distance for h1 and h2
                    h1_dist = head_dist_list[h1-1]
                    h2_dist = head_dist_list[h2-1]
                    # compare and process the edge with bigger head distance
                    """head_dist must be bigger than one, if there is a problem check here."""
                    if h1_dist < h2_dist: # move head up one level, and save the result to edge_update
                        old_h2 = h2
                        h2 = get_new_head(h2, list_head)

                        if old_e2 not in edge_update.keys():
                            edge_update[old_e2] = list()
                            edge_update[old_e2].append(old_h2)
                            edge_update[old_e2].append(h2)
                        else:
                            edge_update[old_e2].append(h2)
                    else:
                        old_h1 = h1
                        h1 = get_new_head(h1, list_head)

                        if old_e1 not in edge_update.keys():
                            edge_update[old_e1] = list()
                            edge_update[old_e1].append(old_h1)
                            edge_update[old_e1].append(h1)
                        else:
                            edge_update[old_e1].append(h1)
                    # update, save to dict, and update
                dist_sum[max_idx] = 0
            # after processing now update the file.
            #original deprel list
            deprel_list = s.deprel()
            # update nodes in sentence
            for node in s.nodes:
                if (node.head, node.index) in edge_update.keys():
                    h_history = edge_update[(node.head, node.index)]
                    length = len(h_history)
                    # set head to the newest
                    new_head = h_history[length - 1]
                    node.set_head(new_head)
                    # combine all the past deprel, seperate by "."
                    for i, h in enumerate(h_history):
                        if i == len(h_history) - 1:
                            continue
                        new_deprel = deprel_list[h - 1]
                        node.set_deprel(new_deprel)
            #print out result to the screen
            print(s.__str__())


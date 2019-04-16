#!/usr/bin/python3

import sys
from conllu import conllu_sentences

def is_non_proj(sent):
    """ Return True if 'sent' is non-projective.
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
    for dep_idx, current_head_id in enumerate(head_list):
        if current_head_id == 0:
            continue
        dep_id = dep_idx + 1
        head_dep_list.append((current_head_id, dep_id))
    for i, (current_head_id, current_dep_id) in enumerate(head_dep_list):
        for (head_id, dep_id) in head_dep_list[i:]:  # current_dep_id < dep_id
            if current_head_id == head_id:#same head, projective
                continue
            #  1)
            elif current_head_id < current_dep_id and current_head_id < head_id < current_dep_id:
                return True
            #  2)
            elif current_dep_id < current_head_id < dep_id and current_dep_id < head_id < current_head_id:
                return True
            #  3) & 4)
            elif current_head_id > dep_id and (head_id < current_dep_id or current_head_id < head_id):
                return True
    return False

if __name__ == '__main__':
    # initialize variable
    non_proj = 0
    sent = 0
    # check file name
    assert (".conllu" in sys.argv[1]), "Incorrect file! Please use a .conllu file."
    for s in conllu_sentences(sys.argv[1]):
        sent += 1
        if is_non_proj(s):
            non_proj += 1
    # <Print out the results>
    print("NON-PROJ", "\t", non_proj, "\t", round(non_proj / sent * 100, 2), "%")
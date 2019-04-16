#!/usr/bin/python3

import sys
from conllu import conllu_sentences
""" 1)ignore subtypes of dependencies i.e "nsubj:pass"
    2)if primary dependency relation exist, ignore others
        subject relation: nsubj(primary), csubj
        object relation: obj(primary), ccomp, xcomp"""
if __name__ == '__main__':
    #initialize variables
    v_as_root, with_s, with_o, with_so, sv, vs, ov, vo = (0,) * 8
    sov_collection = dict()
    #check file name
    assert(".conllu" in sys.argv[1]), "Incorrect file! Please use a .conllu file."

    for s in conllu_sentences(sys.argv[1]):
        # check if there is more than one root, just in case.
        root_indices = [i for i, x in enumerate(s.head()) if x == 0]
        assert(len(root_indices) == 1), "Error: more than one root found!"

        root_index = s.head().index(0)
        root_id = root_index + 1
        root_upos = s.upos(root_id) # find upos of index
        if root_upos == "VERB":
            v_as_root += 1
            # find the direct dependency
            # list of direct dependencies' id
            dep_ids = [i + 1 for i, head_id in enumerate(s.head()) if
                       head_id == root_id]
            # list of dependency relations, plus id information
            dep_rel = []
            dep_rel_id = []

            for dep_id in dep_ids:
                dep_rel.append(s.deprel(dep_id))
                dep_rel_id.append((s.deprel(dep_id), dep_id))  # tuple:(relation, id)

            #initialize variables
            subj_id = None
            obj_id = None

            #primary relation
            if "nsubj" in dep_rel:#there is primary tag
                subj_id = -1
            if "obj" in dep_rel:
                obj_id = -1
            #find subj_id and obj_id if there is one.
            for (rel, rel_id) in dep_rel_id:
                """rel = dep_pair[0]
                rel_id = dep_pair[1]"""
                #subject
                if subj_id == -1:
                    if rel == "nsubj":  # if primary relation is present, then no need to check for other relations
                        subj_id = rel_id
                elif subj_id is None:
                    if rel == "csubj":
                        subj_id = rel_id
                #object
                if obj_id == -1:
                    if rel == "obj":  # if primary relation is present, then no need to check for other relations
                        obj_id = rel_id
                elif obj_id is None:
                    if rel == "ccomp":
                        obj_id = rel_id
                    elif rel == "xcomp":
                        obj_id = rel_id


            if subj_id is not None:
                with_s += 1
                # s v order
                if subj_id < root_id:
                    sv += 1
                elif subj_id > root_id:
                    vs += 1
                else:#just in case
                    raise Exception("Duplicate id found!")
            if obj_id is not None:
                with_o += 1
                # o v order
                if obj_id < root_id:
                    ov += 1
                elif obj_id > root_id:
                    vo += 1
                else:#just in case
                    raise Exception("Duplicate id found!")
            if subj_id is not None and obj_id is not None:
                with_so += 1
                # s o v order
                list = [(subj_id, "S"), (obj_id, "O"), (root_id, "V")]
                list.sort()
                sov_order = "".join([x[1] for x in list])
                if sov_order not in sov_collection.keys():
                    sov_collection[sov_order] = 1
                else:
                    sov_collection[sov_order] += 1

    # <Print out the results>
    for sov_order in sov_collection.keys():
        print(sov_order, "\t", sov_collection[sov_order], "\t", round(sov_collection[sov_order]/with_so * 100, 2), "%")

    if sv != 0:
        print("SV", "\t", sv, "\t", round(sv / with_s * 100, 2), "%")
    if vs != 0:
        print("VS", "\t", vs, "\t", round(vs / with_s * 100, 2), "%")
    if ov != 0:
        print("OV", "\t", ov, "\t", round(ov / with_o * 100, 2), "%")
    if vo != 0:
        print("VO", "\t", vo, "\t", round(vo / with_o * 100, 2), "%")
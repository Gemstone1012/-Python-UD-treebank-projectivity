# UD treebank: projectivity

In this project, [Universal Dependencies](https://universaldependencies.org/)
treebanks are being used.


No CoNLL-U/UD libraries are being used except a program [conllu.py](conllu.py) for handling (reading/writing)
[CoNLL-U files](https://universaldependencies.org/format.html).

## [stats.py](stats.py): Statistics on word order

- This is a Python program that reads a CoNLL-U format treebank,
    and produces statistics only for sentences which root is VERB.

    - Number and percentage of all combinations of subject, object and verb 
        orders if both subject and object arguments are present.
        
    - Number and percentage of all verb-subject and verb-object orders,
        for all main verbal predicates.

    This program takes a single command-line argument,
    followed by the name of the CoNLL-U file, and prints out the statistics:

```
SVO     10  5%
SOV     50  25%
...

```

## [non-proj.py](non-proj.py): Finding and counting non-projective trees

This is a Python program that finds and counts the number of
non-projective trees in a CoNLL-U format treebank. 
It takes a single command-line argument,
followed by the name of the CoNLL-U file, and prints out the number and ratio
of non-projective trees in percentage.
 

```
NON-PROJ    20  0.5%
```

## [pseudo-proj.py](pseudo-proj.py): Pseudo projectivization

Given a non-projective parser, "projectivize" the trees during training is one way to handle 
non-projectivity. This program "projectivize" the trees.

A few toy non-projective trees are given in [non-proj.conllu](non-proj.conllu).

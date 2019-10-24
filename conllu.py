#!/usr/bin/env python3

import sys

""" Utilities for reading/writing CoNLL-U dependency treebanks.
"""

class Node(object):
    """ Holds a node (a word) in a dependency tree

        Except last three arguments, the attributes correspond to CoNLL-U
        columns. Integer values are explicitly typecast.
            multi       keeps the end of the range (the part after the
                        dash in CoNLL-U, in a multi-word token.
                        'index' holds the beginning of the range.
            empty       keeps secondary index of an 'empty' word (the
                        part after the dot in CoNLL-U). 'index' holds
                        the part before the dot.
    """

    __slots__ = ("index form lemma upos xpos feats "
                 "head deprel deps misc multi empty").split()

    def __init__(self,
                 index=0, form=None, lemma=None,
                 upos=None, xpos=None, feats=None,
                 head=None, deprel=None, deps=[],
                 misc=None, multi=0, empty=0):
        self.index=int(index)
        self.form=form
        self.lemma=(None if not lemma or
                        (lemma == '_' and upos != 'PUNCT')
                    else lemma)
        self.upos=upos
        self.xpos=None if not xpos or xpos == '_' else xpos
        self.feats=None if not feats or feats == '_' else feats
        self.head=None if not head or head == '_' else int(head)
        self.deprel=deprel
        self.deps=None if not deps or deps == '_' else deps
        self.misc=None if not misc or misc == '_' else misc
        self.multi = int(multi)
        self.empty = int(empty)

    @classmethod
    def from_str(cls, s):
        columns = s.rstrip().split("\t")
        if '-' in columns[0]:
            begin, end = columns[0].split('-')
            return cls(index=begin, form=columns[1],
                    misc=columns[8], multi=end)
        elif '.' in columns[0]:
            empty_id = columns[0].split('.')
            part1, part2 = columns[0].split('.')
            return cls(part1, *columns[1:], empty=part2)
        else:
            return cls(*columns)

    def __str__(self):
        fields = [str(getattr(self, x)) for x in self.__slots__[1:10]]
        idx = str(self.index)
        if self.multi:
            idx = "-".join((str(self.index), str(self.multi)))
        elif self.empty:
            idx = ".".join((str(self.index), str(self.empty)))
        return (("\t".join([idx] + fields))
                        .replace('None', '_')
                        .replace('[]', '_'))
    def set_head(self, new_head):
        self.head = new_head

    def set_deprel(self, new_deprel):
        old_deprel = self.deprel
        self.deprel = ".".join((new_deprel, old_deprel))

class Sentence(object):
    """ Holds a CoNLL-U sentence.
        Attributes:
            nodes   - nodes of the primary tree
            multi   - dictionary of multi-word tokens indexed by
                      beginning of the range, value is a single
                      node with 'multi' attribute to the final index
            empty   - dictionary of empty tokens indexed by the
                      previous token index, value is a list.
            comment - the pre-sentence comments
    """

    __slots__ = ('nodes', 'empty', 'multi', 'comment')

    def __init__(self, instr=None, stream=None):
        self.nodes = [Node(index=0)] # initialize with the dummy root node
        self.multi = dict()
        self.empty = dict()
        self.comment = []

        if stream:
            inp_str = self.read_sentence(stream)
        self.from_str(inp_str)

    def __len__(self):
        return len(self.nodes) - 1

    def from_str(self, lines):
        for line in lines.splitlines():
            if line.startswith('#'):
                assert len(self.nodes) == 1,\
                       "Comments are allowed only at the beginning"
                self.comment.append(line)
            else:
                node = Node.from_str(line)
                if node.multi:
                    self.multi[node.index] = node
                elif node.empty:
                    e = self.empty.get(node.index, [])
                    e.append(node)
                    self.empty[node.index] = e
                else:
                    self.nodes.append(node)

    def read_sentence(self, stream):
        """ Read a sentence form a CoNLL-U file from a stream.
            The returned list of strings includes pre-sentence comment(s).
            The final empty line is read, but not added to the return value.
        """
        lines = ""
        line = stream.readline()
        while line and not line.isspace():
            lines += line
            line = stream.readline()
        return lines

    def __str__(self):
        s = "\n".join(self.comment) + "\n"
        for i in range(1, len(self) + 1):
            if i in self.multi:
                s += str(self.multi[i]) + "\n"
            s += str(self.nodes[i]) + "\n"
            if self.empty and i in self.empty:
                for e in self.empty[i]:
                    s += str(e) + "\n"
        return s

    def form(self, index=None):
        if index:
            return self.nodes[index].form
        else:
            return [x.form for x in self.nodes[1:]]

    def tokens(self):
        tokens = [node.form for node in self.nodes]
        for node in self.multi.values():
            tokens[node.index] = node.form
            for i in range(node.index + 1, node.multi + 1):
                tokens[i] = None
        return [x for x in tokens if x is not None]

    def text(self):
        tokens = []
        last_tok = len(self.nodes) - 2
        for i, node in enumerate(self.nodes[1:]):
            if (node.misc and 'SpaceAfter=No' in node.misc) or \
                    (i == last_tok):
                tokens.append(node.form)
            else:
                tokens.append(node.form + " ")
        for node in self.multi.values():
            if node.misc and 'SpaceAfter=No' in node.misc:
                tokens[node.index] = node.form
            else:
                tokens[node.index] = node.form + " "
            for i in range(node.index, node.multi):
                tokens[i] = None
        return ''.join([x for x in tokens if x is not None])

    def upos(self, index=None):
        """Return the upos for the indexed node
           or a list of all upos tags. """
        if index:
            return self.nodes[index].upos
        else:
            return [x.upos for x in self.nodes[1:]]

    def lemma(self, index=None):
        if index:
            return self.nodes[index].lemma
        else:
            return [x.lemma for x in self.nodes[1:]]

    def pos(self, index=None):
        """Alternative spelling"""
        return self.upos(index)

    def xpos(self, index=None):
        if index:
            return self.nodes[index].xpos
        else:
            return [x.xpos for x in self.nodes[1:]]

    def feats(self, index=None):
        if index:
            return self.nodes[index].feats
        else:
            return [x.feats for x in self.nodes[1:]]

    def deprel(self, index=None):
        if index:
            return self.nodes[index].deprel
        else:
            return [x.deprel for x in self.nodes[1:]]

    def head(self, index=None):
        if index:
            return self.nodes[index].head
        else:
            return [x.head for x in self.nodes[1:]]

    def misc(self, index=None):
        if index:
            return self.nodes[index].misc
        else:
            return [x.misc for x in self.nodes[1:]]

def conllu_sentences(f):
    if isinstance(f, str):
        fp = open(f, 'r')
    else: # assume it is a file-like object
        fp = f
    sent = Sentence(stream=fp)
    while sent:
        yield sent
        sent = Sentence(stream=fp)
    if isinstance(f, str): # close only if we opened it
        fp.close()

def push_test():
    pass

if '__main__' == __name__:

    sentences = conllu_sentences(sys.argv[1])
    for sent in sentences:
        print("---------")
        print(sent)
        print("---------")

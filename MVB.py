#!/bin/python3

import importlib
import os
import sys
import numpy as np

LoadLog = importlib.import_module("LoadLog")
from LoadLog import LoadLog

class Field:
    def __init__(self, group:int, field:int, index:int=0):
        if isinstance(group, str):
            group = int(group)
        if isinstance(field, str):
            field = int(field)
        self.field = field
        self.index = index
        self.group = group

    def __repr__(self) -> str:
        return 'F{}'.format(self.field).replace(' ', '0')

class Group:
    def __init__(self, group:int, fields:list[Field]=[]):
        if isinstance(group, str):
            group = int(group)
        self.group = group
        self.fields = fields

    def __repr__(self) -> str:
        return 'G{:3.0f}'.format(self.group).replace(' ', '0')

class MVB(LoadLog):
    def __init__(self, log_file):
        super().__init__(log_file,False) 
        self.parse_mvb()

    def parse_mvb(self):
        group_nums = set[int]()
        fields = list[Field]()

        for i in range(len(self.in_blocks)):
            if self.in_blocks[i].startswith('G'):
                group_num = self.in_blocks[i].replace('G', '')
                field_num = self.in_blocks[i + 1].replace('F', '')
                fields.append(Field(group_num, field_num, i))
                group_nums.add(group_num)

        self.groups = list[Group]()

        for v in group_nums:
            self.groups.append(Group(v, [x for x in fields if x.group == v]))
        
    def print_blocks(self):
        for g in self.groups:
            print(g, end=':')
            for f in g.fields:
                print(f, end=' ')
            print()


    def has(self, group:Group):
        for g in self.groups:
            if g.group == group.group:
                return True
        return False

    def has(self, field:Field):
        for g in self.groups:
            if g.group == field.group:
                for f in g.fields:
                    if f.field == field.field:
                        return True
                    
        return False

    def get(self, group):
        #Return fields as array
        fields = []
        for i in range(len(self.in_blocks)):
            if self.in_blocks[i] == group:
                fields.append(self.in_blocks[i + 1])
        return fields

    def has(self, group, field):
        #If field and group exists
        return field in self.get(group)
    
    def get_g(self, field:Field):
        return self.get_index(Group(field.group), field)

    def get_index(self, group:str, field:str):
        print("get_index:",group, field)
        if not self.has(group, field):
            return None
        
        index = self.in_blocks.index(group)
        while index < len(self.in_blocks) + 1:
            if self.in_blocks[index + 1] == field:
                return index
            index = self.in_blocks.index(group, index)

    def get_default(self, group, field):
        return None

    def get_name(self, group, field):
        #Get value of field
        index = self.get_index(group, field)
        if index is None:
            return self.get_default(group, field)
        
        return self.in_fields[index + 1]



if len(sys.argv) < 2:
    print("Add filename")
    exit(1)

if not os.path.isfile(sys.argv[1]):
    print("File not found")
    exit(1)

mvb = MVB(sys.argv[1])

mvb.print_all(all=False)
print(mvb.in_blocks)
mvb.print_blocks()
print(mvb.get('G001'))
print(mvb.has('G001', 'F0'))
print(mvb.get_name('G001', 'F0'))
print(mvb.get('G002'))
print(mvb.get_g(Field(1,0)))
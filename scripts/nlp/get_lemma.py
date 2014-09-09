#encoding: utf8
#-------------------------------------------------------------------------------
# Name:        модуль2
# Purpose:
#
# Author:      kamivao
#
# Created:     30.06.2014
# Copyright:   (c) kamivao 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# nooj_physics_en - словарь, сгенерированный в нудже для тестов по физике (англ)
# filename1 -  выходной файл с леммами (txt)
# filename2 - файл nooj_physics_en.txt
from argparse import ArgumentParser

from optparse import OptionParser


def main():
    pass



parser = ArgumentParser()

parser.add_argument('-t', '--term', dest='term', required=True, help='term for parsing')
parser.add_argument('-d', '--dict', dest='dict', required=True, help='dictionary file for term parsing')
parser.add_argument('-f', '--file', dest='filename', required=True, help='write lemmas to FILE')

args = parser.parse_args()

term = args.term
dict = args.dict
filename = args.filename


out = open(filename, "w") # выходной файл с леммами

d = {} #конвертация словаря NooJ в питоновский словарь, key - словоформа, val - лемма
with open(dict, "r") as f:
    for line in f:
       (key, val) = line.split('\t')
       d[str(key)] = val

input_str = term # в выходном файле 2 х NO_LEMMA
words = input_str.split() #входная строка конвертируется в список

for word in words: #ищем лемму для каждого слова и записываем в выходной файл
    if word in d:
        lemma = d[word]
        out.write(lemma)
    #else: out.write("NO_LEMMA"+'\n') #

out.close() #
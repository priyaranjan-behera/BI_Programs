import sys
import collections
import sklearn.naive_bayes
import sklearn.linear_model
import nltk
import random
import csv
import math
import copy
import numpy as np
from igraph import *
random.seed(0)


def main(argv):
	graph = read('fb_caltech_small_edgelist.txt')
	
	attributes = np.loadtxt('fb_caltech_small_attrlist.csv', skiprows=1, delimiter=',')
	print(attributes)


	graph.vs["community"] = range(len(graph.get_edgelist()))
	print(graph.get_edgelist())
	print(graph.vs["community"])

	for i in range(15):
		graph_cm = getCompositeModularity(graph)
		for vertex in range(len(graph.vs)):
			old_community = graph.vs[vertex]['community']
			for community in np.unique(graph.vs["community"]):
				graph.vs[vertex]['community'] = community
				new_graph_cm = getCompositeModularity(graph)
				if(new_graph_cm <= graph_cm):
					graph.vs[vertex]['community'] = old_community


def getCompositeModularity(graph):
	




if __name__ == "__main__":
   main(sys.argv[1:])
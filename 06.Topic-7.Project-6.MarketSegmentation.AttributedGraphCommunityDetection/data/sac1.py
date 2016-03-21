import sys
import collections
import sklearn.naive_bayes
import sklearn.linear_model
import nltk
import random
import csv
import math
import copy
import scipy
import numpy as np
from igraph import *
random.seed(0)


def main(argv):
	if(len(argv) != 1):
		print("Usage: python sac1.py <alpha>")
		exit(0)

	alpha = int(argv[0])
	graph = read('fb_caltech_small_edgelist.txt')
	attributes = np.loadtxt('fb_caltech_small_attrlist.csv', skiprows=1, delimiter=',')
	#print(attributes)


	graph.vs["community"] = range(len(graph.vs))
	graph.es["weight"] = [1]*len(graph.es)
	#print(graph.get_edgelist())
	#print(graph.vs["community"])

	for i in range(15):
		print('Starting Iteration: ', i+1)
		print "Total vertices", len(graph.vs)


		editsince = 0;
		while(1):
			vertex = random.randint(0, len(graph.vs)-1)
			print('Processing Random Vertex: i+1', vertex)
			cm_gain = 0;
			edit = 0;
			editsince = 0;
			#if(vertex%20 == 0):
			#	print 'Vertex:',vertex

			new_community = graph.vs[vertex]['community']
			old_community = graph.vs[vertex]['community']
			for community in np.unique(graph.vs["community"]):
				temp_cm_gain = getCompositeModularityGain(graph, community, vertex, attributes, alpha)
				if(temp_cm_gain > cm_gain):
					new_community = community
					cm_gain = temp_cm_gain
					edit = 1

			if(edit == 1):
				editsince = 0;
			else:
				editsince += 1
				if(editsince > 3):
					break;

			graph.vs[vertex]['community'] = new_community

		print("Total number of communities is: ", len(np.unique(graph.vs["community"])))
		print "End of Phase1"


		#Phase2 Begins
		graph2 = graph.contract_vertices(graph.vs["community"], combine_attrs=dict(weight="sum", community="first"))

		graph = graph2



		for community in np.unique(graph.vs["community"]):
			for index in range(len(graph.vs)):
				if graph.vs[index]['community'] == community:
					print index, ",",
			print

	with open('communities.txt', 'w') as f:
		for community in np.unique(graph.vs["community"]):
			for index in range(len(graph.vs)):
				if graph.vs[index]['community'] == community:
					f.write(str(index))
					f.write(",")
			f.write('\n')

	graph.vs['color'] = [known_colors.keys()[community] for community in graph.vs["community"]]

	#plot(graph, 'communities.pdf', layout=layout)


def getCompositeModularityGain(graph, community, newPoint, attributes, alpha):
	communityList = graph.vs["community"]
	structural_modularity_old = graph.modularity(communityList)

	comm_size = 0;
	sim_sum = 0;
	for index in range(len(graph.vs)):
		if(graph.vs[index] == community):
			similarity = scipy.spatial.distance.cosine(attributes[index], attributes[newPoint])
			sim_sum += similarity
			comm_size += 1

	if(sim_sum != 0):
		DeltaQAttr = float(sim_sum)/float(comm_size)
	else:
		DeltaQAttr = 0;
	communityList[newPoint] = community
	structural_modularity_new = graph.modularity(communityList)

	DeltaQNewmann = structural_modularity_new - structural_modularity_old

	DeltaQ = (alpha * DeltaQNewmann) + ((1-alpha) * DeltaQAttr)

	return DeltaQ









if __name__ == "__main__":
   main(sys.argv[1:])
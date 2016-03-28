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
import csv
from collections import defaultdict
random.seed(0)


def main(argv):
	if(len(argv) != 1):
		print("Usage: python sac1.py <alpha>")
		exit(0)

	alpha = float(argv[0])
	graph = read('fb_caltech_small_edgelist.txt')
	#attributes = np.loadtxt('fb_caltech_small_attrlist.csv', skiprows=1, delimiter=',')
	attributes = []
	#print(attributes
	with open('fb_caltech_small_attrlist.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			attributes.append(row)


	graph.vs["community"] = range(len(graph.vs))
	graph.es["weight"] = [1]*len(graph.es)
	global_community_list = graph.vs["community"]

	for i in range(len(attributes)):
		for key in attributes[i].keys():
			graph.vs[i][key] = int(attributes[i][key])
	#print(graph.get_edgelist())
	#print(graph.vs["community"])
	keys = attributes[0].keys()

	for i in range(15):
		print('Starting Iteration: ', i+1)
		print "Total vertices", len(graph.vs)

		print graph.vs
		editsince = 0;
		commCountEditSince = 0;
		oldCommunityList = graph.vs["community"]
		while(1):
			vertex = random.randint(0, len(graph.vs)-1)
			print('Processing Random Vertex:', i+1, vertex)
			print('Number of communities left: ', len(np.unique(graph.vs["community"])))
			preCommunitiesLeft = len(np.unique(graph.vs["community"]))
			cm_gain = 0.0;
			edit = 0;
			#if(vertex%20 == 0):
			#	print 'Vertex:',vertex

			new_community = graph.vs[vertex]['community']
			old_community = graph.vs[vertex]['community']
			for community in np.unique(graph.vs["community"]):
				temp_cm_gain = getCompositeModularityGain(graph, community, vertex, keys, alpha)
				if(temp_cm_gain > cm_gain):
					new_community = community
					cm_gain = temp_cm_gain

			if(graph.vs[vertex]['community'] != new_community):
				editsince = 0;
			else:
				editsince += 1
				if(editsince > 50):
					break;

			print 'Moving from: ', graph.vs[vertex]['community'], 'to: ', new_community
			graph.vs[vertex]['community'] = new_community

			postCommunitiesLeft = len(np.unique(graph.vs["community"]))
			if(preCommunitiesLeft != postCommunitiesLeft):
				commCountEditSince = 0;
			else:
				commCountEditSince += 1;
				if(commCountEditSince > 1000):
					break;

			print('editsince = ', editsince)
			print('commCountEditSince = ', commCountEditSince)

		print("Total number of communities is: ", len(np.unique(graph.vs["community"])))
		print "End of Phase1"



		#Phase2 Begins
		print "Start of Phase2"
		communityList = graph.vs["community"]

		for i in range(len(global_community_list)):
			for j in range(len(oldCommunityList)):
				if(global_community_list[i] == oldCommunityList[j]):
					global_community_list[i] = communityList[j];
					break;


		newCommunityList = []
		uniqueCommunity = np.unique(communityList)
		for community in communityList:
			for i in range(len(uniqueCommunity)):
				if(uniqueCommunity[i] == community):
					newCommunityList.append(i)
					break;

		for i in range(len(global_community_list)):
			for j in range(len(communityList)):
				if(global_community_list[i] == communityList[j]):
					global_community_list[i] = newCommunityList[j];
					break;
		#HAVEALOOK


		graph.vs["community"] = newCommunityList
		graph.contract_vertices(newCommunityList, combine_attrs=mean)
		graph.simplify(combine_edges=sum)
		#graph.vs["community"] = communityList

		#vc = VertexClustering(graph, membership=communityList)
		#graph = vc.cluster_graph(combine_vertices=mean, combine_edges=sum)

		#graph.vs["community"] = communityList


		print "After Phase 2"

		print('The Edgelist is: ',graph.get_edgelist())
		print('Communities are: ', graph.vs["community"])

		


		for community in np.unique(graph.vs["community"]):
			for index in range(len(global_community_list)):
				if global_community_list[index]== community:
					print index, ",",
			print
	filename = 'communities' + str(alpha)
	with open(filename, 'w') as f:
		for community in np.unique(graph.vs["community"]):
			for index in range(len(global_community_list)):
				if global_community_list[index]== community:
					f.write(str(index))
					f.write(",")
			f.write('\n')

	plot(graph)
	graph.vs['color'] = [known_colors.keys()[community] for community in graph.vs["community"]]

	#plot(graph, 'communities.pdf', layout=layout)


def getCompositeModularityGain(graph, community, newPoint, keys, alpha):
	communityList = graph.vs["community"]
	structural_modularity_old = graph.modularity(communityList)

	comm_size = 0;
	sim_sum = 0.0;
	comm_count = len(np.unique(communityList))
	for index in range(len(graph.vs)):
		if(graph.vs[index]['community'] == community):
			list1 = []
			list2 = []

			for key in keys:
				list1.append(graph.vs[index][key])
				list2.append(graph.vs[newPoint][key])
			similarity = 1-scipy.spatial.distance.cosine(list1, list2)
			#print 'similarity =', similarity 
			sim_sum += similarity
			comm_size += 1

	if(sim_sum != 0):
		DeltaQAttr = float(sim_sum)/(math.pow(float(comm_size),2) * float(comm_count))
	else:
		DeltaQAttr = 0;
	communityList[newPoint] = community
	structural_modularity_new = graph.modularity(communityList)

	DeltaQNewmann = structural_modularity_new - structural_modularity_old

	DeltaQ = (float(alpha) * float(DeltaQNewmann)) + ((1.0-float(alpha)) * float(DeltaQAttr))

	#print 'For community = ', community
	#print 'DeltaQNewmann =',DeltaQNewmann
	#print 'DeltaQAttr =',DeltaQAttr 

	return DeltaQ









if __name__ == "__main__":
   main(sys.argv[1:])
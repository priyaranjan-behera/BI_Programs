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
from operator import add
import matplotlib.pyplot as plt
import md5
import binascii
from os import listdir
from os.path import isfile, join
random.seed(0)

def createGraphFromFile(filename):
	#This method reads the graph data from the file and creates the igraph graph object.
	with open(filename) as f:
		lines = f.readlines()
	numvertices = int(lines[0].split()[0])
	numedges = int(lines[0].split()[1])
	print 'numvertices:', numvertices
	print 'numedges:', numedges
	graph = Graph(numvertices).as_directed()
	for i in range(len(lines)):
		if i == 0:
			continue;
		v1 = int(lines[i].split()[0])
		v2 = int(lines[i].split()[1])
		graph.add_edges([(v1, v2)])
	return graph

def calculateFeaturesFromGraph(graph):
	#This method calculates the features of a gragh. I.E. quality parameter defined for each edge and vertex
	pageranks = graph.pagerank()
	graph.vs["quality"] = pageranks
	graph.es["weight"] = [1]*len(graph.es)
	outdegrees = graph.outdegree()
	features = []
	for vertex in graph.vs:
		feature = ['v'+str(vertex.index), vertex["quality"]]
		features.append(feature)
	for edge in graph.es:
		quality = graph.vs["quality"][edge.tuple[0]] / float(outdegrees[edge.tuple[0]])
		feature = ['e'+str(edge.tuple[0])+'-'+str(edge.tuple[1]), quality]
		features.append(feature)
	return features

def createSimHashfromFeatures(features):
	#This method creates simhash froom features of a graph. 
	#We create a vector for a token according to digest created for the token by md5 and average all vectors to get simhash
	simhash = [0]*32
	finalsimhash = []
	for feature in features:
		m = md5.new(feature[0])
		st = m.digest()
		bindigest = bin(int(binascii.hexlify(st),16))
		hashlist = bindigest[-32:]
		simhashfeature = []
		for hashpoint in hashlist:
			if hashpoint == '0':
				simhashfeature.append(feature[1])
			else:
				simhashfeature.append(-1*feature[1])
		simhash = map(add, simhash, simhashfeature)
	for simhashelement in simhash:
		if(simhashelement < 0):
			finalsimhash.append(0)
		else:
			finalsimhash.append(1)
	return finalsimhash

def findSimilarityEstimates(simhash1, simhash2):
	#This method returns the similarity of the simhashes of two graphs
	similarity = 1-(scipy.spatial.distance.hamming(simhash1, simhash2)/32)
	return similarity

def findSimilarityBetweenGraphs(graph1, graph2):
	#This method finds the similarity of two graphs
	features1 = calculateFeaturesFromGraph(graph1)
	simhash1 = createSimHashfromFeatures(features1)
	features2 = calculateFeaturesFromGraph(graph2)
	simhash2 = createSimHashfromFeatures(features2)
	return findSimilarityEstimates(simhash1, simhash2)

def main(argv):
	similarities = []
	similaritiesDiff = []
	mypath = argv[0]
	files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
	for i in range(len(files)):
		graph1 = createGraphFromFile(join(mypath,files[i]))
		print graph1
		if i>0:
			similarities.append(findSimilarityBetweenGraphs(graph1,graph2))
		graph2 = graph1
	#Following loop calculates diff 1 time series
	for i in range(len(similarities)):
		if(i==0):
			continue;
		similaritiesDiff.append(abs(similarities[i]-similarities[i-1]))
	M = sum(similaritiesDiff)/len(similaritiesDiff)
	Median = median(similarities)
	#We find lower bound od similarities for anomaly
	LowerBound = Median-(3*M)
	print "Similarities: ",similarities
	print "Diff: ", similaritiesDiff
	print "M: ", M
	print "LowerBound", LowerBound
	AnomalyIndex = []
	AnomalyValue = []
	for i in range(len(similarities)):
		if similarities[i] < LowerBound:
			AnomalyValue.append(similarities[i])
			AnomalyIndex.append(i)
			print 'AnomalyIndex:',i,'AnomalyValue',similarities[i]
	plt.plot(range(len(similarities)),similarities, 'g-', label='Similarities in Graphs')
	print 'X=', AnomalyIndex
	print 'Y=', AnomalyValue
	plt.plot(AnomalyIndex, AnomalyValue, 'bD', label="Threshold Exceed")
	AnomalyPointValue = []
	AnomalyPointIndex = []
	#We find anomalous graphs which are two tconsecutive threshold exceeding graph similarities.
	for i in range(len(AnomalyValue)):
		if((AnomalyIndex[i]+1) in AnomalyIndex):
			AnomalyPointIndex.append(AnomalyIndex[i])
			AnomalyPointValue.append(AnomalyValue[i])
	plt.plot(AnomalyPointIndex, AnomalyPointValue, 'ro', label="Anomalous Graph")
	filename = 'time_series.txt'
	with open(filename, 'w') as f:
		for i in range(len(similarities)):
			f.write(str(i))
			f.write(",")
			f.write(str(similarities[i]))
			f.write('\n')
	filename = 'anomaly_plot.pdf'
	plt.legend()
	plt.savefig(filename)
	plt.show()

if __name__ == "__main__":
	if(len(sys.argv) < 2):
		print 'Usage: python anomaly <data_folder>'
   	else:
   		main(sys.argv[1:])
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
random.seed(0)


def getBudgetDict(filename):
	with open(filename, 'rb') as csvfile:
		biddataset = csv.reader(csvfile, delimiter=',')
		budgetMap = {}
		firstline = True #skips the header line
		for row in biddataset:
			if firstline:    #skip first line
				firstline = False
				continue

			if(row[3] != ''):
				budgetMap[int(row[0])] = [int(row[3]), int(row[3])] #Total Budget, Amount Remaining

		return budgetMap

def getBidsDict(filename):
	with open(filename, 'rb') as csvfile:
		biddataset = csv.reader(csvfile, delimiter=',')
		bidMap = {}
		firstline = True #skips the header line
		for row in biddataset:
			if firstline:    #skip first line
				firstline = False
				continue
			if int(row[0]) not in bidMap:
				bidMap[int(row[0])] = [[row[1], float(row[2])]]
			else:
				bidMap[int(row[0])].append([row[1], float(row[2])])

		return bidMap

def getBiddingAdvertisers(biddict, budgetdict, bidword):
	bidder = []
	for adv in biddict:
		for bids in biddict[adv]:
			if(bids[0] == bidword and budgetdict[adv][1] > 0):
				fraction =  (float(budgetdict[adv][0])-float(budgetdict[adv][1]))/float(budgetdict[adv][0])
				expParameter = float(1)-math.exp(fraction-1)
				expParBudget = bids[1]*expParameter
				bidder.append([adv, bids[1], expParBudget, budgetdict[adv][1]]) #Advertiser, Bid Amount, MSSV Fraction, Unspent Balance

	return bidder

def getHighestBiddingAdvertiser(bidders):
	
	bidValue = 0;
	for bids in bidders:
			
		if(bidValue < bids[1]):
			bidder = bids[0]
			bidValue = bids[1]


	return [bidder, bidValue]


def getHighestMSSVAdvertiser(bidders):
	
	budgetParValue = 0;
	for bids in bidders:
			
		if(budgetParValue < bids[2]):
			bidder = bids[0]
			bidValue = bids[1]
			budgetParValue = bids[2]


	return [bidder, bidValue]	


def getHighestUnspentBalanceAdvertiser(bidders):
	
	unspentBalanceValue = 0;
	for bids in bidders:
			
		if(unspentBalanceValue < bids[3]):
			bidder = bids[0]
			bidValue = bids[1]
			unspentBalanceValue = bids[3]


	return [bidder, bidValue]	

def findCompetitiveRatio(biddinginfofile, queriesfile, algorithm):

	budgetdict_org = getBudgetDict(biddinginfofile)
	biddict_org = getBidsDict(biddinginfofile)
	
	inputList = []
	revenueList = []

	file = open(queriesfile, 'r')

	for line in file:
		inputList.append(line.replace('\n', ''))

	#print "Calculating Competitive Ratio. Iterations: "

	for i in range(0,10):
		#print i+1
		budgetdict = copy.deepcopy(budgetdict_org)
		biddict = copy.deepcopy(biddict_org)
		revenue = 0
		random.shuffle(inputList)
		for line in inputList:

			bidders = getBiddingAdvertisers(biddict, budgetdict, line)
			#print "Processing", line, bidders
			if not bidders:
				continue
			else:
				
				if(algorithm == "msvv"):
					highBidder = getHighestMSSVAdvertiser(bidders)
				elif(algorithm == "balance"):
					highBidder = getHighestUnspentBalanceAdvertiser(bidders)
				else:
					highBidder = getHighestBiddingAdvertiser(bidders)
				#print 'allocating word ',  line, ' to ', highBidder[0]
				budgetdict[highBidder[0]][1] = budgetdict[highBidder[0]][1] - highBidder[1]
				revenue = revenue + highBidder[1]

		revenueList.append(revenue)
		#print revenueList

	ALG = np.mean(revenueList)
	OPT = 0

	for adv in budgetdict:
		OPT += budgetdict[adv][0]

	#print "OPT = ", OPT
	#print "ALG = ", ALG
	CR = float(ALG)/float(OPT)
	#print "Competitive Ratio: ", CR

	return CR


def processQueries(biddinginfofile, queriesfile, algorithm):

	budgetdict = getBudgetDict(biddinginfofile)
	biddict = getBidsDict(biddinginfofile)

	#print biddict
	revenue = 0

	file = open(queriesfile, 'r')

	for line in file:
		bidders = getBiddingAdvertisers(biddict, budgetdict, line.replace('\n', ''))

		#print "Processing", line, bidders
		if not bidders:
			continue
		else:
			if(algorithm == "msvv"):
				highBidder = getHighestMSSVAdvertiser(bidders)
			elif(algorithm == "balance"):
				highBidder = getHighestUnspentBalanceAdvertiser(bidders)
			else:
				highBidder = getHighestBiddingAdvertiser(bidders)
			#print 'allocating word ',  line, ' to ', highBidder[0]
			budgetdict[highBidder[0]][1] = budgetdict[highBidder[0]][1] - highBidder[1]
			revenue = revenue + highBidder[1]
			

	#print "Total Generated Revenue: ", revenue

	return revenue


#budgetdict = getBudgetDict('bidder_dataset.csv')
#biddict = getBidsDict('bidder_dataset.csv')
#print biddict

#bidders = getBiddingAdvertisers(biddict, budgetdict, 'google tablet')
#print "Bidders for Obama: ", bidders

#highBidder = getHighestBiddingAdvertiser(bidders)
#print "Highest Bidder: ", highBidder

#f = open('queries.txt', 'r')
#print f.readline()
#print f.readline()
#print f.readline()

#processMSSVQueries('bidder_dataset.csv', 'queries.txt')
#processGreedyQueries('bidder_dataset.csv', 'queries.txt')
#processUnspentBalanceQueries('bidder_dataset.csv', 'queries.txt')
#findCompetitiveRatio('bidder_dataset.csv', 'queries.txt', 'greedy')
#processQueries('bidder_dataset.csv', 'queries.txt', 'balance')

def main(argv):
	
	if(len(argv) > 0):
		algorithm = argv[0]
		
		if(algorithm in ["greedy", "msvv", "balance"]):
			revenue = processQueries('bidder_dataset.csv', 'queries.txt', algorithm)
			CR = findCompetitiveRatio('bidder_dataset.csv', 'queries.txt', algorithm)
			print "Algorithm: ", algorithm
			print "Revenue: ", revenue
			print "Competitive Ratio: ", CR
		else:
			print "This program only takes greedy, mssv or balance as argument"

	else:
		for algorithm in ["greedy", "msvv", "balance"]:
			revenue = processQueries('bidder_dataset.csv', 'queries.txt', algorithm)
			CR = findCompetitiveRatio('bidder_dataset.csv', 'queries.txt', algorithm)
			print "Algorithm: ", algorithm
			print "Revenue: ", round(revenue,2)
			print "Competitive Ratio: ", round(CR,2)

if __name__ == "__main__":
   main(sys.argv[1:])
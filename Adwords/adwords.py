import sys
import collections
import sklearn.naive_bayes
import sklearn.linear_model
import nltk
import random
import csv
import math
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



def processGreedyQueries(biddinginfofile, queriesfile):

	budgetdict = getBudgetDict(biddinginfofile)
	biddict = getBidsDict(biddinginfofile)

	print biddict
	revenue = 0

	file = open(queriesfile, 'r')

	for line in file:
		bidders = getBiddingAdvertisers(biddict, budgetdict, line.replace('\n', ''))

		print "Processing", line, bidders
		if not bidders:
			continue
		else:
			
			highBidder = getHighestBiddingAdvertiser(bidders)
			print 'allocating word ',  line, ' to ', highBidder[0]
			budgetdict[highBidder[0]][1] = budgetdict[highBidder[0]][1] - highBidder[1]
			revenue = revenue + highBidder[1]
			

	print "Total Generated Revenue: ", revenue

def processMSSVQueries(biddinginfofile, queriesfile):

	budgetdict = getBudgetDict(biddinginfofile)
	biddict = getBidsDict(biddinginfofile)

	print biddict
	revenue = 0

	file = open(queriesfile, 'r')

	for line in file:
		bidders = getBiddingAdvertisers(biddict, budgetdict, line.replace('\n', ''))

		print "Processing", line, bidders
		if not bidders:
			continue
		else:
			
			highBidder = getHighestMSSVAdvertiser(bidders)
			print 'allocating word ',  line, ' to ', highBidder[0]
			budgetdict[highBidder[0]][1] = budgetdict[highBidder[0]][1] - highBidder[1]
			revenue = revenue + highBidder[1]
			

	print "Total Generated Revenue: ", revenue


def processUnspentBalanceQueries(biddinginfofile, queriesfile):

	budgetdict = getBudgetDict(biddinginfofile)
	biddict = getBidsDict(biddinginfofile)

	print biddict
	revenue = 0

	file = open(queriesfile, 'r')

	for line in file:
		bidders = getBiddingAdvertisers(biddict, budgetdict, line.replace('\n', ''))

		print "Processing", line, bidders
		if not bidders:
			continue
		else:
			
			highBidder = getHighestUnspentBalanceAdvertiser(bidders)
			print 'allocating word ',  line, ' to ', highBidder[0]
			budgetdict[highBidder[0]][1] = budgetdict[highBidder[0]][1] - highBidder[1]
			revenue = revenue + highBidder[1]
			

	print "Total Generated Revenue: ", revenue


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
processUnspentBalanceQueries('bidder_dataset.csv', 'queries.txt')
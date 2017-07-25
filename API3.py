# SolarEdge API Program
#
# The purpose of this program is to automate the data collection
# process of the customer outreach project. Data comes from SolarEdge API.
#
# Link to API Manual: https://www.solaredge.com/sites/default/files/se_monitoring_api.pdf
# NOTE: Energy units are in Wh unless otherwise notated
#
# Ryan Biette 2017
# All rights reserved  
#

import urllib2, json, csv

# Make lists to add to 
idList = []
nameList = []
powList = []
energyList = []


## SITE ID, NAME, PEAKPOWER ##
print "Starting program..."
print "First API call..."

# Code block to ascertain count 
req = urllib2.Request("https://monitoringapi.solaredge.com/sites/list.json?api_key=INSERTAPIKEYHERE)")
response = urllib2.urlopen(req)
page = response.read()
data = json.loads(page)

# Count Var/ figure out how many times to call API
count = data["sites"]["count"]
numCalls = (count / 100) #no added "+1" because we already have the first 100

# Loop to add to lists
for x in xrange(0,100):
	idList.append(data["sites"]["site"][x]["id"]) 
	nameList.append(data["sites"]["site"][x]["name"])
	powList.append(data["sites"]["site"][x]["peakPower"])

# Loop to get through the rest of the sites lists 
index = 100
while numCalls > 1:
	url = "https://monitoringapi.solaredge.com/sites/list?startIndex=" + str(index) + "&api_key=INSERTAPIKEYHERE"
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	page = response.read()
	data = json.loads(page)
	for x in xrange(0,100):
		idList.append(data["sites"]["site"][x]["id"])
		nameList.append(data["sites"]["site"][x]["name"])
		powList.append(data["sites"]["site"][x]["peakPower"]) 

	numCalls = numCalls - 1
	index = index + 100

# Take care of the stragglers in the last call (i.e. the 21 of 721)
leftover = count - index
url = "https://monitoringapi.solaredge.com/sites/list?startIndex=" + str(index) + "&api_key=INSERTAPIKEYHERE"
req = urllib2.Request(url)
response = urllib2.urlopen(req)
page = response.read()
data = json.loads(page)
for x in xrange(0,leftover):
		idList.append(data["sites"]["site"][x]["id"])
		nameList.append(data["sites"]["site"][x]["name"])
		powList.append(data["sites"]["site"][x]["peakPower"]) 	

print "ID, name and power added"

## ENERGY ##

# Create string of all the site IDs for URL
sitesURL = str(idList[0])
for x in xrange(1,len(idList)):
	sitesURL = str(sitesURL) + "," + str(idList[x])

# Get energy 2016 data from SolarEdge (This part is pretty slow, just because it is a massive API call)
print "Starting bulk energy call..."

url3 = "https://monitoringapi.solaredge.com/sites/" + sitesURL + "/energy?timeUnit=YEAR&endDate=2016-12-31&startDate=2016-01-01&api_key=INSERTAPIKEYHERE"
req = urllib2.Request(url3)
response = urllib2.urlopen(req)
page = response.read()
data = json.loads(page)

# LOOP to take the energy values from page and put them in the list  
for x in xrange(0,count-1):
	toAdd = data["sitesEnergy"]["siteEnergyList"][x]["energyValues"]["values"][0]["value"]
	if toAdd is None:
		toAdd = 0	
	energyList.append(toAdd)

print "Bulk call completed, values added"

## PRODUCTION RATIOs ##
print "Calculating Production Ratios and culling data..."

prodRatioList = []
for x in xrange(0,count-1):
	prod = energyList[x]
	kW = powList[x]
	ratio = (prod/kW) / 1000	# Units of energy are in Wh so need to convert to 
	prodRatioList.append(ratio)

# Get rid of any production ratio sites with low ratios
newIDList = []
newNameList = []
newPowList = []
newEnergyList = []
newProdRatList = []
for x in xrange(0,len(prodRatioList)):
	if prodRatioList[x] > 999:
		newIDList.append(idList[x])
		newNameList.append(nameList[x])
		newPowList.append(powList[x])
		newEnergyList.append(energyList[x])
		newProdRatList.append(prodRatioList[x])

## ALL ## 
print "Writing to .csv"

# Writes each of the lists to the csv file, currently named test.csv
with open('test.csv', 'wb') as myfile:
	wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
	rows = zip(newNameList, newIDList, newPowList, newEnergyList, newProdRatList)
	for row in rows:
		wr.writerow(row)

print "Program complete!"
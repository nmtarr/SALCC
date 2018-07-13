# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 11:21:43 2018 by nmtarr

Description:  Get a crosswalked list of ncsgcn species (crosswalked to gap).
"""

import sys
sys.path.append('C:/Program Files (x86)/ArcGIS/Desktop10.4/bin64')
sys.path.append('C:/Program Files (x86)/ArcGIS/Desktop10.4/ArcPy')
sys.path.append('C:/Program Files (x86)/ArcGIS/Desktop10.4/ArcToolBox/Scripts')
sys.path.append('P:/Proj3/USGap/Scripts/GAPProduction')
sys.path.append('P:/Proj3/USGap/Scripts/')
import gapproduction as gp
import gapconfig as config
import pandas as pd
pd.set_option('display.width', 1000)

#### Get list of SGCN species from downloaded csv file.
# from https://www1.usgs.gov/csas/swap/state_list.html#state=North%20Carolina
sgcnCSV = "T:/SALCC/ncsgcn.csv"
BCBlist = pd.read_csv(sgcnCSV, sep="|")

# Filter out non-tetrapods
BCBlist2 = BCBlist[BCBlist['Taxonomic Group'].isin(['Birds', 'Reptiles', 
                   'Amphibians', 'Mammals'])]
print(BCBlist2.head(n=20))

# Filter out non-2015 species
BCBlist3 = BCBlist2[BCBlist2['Occurs in 2015 Data'] == 'yes']

# save 
BCBlist3.to_csv('T:/SALCC/ncsgcn2015TetrapodsBCB.csv')

####################################################
# Get a species code dictionary
gapcodeDict = gp.gapdb.Dict_SciNameToCode()

# Use scientific names to look up GAPcodes, note if there isn't a match
combinedList = BCBlist3.copy()
combinedList.set_index('Scientific Name Reported in State SWAP', inplace=True)
for x in combinedList.index:
    print(x)
    try:
        code = gapcodeDict[x]
    except:
        code = 'no_GAP_match'
        print(code)
    combinedList.loc[x, 'GAPCode'] = code
combinedList.reset_index(inplace=True)

# Isolate records that didn't match on sci name, then try to match on common
# name
nonmatches = combinedList[combinedList['GAPCode'] == 'no_GAP_match']

# Get a common name species code dictionary
d = {}
l = gp.gapdb.ListAllSpecies()
for i in l:
    try:
        com = gp.gapdb.NameCommon(i)
        if com in d.iterkeys():
            if i.endswith('x'):
                d[com] = i
            else:
                pass
        else:
            d[com] = i
    except:
        pass

combinedList.set_index('Common Name', inplace=True)
for x in combinedList.index:
    if combinedList.loc[x, 'GAPCode'] == 'no_GAP_match':
        try:
            code = d[x]
        except:
            code = 'no_GAP_match'
            print(code)
        combinedList.loc[x, 'GAPCode'] = code
        
combinedList.reset_index(inplace=True)
combinedList.set_index(['GAPCode'], inplace=True)
for x in combinedList.index:
    try:
        combinedList.loc[x, 'GAP_common_name'] = gp.gapdb.NameCommon(x)
        combinedList.loc[x, 'GAP_sci_name'] = gp.gapdb.NameSci(x)
        combinedList.loc[x, 'ITIS_TSN'] = gp.gapdb.Crosswalk[2]
    except:
        pass
combinedList.reset_index(inplace=True)
combinedList.to_csv("T:/SALCC/ncsgcn-gap_crosswalk.csv")
    
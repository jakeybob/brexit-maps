import fiona
import numpy as np
import pandas as pd
from shapely.geometry import shape, MultiPolygon
from shapely import speedups
from matplotlib.collections import PatchCollection
from descartes import PolygonPatch
import pickle
import mapMisc as mapMisc

if speedups.available:
    speedups.enable()


# load data
GBRpropertiesDF, NIpropertiesDF, GIBpropertiesDF, GBRdataDF, NIdataDF, GIBdataDF, GBRmp, NImp, GIBmp,\
GBRpolyCount, NIpolyCount, GIBpolyCount, bounds = mapMisc.loadData('data/allData.dat')


NIdata2write = NIdataDF.drop(['Area', 'Pct_Turnout', 'Pct_Remain', 'Pct_Leave', 'Rejected_Ballots'], axis=1)
NIdata2write['RemainPlusLeave'] = NIdata2write['Remain'] + NIdata2write['Leave']
NIdata2write['NoVote'] = NIdata2write['Electorate'] - NIdata2write['RemainPlusLeave']
NIdata2write.rename(columns={'Area_Code':'PC_ID'}, inplace=True)

print(NIdata2write)
NIdata2write.to_csv('NIdata.csv')


GBRdata2write = GBRdataDF.drop(['Area', 'Pct_Turnout', 'Pct_Remain', 'Pct_Leave', 'Rejected_Ballots', 'Region'], axis=1)
GBRdata2write['RemainPlusLeave'] = GBRdata2write['Remain'] + GBRdata2write['Leave']
GBRdata2write['NoVote'] = GBRdata2write['Electorate'] - GBRdata2write['RemainPlusLeave']
GBRdata2write.rename(columns={'Area_Code':'CODE'}, inplace=True)

print(GBRdata2write.head())
GBRdata2write.to_csv('GBRdata.csv')

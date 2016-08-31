import fiona
import numpy as np
import pandas as pd
from shapely.geometry import shape, MultiPolygon
from shapely import speedups
from matplotlib.collections import PatchCollection
from descartes import PolygonPatch
import pickle

if speedups.available:
    speedups.enable()

# location of data
refDataCSV = 'data/EU-referendum-result-data.csv'
refDataNICSV = 'data/NIrefData.csv' # data collated from www.eoni.org.uk
# http://www.eoni.org.uk/getmedia/fc176a12-39ee-46b6-8587-68b5b948762d/EU-REFERENDUM-2016-NORTHERN-IRELAND-COUNT-
# TOTALS-DECLARATION
# http://www.eoni.org.uk/getmedia/c371ecda-c0b7-4914-83ca-50d38b5ca8ea/EU-REFERENDUM-2016-CONSTITUENCY-COUNT-TOTALS
# http://www.eoni.org.uk/getmedia/65f3947d-90bf-4b3b-aaf0-2e5fa760e706/EU-REFERENDUM-2016-CONSTITUENCY-TURNOUT_1

GBRshpfile = 'data/boundaryline/district_borough_unitary_region.shp'
NIshpfile = 'data/OSNI_Open_Data_Largescale_Boundaries__Parliamentary_Constituencies_2008/' \
            'OSNI_Open_Data_Largescale_Boundaries__Parliamentary_Constituencies_2008.shp'   # NI shapefile from here:
# http://osni.spatial-ni.opendata.arcgis.com/datasets/563dc2ec3d9943428e3fe68966d40deb_3
GIBshpfile = 'data/GIB_adm/GIB_adm0.shp'    # http://www.diva-gis.org

def makePolyLists(collection):

    polyList = []
    polyCount = []

    for entry in collection:
        if entry['geometry']['type'] == 'Polygon':
            x = shape(entry['geometry'])
            polyList.append(x)
            polyCount.append(1)


        if entry['geometry']['type'] == 'MultiPolygon':
            x = shape(entry['geometry'])
            polyCount.append(len(x))

            for i, poly in enumerate(x):
                polyList.append(x[i])

    return polyList, polyCount



# convert and format csv data into dataframes
GBRdataDF = pd.read_csv(refDataCSV, sep=',', header=0, index_col=0)   # create dataframe
GBRdataDF.drop(['Region_Code', 'ExpectedBallots', 'Votes_Cast', 'Valid_Votes', 'No_official_mark',
                'Voting_for_both_answers', 'Writing_or_mark',
                'Unmarked_or_void', 'Pct_Rejected'], axis=1, inplace=True)  # drop unwanted bumf
GIBdataDF = GBRdataDF.loc[382]   # Gibraltar data
NItotalDF = GBRdataDF.loc[381]  # N.I. *as a whole* data
GBRdataDF.drop([381, 382], inplace=True)  # removing N. Ireland and Gibraltar so is just GBR
NIdataDF = pd.read_csv(refDataNICSV, sep=',', header=0, index_col=0)   # create dataframe
NIdataDF['Pct_Remain'] = (100.0 * NIdataDF.Remain)/(NIdataDF.Remain+NIdataDF.Leave)
NIdataDF['Pct_Leave'] = 100.0 - NIdataDF['Pct_Remain']


# create multipolygon objects from shapefiles
GBRcollection = fiona.open(GBRshpfile)
# GBRmp = MultiPolygon([shape(entry['geometry']) for entry in GBRcollection])   # create list of polygons from shapefile
GBRpolyList, GBRpolyCount = makePolyLists(GBRcollection)
GBRmp = MultiPolygon(GBRpolyList)

# map the referendum data to the areas in the shapefiles/multipolygon objects
areaProperties = []
for i, entry in enumerate(GBRcollection):
    areaCode = entry['properties']['CODE']
    turnOut = GBRdataDF[GBRdataDF['Area_Code'] == areaCode]['Pct_Turnout']
    pctLeave = GBRdataDF[GBRdataDF['Area_Code'] == areaCode]['Pct_Leave']
    pctRemain = GBRdataDF[GBRdataDF['Area_Code'] == areaCode]['Pct_Remain']

    areaProperties.append([i, turnOut.values, pctLeave.values, pctRemain.values])

# referendum data reordered to match order of polygons
GBRpropertiesDF = pd.DataFrame(areaProperties, columns=('id', 'Turnout', 'Leave', 'Remain'))



# as above but for NI

NIcollection = fiona.open(NIshpfile)
# NImp = MultiPolygon([shape(entry['geometry']) for entry in NIcollection])   # create list of polygons from shapefile
NIpolyList, NIpolyCount = makePolyLists(NIcollection)
NImp = MultiPolygon(NIpolyList)

areaProperties = []
for i, entry in enumerate(NIcollection):
    areaCode = entry['properties']['PC_ID']
    turnOut = NIdataDF[NIdataDF['Area_Code'] == areaCode]['Pct_Turnout']
    pctLeave = NIdataDF[NIdataDF['Area_Code'] == areaCode]['Pct_Leave']
    pctRemain = NIdataDF[NIdataDF['Area_Code'] == areaCode]['Pct_Remain']

    areaProperties.append([i, turnOut.values, pctLeave.values, pctRemain.values])

NIpropertiesDF = pd.DataFrame(areaProperties, columns=('id', 'Turnout', 'Leave', 'Remain'))




# as above but for GIB

GIBcollection = fiona.open(GIBshpfile)
# GIBmp = MultiPolygon([shape(entry['geometry']) for entry in GIBcollection])   # create list of polygons from shapefile
GIBpolyList, GIBpolyCount = makePolyLists(GIBcollection)
GIBmp = MultiPolygon(GIBpolyList)

areaProperties = []
areaProperties.append([1, GIBdataDF['Pct_Turnout'], GIBdataDF['Pct_Leave'], GIBdataDF['Pct_Remain']])
GIBpropertiesDF = pd.DataFrame(areaProperties, columns=('id', 'Turnout', 'Leave', 'Remain'))



# list of the map bounds (useful for plotting)
bounds = [GBRmp.bounds, NImp.bounds, GIBmp.bounds]


# save patches and properties etc

toSave = [GBRpropertiesDF, NIpropertiesDF, GIBpropertiesDF, GBRdataDF, NIdataDF, GIBdataDF, GBRmp, NImp, GIBmp, GBRpolyCount, NIpolyCount,
          GIBpolyCount, bounds]
outfile = open('data/allData.dat', 'wb')
pickle.dump(toSave, outfile)
outfile.close()

print('done')
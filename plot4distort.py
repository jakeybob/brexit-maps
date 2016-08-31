import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
import pandas as pd
import mapMisc as mapMisc
import numpy as np
import fiona
from shapely.geometry import shape, MultiPolygon
from shapely import speedups, affinity
if speedups.available:
    speedups.enable()
from sklearn import cluster


# load data
GBRpropertiesDF, NIpropertiesDF, GIBpropertiesDF, GBRdataDF, NIdataDF, GIBdataDF, GBRmp, NImp, GIBmp,\
GBRpolyCount, NIpolyCount, GIBpolyCount, bounds = mapMisc.loadData('data/allDataDistort.dat')

GBRshpfile = 'data/distorted/GBR/GBRremainPlusLeave.shp'
NIshpfile = 'data/distorted/NI/NIremainPlusLeave.shp'   # NI shapefile from here:
# http://osni.spatial-ni.opendata.arcgis.com/datasets/563dc2ec3d9943428e3fe68966d40deb_3
GIBshpfile = 'data/GIB_adm/GIB_adm0.shp'    # http://www.diva-gis.org



# scale the NI map properly, as Dorling distortion map is only scaled to itself, not GBR + NI as a whole
GBRpeopleRepresented = np.sum(GBRdataDF.Remain) + np.sum(GBRdataDF.Leave)
GBRpopDensity = GBRpeopleRepresented/GBRmp.area

NIpeopleRepresented = np.sum(NIdataDF.Remain) + np.sum(NIdataDF.Leave)
NIpopDensity = NIpeopleRepresented/NImp.area
NIscaleFactor = np.sqrt(NIpopDensity/GBRpopDensity)

NImp = affinity.scale(NImp, xfact=NIscaleFactor, yfact=NIscaleFactor, origin='center')
NIpopDensity = NIpeopleRepresented/NImp.area

# scale the GIB map properly, as Dorling distortion map is only scaled to itself, not GBR + GIB as a whole
GIBpeopleRepresented = np.sum(GIBdataDF.Remain) + np.sum(GIBdataDF.Leave)
GIBpopDensity = GIBpeopleRepresented/GIBmp.area
GIBscaleFactor = np.sqrt(GIBpopDensity/GBRpopDensity)

GIBmp = affinity.scale(GIBmp, xfact=GIBscaleFactor, yfact=GIBscaleFactor, origin='center')
GIBpopDensity = GIBpeopleRepresented/GIBmp.area



# calculate data to include the whole electorate
countryDFs = [GBRdataDF, NIdataDF, GIBdataDF]
newData = []
for i, country in enumerate(countryDFs):
    if isinstance(country, pd.DataFrame):
        country = country.assign(Pct_RemainOfElectorate = 100 * country['Remain']/country['Electorate'])
        country = country.assign(Pct_LeaveOfElectorate = 100 *country['Leave']/country['Electorate'])
        country = country.assign(Pct_Neither = 100 - (country['Pct_RemainOfElectorate'] + country['Pct_LeaveOfElectorate']))
        newData.append(country)
    else:  # for GIB, which is series, not dataframe
        country['Pct_RemainOfElectorate'] = 100 * country['Remain']/country['Electorate']
        country['Pct_LeaveOfElectorate'] = 100 * country['Leave'] / country['Electorate']
        country['Pct_Neither'] = 100 - (country['Pct_RemainOfElectorate'] + country['Pct_LeaveOfElectorate'])

GBRdataDF = newData[0]
NIdataDF = newData[1]



# fit clusters to data
allData = pd.concat([GBRdataDF, NIdataDF], axis=0)

d = allData[['Pct_LeaveOfElectorate', 'Pct_RemainOfElectorate']].as_matrix()
# d = np.vstack((d, [GIBdataDF.Pct_LeaveOfElectorate, GIBdataDF.Pct_RemainOfElectorate]))  # adds GIBdata to the end

k_means = cluster.KMeans(n_clusters=4, n_jobs=-2)
k_means.fit(d)


# add labels to GBR and NI data so we know which cluster each constituency belongs to
GBRdataDF['Cluster'] = k_means.labels_[0: np.shape(GBRdataDF)[0]]
NIdataDF['Cluster'] = k_means.labels_[np.shape(GBRdataDF)[0]: len(k_means.labels_)]



# split GBR data into Scotland, England and Wales so they can be plotted separately
scotDataDF = GBRdataDF.loc[lambda df: df.Region == 'Scotland', :]
walesDataDF = GBRdataDF.loc[lambda df: df.Region == 'Wales', :]
engDataDF = GBRdataDF.loc[lambda df: df.Region != 'Scotland', :]  # cludgy but what the hell
engDataDF = engDataDF.loc[lambda df: df.Region != 'Wales', :]


colour_list = ['#fdae61', '#abd9e9', '#2c7bb6', '#d7191c']  # from colorbrewer2.org




# plot new map
with fiona.open(GBRshpfile) as GBRcollection:  # ack, have to reorder the cluster labels to fit order of polygons in map.
    GBRlabels = []
    for i, entry in enumerate(GBRcollection):
        areaCode = entry['properties']['CODE']
        cluster = GBRdataDF[GBRdataDF['Area_Code'] == areaCode]['Cluster']
        GBRlabels.append(cluster.values)


with fiona.open(NIshpfile) as NIcollection:
    NIlabels = []
    for i, entry in enumerate(NIcollection):
        areaCode = entry['properties']['PC_ID']
        cluster = NIdataDF[NIdataDF['Area_Code'] == areaCode]['Cluster']
        NIlabels.append(cluster.values)


# k_means clustered will be numbered differently on each run, so need to rearrange colour list to get consistent plots
vals, indices = np.unique(GBRlabels, return_index=True)
sorted = vals[np.argsort(indices)]
shifted = [0]*len(indices)
for i, entry in enumerate(shifted):
    shifted[sorted[i]] = colour_list[i]
colour_list = shifted


# make the patch collections to plot
GBRpc = mapMisc.makePatchCollectionForClusterMap(GBRpolyCount, GBRlabels, GBRmp, colour_list, lw=0.3, ec='black')
NIpc = mapMisc.makePatchCollectionForClusterMap(NIpolyCount, NIlabels, NImp, colour_list, lw=0.3, ec='black')
NIpc.set_offset_position('data')
NIpc.set_offsets([-200000, 150000])  # offset obtained from the shapefiles x_0, y0 coords in their CRS


# plt map
fig = plt.figure(frameon=False)
plt.gcf().set_size_inches(24, 20, forward=True)
ax = fig.add_subplot(111)

minx, miny, maxx, maxy = bounds[0]  # width, height info etc, for plotting / bounds[0]=GBR, 1 = NI, 2 = GIB
w, h = maxx - minx, maxy - miny
ax.set_xlim(minx - 0.05 * w, maxx + 0.05 * w)
ax.set_ylim(miny - 0.05* h, maxy + 0.05 * h)
ax.set_aspect(1)
ax.set_xticks([])
ax.set_yticks([])
ax.axis('off')

ax.add_collection(GBRpc)
ax.add_collection(NIpc)

# add  boxes
boxx, boxy = 500000, 880000
ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor='#d7191c', linewidth=0.3))
ax.text(boxx+60000, boxy+16000, 'Zone 1', fontsize=16)

boxx, boxy = 500000, 800000
ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor='#fdae61', linewidth=0.3))
ax.text(boxx+60000, boxy+16000, 'Zone 2', fontsize=16)

boxx, boxy = 500000, 720000
ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor='#abd9e9', linewidth=0.3))
ax.text(boxx+60000, boxy+16000, 'Zone 3', fontsize=16)

boxx, boxy = 500000, 640000
ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor='#2c7bb6', linewidth=0.3))
ax.text(boxx+60000, boxy+16000, 'Zone 4', fontsize=16)


picPath = 'pics/4newZonesDistort.png'
plt.savefig(picPath, alpha=True, dpi=300, bbox_inches='tight', pad_inches=0, transparent=False)
mapMisc.saveWidthResizedpics(picPath, widths=[2500, 2040, 1400])  # recommended sizes for medium.com

# plt.show()
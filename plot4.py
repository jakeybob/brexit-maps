import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mapMisc as mapMisc
from sklearn import cluster
import fiona
import matplotlib.patches as patches
from matplotlib.lines import Line2D


GBRshpfile = 'data/boundaryline/district_borough_unitary_region.shp'
NIshpfile = 'data/OSNI_Open_Data_Largescale_Boundaries__Parliamentary_Constituencies_2008/' \
            'OSNI_Open_Data_Largescale_Boundaries__Parliamentary_Constituencies_2008.shp'   # NI shapefile from here:
# http://osni.spatial-ni.opendata.arcgis.com/datasets/563dc2ec3d9943428e3fe68966d40deb_3
GIBshpfile = 'data/GIB_adm/GIB_adm0.shp'    # http://www.diva-gis.org

# load data
GBRpropertiesDF, NIpropertiesDF, GIBpropertiesDF, GBRdataDF, NIdataDF, GIBdataDF, GBRmp, NImp, GIBmp,\
GBRpolyCount, NIpolyCount, GIBpolyCount, bounds = mapMisc.loadData('data/allData.dat')

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
# GBRpc = mapMisc.makePatchCollectionForClusterMap(GBRpolyCount, GBRlabels, GBRmp, colour_list, lw=0.3, ec='black')
# NIpc = mapMisc.makePatchCollectionForClusterMap(NIpolyCount, NIlabels, NImp, colour_list, lw=0.3, ec='black')
# NIpc.set_offset_position('data')
# NIpc.set_offsets([-200000, 150000])  # offset obtained from the shapefiles x_0, y0 coords in their CRS
#
#
# # plt map
# fig = plt.figure(frameon=False)
# plt.gcf().set_size_inches(24, 20, forward=True)
# ax = fig.add_subplot(111)
#
# minx, miny, maxx, maxy = bounds[0]  # width, height info etc, for plotting / bounds[0]=GBR, 1 = NI, 2 = GIB
# w, h = maxx - minx, maxy - miny
# ax.set_xlim(minx - 0.05 * w, maxx + 0.05 * w)
# ax.set_ylim(miny - 0.05* h, maxy + 0.05 * h)
# ax.set_aspect(1)
# ax.set_xticks([])
# ax.set_yticks([])
# ax.axis('off')
#
# ax.add_collection(GBRpc)
# ax.add_collection(NIpc)
#
# # add  boxes
# boxx, boxy = 500000, 880000
# ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor='#d7191c', linewidth=0.3))
# ax.text(boxx+60000, boxy+16000, 'Zone 1', fontsize=16)
#
# boxx, boxy = 500000, 800000
# ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor='#fdae61', linewidth=0.3))
# ax.text(boxx+60000, boxy+16000, 'Zone 2', fontsize=16)
#
# boxx, boxy = 500000, 720000
# ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor='#abd9e9', linewidth=0.3))
# ax.text(boxx+60000, boxy+16000, 'Zone 3', fontsize=16)
#
# boxx, boxy = 500000, 640000
# ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor='#2c7bb6', linewidth=0.3))
# ax.text(boxx+60000, boxy+16000, 'Zone 4', fontsize=16)
#
#
# picPath = 'pics/4newZones.png'
# plt.savefig(picPath, alpha=True, dpi=300, bbox_inches='tight', pad_inches=0, transparent=False)
# mapMisc.saveWidthResizedpics(picPath, widths=[2500, 2040, 1400])  # recommended sizes for medium.com

# plt.show()



# # plot2D scatter
markersize = 220
alpha = 0.9

fig = plt.figure(frameon=False, figsize=(15, 15), dpi=300)
ax = fig.add_subplot(111)
ax.set_xlabel('Leave %', fontweight='semibold', fontsize=25)
ax.set_ylabel('Remain %', fontweight='semibold', fontsize=25)
ax.set_xlim(10, 60)
ax.set_ylim(10, 60)
ax.set_aspect(1)
ax.tick_params(axis='both', labelsize=22)

# ax.scatter(d[:,0], d[:,1], c='black', marker='o', s=markersize, alpha=0.3)

# ax.scatter(engDataDF['Pct_LeaveOfElectorate'], engDataDF['Pct_RemainOfElectorate'], c='blue', marker='o', s=markersize, alpha=alpha)
# ax.scatter(scotDataDF['Pct_LeaveOfElectorate'], scotDataDF['Pct_RemainOfElectorate'], c='red', marker='o', s=markersize, alpha=alpha)
# ax.scatter(walesDataDF['Pct_LeaveOfElectorate'], walesDataDF['Pct_RemainOfElectorate'], c='green', marker='o', s=markersize, alpha=alpha)
# ax.scatter(NIdataDF['Pct_LeaveOfElectorate'], NIdataDF['Pct_RemainOfElectorate'], c='yellow', marker='o', s=markersize, alpha=alpha)
# ridiculous cludge to get circular legend markers
# line1 = Line2D(range(1), range(1), color="white", marker='o', markersize=32, markerfacecolor='blue', alpha=alpha)
# line2 = Line2D(range(1), range(1), color="white", marker='o', markersize=32, markerfacecolor='red', alpha=alpha)
# line3 = Line2D(range(1), range(1), color="white", marker='o', markersize=32, markerfacecolor='green', alpha=alpha)
# line4 = Line2D(range(1), range(1), color="white", marker='o', markersize=32,markerfacecolor='yellow', alpha=alpha)
#
# ax.legend((line1, line2, line3, line4),('England','Scotland', 'Wales', 'N.I.'), numpoints=1, loc=3, labelspacing=2, fontsize=30)


for i, index in enumerate(k_means.labels_):
    if index == 0:
        colour = colour_list[0]
    if index == 1:
        colour = colour_list[1]
    if index == 2:
        colour = colour_list[2]
    if index == 3:
        colour = colour_list[3]
    ax.scatter(d[i, 0], d[i, 1], c=colour, s=markersize, marker='o', alpha=alpha, color='#333333')

# ax.scatter(k_means.cluster_centers_[:, 0], k_means.cluster_centers_[:, 1], c='black', s=markersize+100, marker='*')

line1 = Line2D(range(1), range(1), color="white", marker='o', markersize=32, markerfacecolor='#fdae61', alpha=alpha)
line2 = Line2D(range(1), range(1), color="white", marker='o', markersize=32, markerfacecolor='#abd9e9', alpha=alpha)
line3 = Line2D(range(1), range(1), color="white", marker='o', markersize=32, markerfacecolor='#2c7bb6', alpha=alpha)
line4 = Line2D(range(1), range(1), color="white", marker='o', markersize=32, markerfacecolor='#d7191c', alpha=alpha)

ax.scatter([20.440092,  12.423790], [41.214333, 44.734015], c='black', s=markersize+20, marker='o')

ax.legend((line4, line1, line2, line3),('Zone 1','Zone 2', 'Zone 3', 'Zone 4'), numpoints=1, loc=3, labelspacing=2, fontsize=30)




picPath = 'pics/test.png'
plt.savefig(picPath, alpha=True, dpi=300, bbox_inches='tight', pad_inches=0, transparent=False)
# mapMisc.saveWidthResizedpics(picPath, widths=[2500, 2040, 1400])  # recommended sizes for medium.com

# plt.show()
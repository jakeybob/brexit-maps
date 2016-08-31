import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib as mpl
import mapMisc as mapMisc
import numpy as np
from shapely.geometry import shape, MultiPolygon
from shapely import speedups, affinity
if speedups.available:
    speedups.enable()

# load data
GBRpropertiesDF, NIpropertiesDF, GIBpropertiesDF, GBRdataDF, NIdataDF, GIBdataDF, GBRmp, NImp, GIBmp,\
GBRpolyCount, NIpolyCount, GIBpolyCount, bounds = mapMisc.loadData('data/allDataDistort.dat')

globalMin, globalMax = mapMisc.getMinMax([GBRpropertiesDF, NIpropertiesDF, GIBpropertiesDF], 'Remain')
GBR_NI_min, GBR_NI_max = mapMisc.getMinMax([GBRpropertiesDF, NIpropertiesDF], 'Remain') # use these values avoid GIB
                                                                                        # throwing things off


# define colourmap for plot
cmap = mpl.cm.get_cmap('viridis')
# norm = mpl.colors.Normalize(GBR_NI_min, GBR_NI_max)               # set min/max values of colourmap
norm = mpl.colors.Normalize(0, 100)                             # use this to set to 0-100 range
colour_generator = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)

# col = colour_generator.to_rgba(48.108158)


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



# alpha='turnout' to scale to turnout, lw, ec args are linewidth/edgecolor, binary=True plots binary map
GBRpc = mapMisc.makePatchCollection(GBRpolyCount, GBRpropertiesDF, GBRmp, colour_generator, alpha='turnout', lw=0.1, binary=False, ec='black')
NIpc = mapMisc.makePatchCollection(NIpolyCount, NIpropertiesDF, NImp, colour_generator, alpha='turnout', lw=0.1, binary=False, ec='black')
GIBpc = mapMisc.makePatchCollection(GIBpolyCount, GIBpropertiesDF, GIBmp, colour_generator, alpha='turnout', lw=0.1, binary=False, ec='black')
NIpc.set_offset_position('data')
NIpc.set_offsets([-200000, 150000])  # offset obtained from the shapefiles x_0, y0 coords in their CRS



# plot
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


# do separate inset graphic for GIB
# left, bottom, width, height = [0.35, 0.27, 0.015, 0.015]
# ax2 = fig.add_axes([left, bottom, width, height])
# for axis in ['top','bottom','left','right']:
#     ax2.spines[axis].set_linewidth(0.5)
#     ax2.spines[axis].set_color('#555555')
#
# minx, miny, maxx, maxy = bounds[0]  # width, height info etc, for plotting / bounds[0]=GBR, 1 = NI, 2 = GIB
# w, h = maxx - minx, maxy - miny
#
# ax2.set_xlim(minx - 0.5 * w, maxx + 0.5 * w)
# ax2.set_ylim(miny - 0.2* h, maxy + 0.2 * h)
# ax2.set_xticks([])
# ax2.set_yticks([])
#
# ax2.add_collection(GIBpc)
# ax2.set_aspect(1)



# # add colour bar
cbaxes = fig.add_axes([0.65, 0.42, 0.01, 0.43])  # [left, bottom, width, height]
colourbar_generator = colour_generator
colourbar_generator.set_array([0,0])  # array here just needs to be something iterable – norm and cmap are inherited
                                        # from colour_generator
# colourbar_generator.set_cmap(mpl.cm.get_cmap('jet'))  # change colourbar to jet map
cbar = fig.colorbar(colourbar_generator, cax=cbaxes, orientation='vertical')
cbar.ax.tick_params(labelsize=12)
cbar.set_label('Remain %', fontsize=16)


# add binary boxes
# boxx, boxy = 500000, 800000
# ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor=mapMisc.viridisYellow, linewidth=0.3))
# ax.text(boxx+60000, boxy+16000, 'Remain', fontsize=8)
#
# boxx, boxy = 500000, 720000
# ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor=mapMisc.viridisBlue, linewidth=0.3))
# ax.text(boxx+60000, boxy+16000, 'Leave', fontsize=8)


# boxx, boxy = 500000, 800000
# ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor=mapMisc.viridisYellow, linewidth=0.3))
# ax.text(boxx+60000, boxy+16000, 'Remain', fontsize=16)
#
# boxx, boxy = 500000, 720000
# ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor=mapMisc.viridisHalfwayGreen, linewidth=0.3))
# ax.text(boxx+60000, boxy+16000, 'Neither', fontsize=16)
#
# boxx, boxy = 500000, 640000
# ax.add_patch(patches.Rectangle((boxx, boxy),50000, 50000, facecolor=mapMisc.viridisBlue, linewidth=0.3))
# ax.text(boxx+60000, boxy+16000, 'Leave', fontsize=16)


# plt.show()
picPath = 'pics/distortAmbiv2.png'
plt.savefig(picPath, alpha=True, dpi=300, transparent=True, bbox_inches='tight', pad_inches=0, facecolor=mapMisc.viridisHalfwayGreen)
# plt.savefig(picPath, alpha=True, dpi=300, bbox_inches='tight', pad_inches=0, transparent=False)
mapMisc.saveWidthResizedpics(picPath, widths=[2500, 2040, 1400])  # recommended sizes for medium.com

print('done')
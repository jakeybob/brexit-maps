import numpy as np
import matplotlib.pyplot as plt
import mapMisc as mapMisc
import pandas as pd
import matplotlib.patches as patches
from matplotlib import gridspec



refDataCSV = 'data/EU-referendum-result-data.csv'
refDataNICSV = 'data/NIrefData.csv'

# unfortunately need to do some data munging to get the data for these plots back

# load data
GBRpropertiesDF, NIpropertiesDF, GIBpropertiesDF, GBRdataDF, NIdataDF, GIBdataDF, GBRmp, NImp, GIBmp,\
GBRpolyCount, NIpolyCount, GIBpolyCount, bounds = mapMisc.loadData('data/allData.dat')


# split GBR data into Scotland, England and Wales
scotDataDF = GBRdataDF.loc[lambda df: df.Region == 'Scotland', :]
walesDataDF = GBRdataDF.loc[lambda df: df.Region == 'Wales', :]
engDataDF = GBRdataDF.loc[lambda df: df.Region != 'Scotland', :]  # cludgy but what the hell
engDataDF = engDataDF.loc[lambda df: df.Region != 'Wales', :]

countryDFs = [engDataDF, scotDataDF, walesDataDF, NIdataDF, GIBdataDF]

data = np.zeros((6, 8))

for i, entry in enumerate(countryDFs):
    remainTotal = entry['Remain'].sum()
    leaveTotal = entry['Leave'].sum()
    electorateTotal = entry['Electorate'].sum()

    remainVotersPct = 100.0 * remainTotal/(remainTotal + leaveTotal)
    leaveVotersPct = 100.0 - remainVotersPct

    remainOfElectoratePct = 100.0 * remainTotal / electorateTotal
    leaveOfElectoratePct = 100.0 * leaveTotal / electorateTotal
    neitherPct = 100.0 - (remainOfElectoratePct + leaveOfElectoratePct)

    data[i, 0] = remainTotal
    data[i, 1] = leaveTotal
    data[i, 2] = electorateTotal
    data[i, 3] = remainVotersPct
    data[i, 4] = leaveVotersPct
    data[i, 5] = remainOfElectoratePct
    data[i, 6] = leaveOfElectoratePct
    data[i, 7] = neitherPct

data[5, 0] = np.sum(data[:, 0])
data[5, 1] = np.sum(data[:, 1])
data[5, 2] = np.sum(data[:, 2])

data[5, 3] = 100.0 * data[5, 0] / (data[5, 0] + data[5, 1])
data[5, 4] = 100.0 - data[5, 3]

data[5, 5] = 100.0 * data[5, 0] / data[5, 2]
data[5, 6] = 100.0 * data[5, 1] / data[5, 2]
data[5, 7] = 100.0 - (data[5, 5] + data[5, 6])


resultsDF = pd.DataFrame(data, index=['England', 'Scotland', 'Wales', 'N. Ireland', 'Gibraltar', 'UK'],
                    columns=['remainTotal', 'leaveTotal', 'electorateTotal', 'remainVotersPct', 'leaveVotersPct',
                             'remainOfElectoratePct', 'leaveOfElectoratePct','neitherPct'])


area = ['UK', 'England', 'Scotland', 'Wales', 'N. Ireland', 'Gibraltar']



segments = 2
dataToPlot = np.zeros((len(area), segments))
for i, country in enumerate(area):
    dataToPlot[i, 0] = resultsDF['leaveVotersPct'][country]
    dataToPlot[i, 1] = resultsDF['remainVotersPct'][country]

data = np.transpose(dataToPlot)





fig = plt.figure(frameon=False, figsize=(13, 18))
gs = gridspec.GridSpec(2, 2, width_ratios=[1, 0.08], height_ratios=[1, 1])
gs.update(wspace=0, hspace=0.4)

ax1 = fig.add_subplot(gs[0])
axm1 = fig.add_subplot(gs[1], sharey=ax1, frameon=False)
ax2 = fig.add_subplot(gs[2], sharex=ax1)
axm2 = fig.add_subplot(gs[3], sharey=ax2, frameon=False)



for i, entry in enumerate(list(reversed(area))):
    axm1.text(0.5, i+1, entry, ha='left', va='center', color='black', weight='bold', fontsize=20)
    axm2.text(0.5, i + 1, entry, ha='left', va='center', color='black', weight='bold', fontsize=20)
axm1.set_xticks([])
axm1.set_yticks([])
axm1.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    width=10,
    length=0)
axm2.set_xticks([])
axm2.set_yticks([])
axm2.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    width=10,
    length=0)



colours = [mapMisc.viridisBlue, mapMisc.viridisYellow]
patch_handles = []
left = np.zeros(len(area))
y_pos = np.arange(len(area), 0, -1)

for i, entry in enumerate(data):
    patch_handles.append(ax1.barh(y_pos, entry, color=colours[i%len(colours)], align='center', left=left, linewidth=0.5))
    left = left + entry
for j in range(len(patch_handles)):
    for i, patch in enumerate(patch_handles[j].get_children()):
        bl = patch.get_xy()
        x = 0.5*patch.get_width() + bl[0]
        y = 0.5*patch.get_height() + bl[1]
        if j == 0:
            textCol = 'white'
            if i == 5:
                textCol = [0,0,0,0]
        else:
            textCol = 'black'

        value = '{:.1%}'.format(data[j, i]/100)
        if value[-2] == '0':
            value = '{:.0%}'.format(data[j, i] / 100)

        ax1.text(x, y, value, ha='center', va='center', color=textCol, weight='semibold', fontsize=14)

ax1.set_yticks(y_pos)
ax1.set_yticklabels([])
ax1.set_xticks([])

ax1.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    width=10,
    length=0)
ax1.plot((50, 50), (0, 7), 'k-', zorder=0, lw=0.5)
ax1.set_title('Voter distribution\n', fontweight='semibold', fontsize=18)

legendHandles = [patches.Patch(color=mapMisc.viridisBlue, label='leave'), patches.Patch(color=mapMisc.viridisYellow, label='remain'), ]
ax1.legend(handles=legendHandles, bbox_to_anchor=(-0.25, 0.5, 0.1, 0.52), loc=2)


# plt.show()


segments = 3
dataToPlot = np.zeros((len(area), segments))

for i, country in enumerate(area):
    dataToPlot[i, 0] = resultsDF['leaveOfElectoratePct'][country]
    dataToPlot[i, 1] = resultsDF['neitherPct'][country]
    dataToPlot[i, 2] = resultsDF['remainOfElectoratePct'][country]

data = np.transpose(dataToPlot)

colours = [mapMisc.viridisBlue, mapMisc.viridisHalfwayGreen, mapMisc.viridisYellow]
patch_handles = []
left = np.zeros(len(area))
y_pos = np.arange(len(area), 0, -1)

for i, entry in enumerate(data):
    patch_handles.append(ax2.barh(y_pos, entry, color=colours[i%len(colours)], align='center', left=left, linewidth=0.5))
    left = left + entry

for j in range(len(patch_handles)):
    for i, patch in enumerate(patch_handles[j].get_children()):
        bl = patch.get_xy()
        x = 0.5*patch.get_width() + bl[0]
        y = 0.5*patch.get_height() + bl[1]
        if j == 0:
            textCol = 'white'
            if i == 5:
                textCol = [0,0,0,0]
        else:
            textCol = 'black'

        value = '{:.1%}'.format(data[j, i]/100)
        if value[-2] == '0':
            value = '{:.0%}'.format(data[j, i] / 100)

        ax2.text(x, y, value, ha='center', va='center', color=textCol, weight='semibold', fontsize=14)


ax2.set_yticks(y_pos)
for i, entry in enumerate(area):
    area[i] = area[i] + '   .'
ax2.set_yticklabels([])

ax2.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    width=10,
    length=0)


ax2.set_xticks([])
ax2.set_title('Electorate distribution\n', fontweight='semibold', fontsize=18)
ax2.plot((50, 50), (0, 7), 'k-', zorder=0, lw=0.5)
legendHandles = [patches.Patch(color=mapMisc.viridisBlue, label='leave'), patches.Patch(color=mapMisc.viridisHalfwayGreen, label='no vote'), patches.Patch(color=mapMisc.viridisYellow, label='remain'), ]
legend = ax2.legend(handles=legendHandles, bbox_to_anchor=(-0.25, 0.5, 0.1, 0.52), loc=2)



# plt.show()
picPath = 'pics/chartNew.png'
plt.savefig(picPath, alpha=True, dpi=300, bbox_inches='tight', pad_inches=0.1, transparent=False)
# mapMisc.saveWidthResizedpics(picPath, widths=[2500, 2040, 1400])  # recommended sizes for medium.com
#################################################################



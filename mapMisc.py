import pickle
from matplotlib.collections import PatchCollection
from descartes import PolygonPatch
import numpy as np
import os
from PIL import Image  # see 'pillow' for python3+

# some useful stuff for plotting
euroBlue = '#000099'    # EU flag background blue
euroYellow = '#ffcc00'  # EU flag star yellow
viridisBlue = (0.26700400000000002, 0.0048739999999999999, 0.32941500000000001, 1.0)
viridisYellow = (0.99324800000000002, 0.90615699999999999, 0.14393600000000001, 1.0)
viridisHalfwayGreen = (0.12756799999999999, 0.56694900000000004, 0.55055600000000005, 1.0)

def loadData(filepath):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    #
    # GBRpropertiesDF = data[0]
    # NIpropertiesDF = data[1]
    # GIBproperties = data[2]
    # GBRpatches = data[3]
    # NIpatches = data[4]
    # GIBpatches = data[5]
    # bounds = data[6]

    return data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], \
           data[11], data[12]

def makePatchCollection(polyCount, areaPropertiesDF, mp, colour_generator, **kwargs):

    scale2turnout = False
    try:
        alphaVal = kwargs['alpha']  # has user passed an alpha val?
        if alphaVal == 'turnout':
            scale2turnout = True
    except KeyError:    # if no alpha included, assume alpha = 1
        alphaVal = 1


    try:
        lwVal = kwargs['lw']    # has user passed a linewidth val?
    except KeyError:
        lwVal = 0               # if not default to zero



    try:
        ecVal = kwargs['ec']    # has user passed an edgecolour val?
    except KeyError:
        ecVal = '#555555'              # if not default to grey


    try:
        drawBinaryMap = kwargs['binary']
    except KeyError:
        drawBinaryMap = False

    try:
        drawNoVoteBinaryMap = kwargs['novotebinary']
    except KeyError:
        drawNoVoteBinaryMap = False

    try:
        overrideCol = kwargs['overrideColour']
        overrideFillColour = True

    except KeyError:
        overrideFillColour = False


    patches = []

    patchNumber = 0
    for region, polyNumber in enumerate(polyCount):

        fillColour = colour_generator.to_rgba(areaPropertiesDF['Remain'][region])
        # fillColour = colour_generator.to_rgba(areaPropertiesDF['Remain'][region]*(areaPropertiesDF['Turnout'][region]/100.0))
        if len(fillColour) == 1:
            fillColour = fillColour[0]
        if overrideFillColour:
            fillColour = overrideCol


        if scale2turnout:
            alphaVal = areaPropertiesDF['Turnout'][region]/100.0


        if drawBinaryMap:
            if areaPropertiesDF['Remain'][region] < 50:
                fillColour = colour_generator.to_rgba(0)
            else:
                fillColour = colour_generator.to_rgba(100)

        #########           # set binary = True and uncomment this section for trinary map
            # majRemain = False
            # majLeave = False
            # if areaPropertiesDF['Remain'][region]*(areaPropertiesDF['Turnout'][region]/100.0) > 50:
            #     fillColour = colour_generator.to_rgba(100)
            #     majRemain = True
            # if areaPropertiesDF['Leave'][region] * (areaPropertiesDF['Turnout'][region] / 100.0) > 50:
            #     fillColour = colour_generator.to_rgba(0)
            #     majLeave = True
            # if not majRemain and not majLeave:
            #     fillColour = colour_generator.to_rgba(50)
        #########


        if drawNoVoteBinaryMap:
            remainPctofElec = areaPropertiesDF['Remain'][region] * (areaPropertiesDF['Turnout'][region] / 100.0)
            leavePctofElec = areaPropertiesDF['Leave'][region] * (areaPropertiesDF['Turnout'][region] / 100.0)
            noVotes = 100 - areaPropertiesDF['Turnout'][region]

            dataVec = [remainPctofElec, leavePctofElec, noVotes]
            whichMax = np.argmax(dataVec)


            if whichMax == 0:
                fillColour = colour_generator.to_rgba(100)
            if whichMax == 1:
                fillColour = colour_generator.to_rgba(0)
            if whichMax == 2:
                fillColour = colour_generator.to_rgba(50)




        if polyNumber == 1:
            patches.append(PolygonPatch(mp[patchNumber], fc=fillColour, ec=ecVal, lw=lwVal, alpha=alphaVal, zorder=1))
            patchNumber = patchNumber + 1
        else:
            for i in range(polyNumber):
                patches.append(PolygonPatch(mp[patchNumber], fc=fillColour, ec=ecVal, lw=lwVal, alpha=alphaVal, zorder=1))
                patchNumber = patchNumber + 1

    p = PatchCollection(patches, match_original=True)


    return p

def getMinMax(dfList, key):

    minList = []
    maxList = []

    for entry in dfList:
        minList.append(np.min(entry[key]))
        maxList.append(np.max(entry[key]))

    min = np.min(minList)
    max = np.max(maxList)


    try:                        # if values returned as arrays, convert to scalar
        len(min)
        min = min[0]
    except:
        None

    try:
        len(max)
        max = max[0]
    except:
        None


    return min, max

def makePatchCollectionForClusterMap(polyCount, listOfLabels, mp, colour_list, **kwargs):


    try:
        lwVal = kwargs['lw']    # has user passed a linewidth val?
    except KeyError:
        lwVal = 0               # if not default to zero

    try:
        ecVal = kwargs['ec']    # has user passed an edgecolour val?
    except KeyError:
        ecVal = '#555555'              # if not default to grey



    patches = []
    patchNumber = 0
    for region, polyNumber in enumerate(polyCount):

        fillColour = colour_list[listOfLabels[region]]
        if len(fillColour) == 1:
            fillColour = fillColour[0]

        if polyNumber == 1:
            patches.append(PolygonPatch(mp[patchNumber], fc=fillColour, ec=ecVal, lw=lwVal, zorder=1))
            patchNumber = patchNumber + 1
        else:
            for i in range(polyNumber):
                patches.append(PolygonPatch(mp[patchNumber], fc=fillColour, ec=ecVal, lw=lwVal, zorder=1))
                patchNumber = patchNumber + 1

    p = PatchCollection(patches, match_original=True)


    return p

def saveWidthResizedpics(origPic, widths):
    """Saves picture as png in same folder at 3 different width sizes, with aspect ratio preserved
    widths should be a list of integer pixel sizes, e.g. widths = [200, 400, 800]
    """

    if os.path.isabs(origPic):
        origPic = origPic[1:]       # delete slash if present at start of path


    origPicPath, origPicFilename = os.path.split(os.path.realpath(origPic))
    origPicName, origPicExt = os.path.splitext(origPicFilename)


    im = Image.open(origPic)
    imWidth = im.size[0]
    imHeight = im.size[1]
    imAspect = imWidth/imHeight



    for width in widths:

        newHeight = int(width/imAspect)
        im = im.resize((width, newHeight), resample=Image.LANCZOS)
        outPic = origPicPath + os.sep + origPicName + '-' + str(width) + origPicExt
        im.save(outPic)



    return None



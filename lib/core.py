from __future__ import print_function
import numpy

# Utilities Classes

class Input(object):
    def __init__(self, index, elts_corners, lats, lons):
        self.index = index
        self.elts_corners = elts_corners
        self.lats =lats
        self.lons = lons

# Utilities Functions
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

def isIntersecting(lats, lons):
    for i in range(len(lats)-2):
        i_Pts1 = (lons[i], lats[i])
        i_Pts2 = (lons[i+1], lats[i+1])
        line_i = (i_Pts1, i_Pts2)
        for j in range(i+1,len(lats)):
            j_Pts1  = (lons[j], lats[j])
            if j == len(lats)-1:
                j_Pts2 = (lons[0], lats[0])
            else:
                j_Pts2 = (lons[j+1], lats[j+1])
            line_j = (j_Pts1, j_Pts2)
            Pts = line_intersection(line_i, line_j)
            if Pts is None:
                continue
            else:
                x, y = Pts
            mn = min(lons[i],lons[i+1])
            mx = max(lons[i],lons[i+1])
            if (mn < x) and (x < mx) and not numpy.allclose(mn,x) and not numpy.allclose(x,mx):
                #print("Pts:",Pts,mn,mx)
                return 1
    return 0

def clockWise(pts,showPoints = False):
    n = pts.shape[-1]
    if showPoints: print(pts,pts.shape)
    clockwise = 0 
    for i in range(n):
        if i == n-1:
            j=0
        else:
            j=i+1
        if showPoints: print(i,j,pts[:,i])
        clockwise += (pts[0,j]+pts[0,i])*(pts[1,j]-pts[1,i])
    if showPoints: print("Result:",clockwise)
    if clockwise < 0:
        return False
    else:
        return True

def corners(param):
    index = param.index
    ec = param.elts_corners
    lats = param.lats
    lons =param.lons
    cells_indices = numpy.argwhere(ec==(index+1))[:,1]
    lats_corners = []
    lons_corners = []
    saved_lats = []
    saved_lons = []
    for i in cells_indices:
        select = ec[...,i]-1
        lat = lats[select]
        lon = lons[select].tolist()
        counter = 0
        while(max(lon)-min(lon))>181. and counter<5:
            lon[lon.index(min(lon))]=360.-lon[lon.index(min(lon))]
            counter+=1
        if counter>8:
            lon = lons[select]

        saved_lats.append(lat)
        saved_lons.append(lon)
        lats_corners.append(numpy.average(lat))
        lons_corners.append(numpy.average(lon))
    if len(lats_corners)==3:  # special cases
        lats_corners.append(lats_corners[-1])
        lons_corners.append(lons_corners[-1])

    # Need to do the 181 magic again here!
    counter = 0
    while(max(lons_corners)-min(lons_corners)>181.) and counter<8:
        counter+=1
        lons_corners[lons_corners.index(min(lons_corners))] += 360.
    pts = numpy.array([lats_corners, lons_corners])
    if isIntersecting(lats_corners, lons_corners):
        lats_corners2 = lats_corners
        lons_corners2 = lons_corners
        tmp = lats_corners2[2]
        lats_corners2[2] = lats_corners2[1]
        lats_corners2[1] = tmp
        tmp = lons_corners2[2]
        lons_corners2[2] = lons_corners2[1]
        lons_corners2[1] = tmp
        if isIntersecting(lats_corners2, lons_corners2):
            tmp = lats_corners[2]
            lats_corners[2] = lats_corners[3]
            lats_corners[3] = tmp
            tmp = lons_corners[2]
            lons_corners[2] = lons_corners[3]
            lons_corners[3] = tmp
        else:
            lons_corners = lons_corners2
            lats_corners = lats_corners2

    #if max(lons_corners)<87. and min(lons_corners)>85 and max(lats_corners)<-44 and min(lats_corners)>-45.5:
    #    print("BAD?:",zip(lons_corners, lats_corners))
    #if not clockWise(pts):
    #    lats_corners = lats_corners[::-1]
    #    lons_corners = lons_corners[::-1]
    return index, lats_corners, lons_corners



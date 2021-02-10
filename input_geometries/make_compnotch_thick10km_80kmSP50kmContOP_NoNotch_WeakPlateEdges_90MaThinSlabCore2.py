#!/usr/bin/env python 
import sys
import numpy, scipy, scipy.special

# box dimensions (i.e. "extent" in ASPECT input)
xmin=0;xmax=11600.e3;
ymin=0;ymax=2900.e3;
# number of cells, (i.e. "number of repetitions" in ASPECT input)
xnum=int(5800/2)
ynum=int(1450/2)

x_gap = 1550.e3; 
x_SP  = 6000.e3; 
y_crust = 10.e3; 
depth_notch  = 150e3;
radius_outer = 250e3;
slab_dip = 70.;
OPthick = 50.e3;
SPthick = 80.e3;

ridge_extent = 1000.e3;
age_ma=90;
age=age_ma*1e6*365*24*60*60;
Tmax = 1694.5; Tmin = 273.;
Tcutoff = 1400.;
k = 1e-6


# refinement in y-direction
ybound = 250.e3    # depth of refinement boundary
num_refine = 250  # number of grid points in refined (upper) layer
lower_lowres = numpy.linspace(0,ymax-ybound,ynum+1-num_refine)
upper_highres = numpy.linspace(ymax-ybound,ymax,1+num_refine)
yvals = numpy.concatenate((lower_lowres, upper_highres[1:]), axis=0)
#print "lower vertical res = %.2f km" % ((yvals[1]-yvals[0])/1.e3)
#print "higher vertical res = %.2f km" % ((yvals[ynum]-yvals[ynum-1])/1.e3)


No_nodes= (xnum + 1) * (ynum + 1)
C=numpy.zeros([No_nodes,6],float)
 
ind=0

# z at which T = 950 K
depth_T = 2*numpy.sqrt(k*age)*scipy.special.erfcinv((Tmax-850.)/(Tmax-Tmin))
#print depth_T/1.e3

for j in range(ynum + 1): 
    for i in range(xnum + 1):

        x = xmin + i * ((xmax - xmin)/xnum)
        y = yvals[j]

        C[ind,0] = x
        C[ind,1] = y

        # crust tracers
        if x > (x_gap) and x <= (x_gap + x_SP - radius_outer) and y > (ymax - y_crust):
            C[ind,2]=1
        elif x > (x_gap + x_SP - radius_outer) and x < (x_gap + x_SP):
            x1 = x_gap + x_SP - radius_outer; 
            y1 = ymax - radius_outer;
            if ((x-x1)**2 + (y-y1)**2) < radius_outer**2 and ((x-x1)**2 + (y-y1)**2) >= (radius_outer-y_crust)**2 and y > (ymax - depth_notch): 
                angle=numpy.arctan((y-y1)/(x-x1));
                if angle > numpy.radians(90. - slab_dip):
                   C[ind,2]=1


        # OP tracers
        if  C[ind,2] != 1:
            if x > (x_gap + x_SP - radius_outer) and x < (x_gap + x_SP):
                x1 = x_gap + x_SP - radius_outer; 
                y1 = ymax - radius_outer;
                if ((x-x1)**2 + (y-y1)**2) >= radius_outer**2 and y > (ymax - OPthick): 
                    C[ind,4]= 1
            if  x >= (x_gap + x_SP) and x < (xmax - x_gap) and y > (ymax - OPthick): 
                    C[ind,4]= 1



        # weak plate edge tracers
        if C[ind,2] != 1 and C[ind,4] != 1:
            if x > (x_gap - 75.e3) and x < (x_gap) and y > (ymax - 75.e3):
                C[ind,3]=1
            if x > (xmax - x_gap) and x < (xmax - x_gap + 75.e3) and y > (ymax - 75.e3):
                C[ind,3]=1


        ind=ind+1;

# write to file
f= open("text_files/compnotch_thick10km_80km50kmContOP_NoNotch_WeakPlateEdges_90MaThinSlabCore2.txt","w+")
f.write("# POINTS: %s %s\n" % (str(xnum+1),str(ynum+1)))
f.write("# Columns: x y composition1 composition2 composition3 composition4\n")
for k in range(0,ind):
    f.write("%.6f %.6f %.2f %.2f %.2f %.2f\n" % (C[k,0],C[k,1],C[k,2],C[k,3],C[k,4],C[k,5]))
f.close() 


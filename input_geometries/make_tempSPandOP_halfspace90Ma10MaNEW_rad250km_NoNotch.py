#!/usr/bin/env python 

import sys
import numpy as np
import scipy
import scipy.special

# box dimensions (i.e. "extent" in ASPECT input)
xmin=0;xmax=11600.e3;
ymin=0;ymax=2900.e3;
# number of cells, (i.e. "number of repetitions" in ASPECT input)
xnum=int(5800/2)
ynum=int(1450/2)

x_gap = 1550.e3; 
x_SP  = 6000.e3; 
depth_notch  = 200e3;
radius_outer = 250e3;
Tmax = 1694.5; Tmin = 273.;
slab_dip = 70.;

# refinement in y-direction
ybound = 250.e3    # depth of refinement boundary
num_refine = 250  # number of grid points in refined (upper) layer
lower_lowres = np.linspace(0,ymax-ybound,ynum+1-num_refine)
upper_highres = np.linspace(ymax-ybound,ymax,1+num_refine)
yvals = np.concatenate((lower_lowres, upper_highres[1:]), axis=0)
#print "lower vertical res = %.2f km" % ((yvals[1]-yvals[0])/1.e3)
#print "higher vertical res = %.2f km" % ((yvals[ynum]-yvals[ynum-1])/1.e3)

age_ma=90;
age=age_ma*1e6*365*24*60*60;
age_op_ma=10;
age_op=age_op_ma*1e6*365*24*60*60;
ridge_extent = 1000.e3;
k = 1e-6

No_nodes= (xnum + 1) * (ynum + 1)
T=np.zeros([No_nodes,3],float)
 
ind=0

for j in range(ynum + 1): 
    for i in range(xnum + 1):

        x = xmin + i * ((xmax - xmin)/xnum)
        y = yvals[j]

        T[ind,0] = x
        T[ind,1] = y
        T[ind,2] = Tmax

        if x > (x_gap) and x <= (x_gap + ridge_extent):
            age_ridge = (x - x_gap) * (age/ridge_extent)
            erf_term=(ymax-y)/(2*np.sqrt(k*age_ridge))
            T[ind,2]='%.5f'  %   (Tmax - (Tmax - Tmin)*scipy.special.erfc(erf_term))
        elif x > (x_gap + ridge_extent) and x <= (x_gap + x_SP - radius_outer):
            erf_term=(ymax-y)/(2*np.sqrt(k*age))
            T[ind,2]='%.5f'  %   (Tmax - (Tmax - Tmin)*scipy.special.erfc(erf_term))
        elif x >= (x_gap + x_SP) and x < (xmax - x_gap):
            erf_term=(ymax-y)/(2*np.sqrt(k*age_op))
            T[ind,2]='%.5f'  %   (Tmax - (Tmax - Tmin)*scipy.special.erfc(erf_term))
                
        if x > (x_gap + x_SP - radius_outer) and x < (x_gap + x_SP):
            x1 = x_gap + x_SP - radius_outer; 
            y1 = ymax - radius_outer;
            if ((x-x1)**2 + (y-y1)**2) < radius_outer**2 and y > (ymax - depth_notch): 
                erf_term=(ymax-y)/(2*np.sqrt(k*age))
                T[ind,2]='%.5f'  %   (Tmax - (Tmax - Tmin)*scipy.special.erfc(erf_term))
            elif ((x-x1)**2 + (y-y1)**2) >= radius_outer**2 and y > (ymax - depth_notch): 
                erf_term=(ymax-y)/(2*np.sqrt(k*age_op))
                T[ind,2]='%.5f'  %   (Tmax - (Tmax - Tmin)*scipy.special.erfc(erf_term))

        ind=ind+1;
 
# write to file
f= open("text_files/tempSPandOP_halfspace90Ma10MaNEW_rad250km_SlabT_NoNotch.txt","w+")
f.write("# POINTS: %s %s\n" % (str(xnum+1),str(ynum+1)))
f.write("# Columns: x y temperature\n")
for k in range(0,ind):
    f.write("%.6f %.6f %.6f\n" % (T[k,0],T[k,1],T[k,2]))
f.close() 


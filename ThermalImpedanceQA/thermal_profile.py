#!/usr/bin/env python

"""
thermal_profile.py

Author: Arianna Garcia Caffaro (Yale University)
About: This code plots the stave's thermal profile ignoring the end of the stave where the pipes loop around.  It gets the termal profile by fitting each pixel slice, tranverse to the  top and bottom pipes, to gaussians and using the gaussian amplitude (max temp) of each slice to plot the thermal profile. 

"""

import logging
import numpy as np
import scipy as sp
from scipy import optimize
import matplotlib.pyplot as plt

d = np.load("stave_cut.npy")
d_og = np.load("stave_og.npy")
#get rid of turn pipe data
#data = d[:,110:]
debug = False

def loop_cutter(stave):
    #find where the pipe loops around and cut the end loop 
    #cut point corresponds to the first point where Temp equals the mean T throughout stave
    #get slice of 1 pixel though the middle of stave
    s_mid = stave[stave.shape[0]//2:stave.shape[0]//2+1,:]
    #get y, x values and max for array 
    x_m = np.arange(s_mid.shape[1])
    x = x_m.reshape((s_mid.shape[1],1))
    x_max = x[np.argmax(s_mid)]
    y = s_mid.T
    y_mean = y.mean()
    #x value of first instance of y = y_mean
    x_flat = int(x[np.argmin([(x<x_max)|((x>=x_max)&(y>y_mean))])])
    
    #cut stave
    s_cut = stave[:,x_flat:]
    
    return s_cut
     

def gaus_finder(stave, region, i):
    ###define gaussian baseline and data for top or bottom pipe
    if region == "top":
        d_top = stave[:stave.shape[0]//2,:]
        y = d_top[:,i]
        base = y[-1]
    else: 
        d_bottom = stave[stave.shape[0]//2:,:]
        y = d_bottom[:,i]
        base = y[0]

    #make x data to match 1:1 number y data points + 0.5 to be in center of bins
    x = np.arange(y.shape[0])+0.5
    #flipped data
    y_f = np.flip(y)


    #x value where y is max
    x_max = x[np.argmax(y)]
    ## flipped data x val for max y
    x_max_f = x [np.argmax(y_f)]

    #set half max of gaussian
    h_max = (np.max(y)-base)/2

    ##all points y above baseline (y coordinates of gaussian)
    above = y>(base+h_max)
    above_f = y_f>(base+h_max)

    #np.argmin(above&(x>x_max))
    x_high = x[np.argmin((above&(x>x_max))|(x <= x_max))]
    #plt.axvline(x_high, color= 'green')

    x_low_f = x[np.argmin((above_f&(x>x_max_f))|(x <= x_max_f))]
    #plt.axvline(x_low_f, color = 'PINK')
    x_low = x[-np.argmin((above_f&(x>x_max_f))|(x <= x_max_f))-1]
    #plt.axvline(x_lowN, color = 'brown')

    return x, y, x_max, h_max, base, x_low, x_high


def gaus(x, a, mu, sig, k):
    return a*np.exp(-((x-mu)/sig)**2)+k
    
def fit_gaus(parameters):
    x, y, x_max, h_max, base, x_low, x_high = parameters
    try:
        fit = sp.optimize.curve_fit(gaus, x[(x>x_low)&(x<x_high)],y[(x>x_low)&(x<x_high)], p0 = (2*h_max, x_max, (x_high-x_low)/2, base),bounds = ((-10,0,0,-60),(10,x.max(),x.max(),50)))
    except RuntimeError:
        try:
            fit = sp.optimize.curve_fit(gaus, x[y>base],y[y>base], p0 = (2*h_max, x_max, (x_high-x_low)/2, base))
        except:
            print("Runtime error")
            return None
            
    val = fit[0]
    max_T = val[3] + val[0]

    if debug:
        x_gaus = x[(x>x_low)&(x<x_high)]
        y_gaus = y[(x>x_low)&(x<x_high)]
        plt.figure()
        plt.step(x_gaus, y_gaus, color = "blue")
        plt.plot(x_gaus, gaus (x_gaus, val[0], val[1], val[2], val[3]), color = "purple")
        plt.text(0.05, 0.90, "A: %.5f    Mu: %.5f    Max T: % C" %(val[0], val[1], max_T), transform=plt.gca().transAxes, fontsize=10)
        plt.text(0.05, 0.85, "Sigma: %.5f      K (constant off-set) : %.5f" %(val[2], val[3]), transform=plt.gca().transAxes, fontsize=10)
        plt.ylim(base + h_max -0.2,y_gaus.max()+0.3)
        plt.savefig("output/Fitted_gauss.png")
    return val



data = loop_cutter(d)
plt.figure()
plt.imshow(data, cmap = "plasma")
plt.colorbar()
plt.savefig("output/StaveLoopCut_img.png")

x_coord = np.arange(data.shape[1])
max_T = np.zeros(data.shape[1])
results = []

for i in range(data.shape[1]):
    print("in ", i , " run")
    parameters = gaus_finder(data, "top", i)
    val = fit_gaus(parameters)
    if val is None:
        s_max_T = np.nan
        results.append([np.nan]*4)
    else:
        results.append(val)
        max_T[i] = val[0] + val[3] 


results = np.array(results)

print(np.sum(np.isnan(max_T)))

np.save("max_T.npy", max_T)
plt.figure()
plt.plot(x_coord, max_T)
plt.savefig("output/thermal_profile.png")
plt.figure()
plt.plot(x_coord, results[:,0])
plt.savefig("output/amplitude_profile.png")
plt.figure()
plt.plot(x_coord, results[:,1])
plt.savefig("output/mu_profile.png")
plt.figure()
plt.plot(x_coord, results[:,2])
plt.savefig("output/sigma_profile.png")
plt.figure()
plt.plot(x_coord, results[:,3])
plt.savefig("output/k_profile.png")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 15:41:30 2020

@author: Lynnette Dray

Functions for the NAVIGATE aviation interpolation model

"""
import csv   # needed for data read-in
import numpy as np # needed to define n-dimensional arrays
import scipy.interpolate as interp   # for 2D interpolation routines

# Generic function to read data into a list array from a csv file

def Read_Data(csv_filename):
    
    with open(csv_filename,'r') as data:
        datain = csv.reader(data)
        output = []
        for row in datain:
            output.append(row)
    return output;

# adapted generic function to write data to a csv file, given a filename, array, headers and region designation
# 'regs' is an array of strings giving region designation
# 'data' has domeensions (year,region,variable)
def Write_Data(csv_filename,csv_headers,regs,data):
    csvfile=open(csv_filename,'w')
    csv.writer(csvfile).writerow(csv_headers)
    for y in range(0,len(data)):           # across different years
        for j in range(0,len(data[y])):           # across different regions
           thisrow = [str(data[y,j,0])]+[regs[j]]+list(map(str,data[y,j,1:]))
           csv.writer(csvfile).writerow(thisrow)
    csvfile.close()

# put the data in the format that we want. For now this 
# is just a big array (so that it can safely be passed 
# back/forward to external models). The dimensions of the
# array are [year][Country][variable][oil price grid point][carbon price grid point]
# The countries are the AIM country set by alphabetical 
# order of 2-letter ISO code. 

def Read_Grid(run_mode,csv_filename):
    
    griddatain = Read_Data(csv_filename)
    # expected values for dimensions of the input grid
    # these should be the same between all sets of model
    # runs and are not expected to change
    ylength = 2100 - 2005 + 1   # i.e. all years from 2005 to 2100
    clength = 140 # the number of countries in the AIM output
    nvar = 16    # the number of variables we are outputting
    if run_mode == 0:  # basic mode, i.e. fuel only
        nvar = 2     
    oplength = 9 # number of grid points in oil price
    cplength = 5 # number of grid points in carbon price
    
    gridout=np.empty([ylength,clength,nvar,oplength,cplength])   # year, country, variable, op, cp
#    cindex = 0   # country index - gives positioning of country in arrays
    
    opind = 0
    cpind = 0
    for i in range(1,(len(griddatain))):  # 0 is headers
        # work out which point in the oil and carbon price grid we are
        if (cpind == cplength):
            cpind = 0
            opind += 1
        if (opind == oplength):
            cpind = 0
            opind = 0

        # current data arrangement:     
        # i is the row of data, i.e. one data point per variable
        # j[0] is year, j[1] is country code which we'll need
        # to represent with the index j[2], 3 and 4 give the specific 
        # oil and carbon price variables used, then output variables
        # start at 5
        ygrid = int(griddatain[i][0]) - 2005   # data starts at 2015
        cgrid = int(griddatain[i][2])
            
        for j in range(0,nvar):
            gridout[ygrid][cgrid][j][opind][cpind] = griddatain[i][5+j]

        cpind += 1
    return gridout;

def Read_Price(csv_filename):
    
    pricedatain = Read_Data(csv_filename)
    # expected values for dimensions of the input grid
    # these should be the same between all sets of model
    # runs and are not expected to change
    ylength = 2100 - 2005 + 1   # i.e. all years from 2005 to 2100
    clength = 1 # the number of countries in the TIAM output
    nvar = 2     # the number of variables we are outputting
#    if run_mode == 0:  # basic mode, i.e. fuel only
#        nvar = 2     #(Kerosene and CO2 price - NB: CO2 price calculated from ratio of FF kerosene)
#    oplength = 9 # number of grid points in oil price
#    cplength = 5 # number of grid points in carbon price
    
    priceout=np.empty([ylength,nvar])   # year, variable
#    cindex = 0   # country index - gives positioning of country in arrays
    
#    opind = 0
#    cpind = 0
    for i in range(1,(len(pricedatain))):  # 0 is headers
#        # work out which point in thdde oil and carbon price grid we are
#        if (cpind == cplength):
#            cpind = 0
#            opind += 1
#        if (opind == oplength):
#            cpind = 0
#            opind = 0

        # current data arrangement:     
        # i is the row of data, i.e. one data point per variable
        # j[0] is year, j[1] is country code which we'll need
        # to represent with the index j[2], 3 and 4 give the specific 
        # oil and carbon price variables used, then output variables
        # start at 5
        ygrid = int(pricedatain[i][0]) - 2005   # data starts at 2005
#        cgrid = int(griddatain[i][1])
            
        for j in range(0,nvar):
#            gridout[ygrid][cgrid][j] = griddatain[i][2+j]
            priceout[ygrid][j] = pricedatain[i][1+j]
#        cpind += 1
    return priceout;

def Read_Country_Lookup(csv_filename):
    
    # reads in the lookup between country and NAVIGATE region
    
    datain = Read_Data(csv_filename)
 
    lookupout = []

    for i in range(1,(len(datain))):  # 0 is headers
        # datain[i][2] is the NAVIGATE 3-letter region code
        # datain[i][1] is the array position we want to put it in 
        # datain[i][3] is fuel scaling lookup (ignored here)
        # this means the output is a list of strings giving the 
        # NAVIGATE region per country, where the array index gives
        # the country
    
        lookupout.append(datain[i][2])

    return lookupout;

def Get_Op_GridPoints(year):
    
    # The input model runs have oil and carbon price that 
    # changes by year (the modelled range becomes greater 
    # over time). Get_Op_GridPoints and Get_Cp_GridPoints
    # account for this in the interpolation grid values.
    # Note that the main interpolation routine is called 
    # with kerosene price per kg in year 2005 USD - this
    # is dealt with by several steps of conversion factors. 
    
    op_modelbase = [68.74,77.61,82.67,109.77,68.45,86.39,99.98,97.06,99.67,93.26,48.66,42.77] # the year-2005 to year-2016 
                         # base year values. These
                         # are the same for all model runs
                         # they are in year 2015 dollars/bbl
                         # which is what is used internally in AIM
    
    # Baseline oil price grid. This always applies from 2020 onwards
    op_vals = [30,50,70,90,110,130,150,170,190] # grid values are consistent between all sets of model runs
    
    # 2015 - 2016 - single oil price value at model base
    if year < 2017:
        for i in range(0,len(op_vals)):
            op_vals[i] = op_modelbase[year-2005] + 0.0001*i # with small delta so that the ascending condition is met
    elif year < 2020:
        for i in range(0,len(op_vals)):
            op_vals[i] = op_vals[i] - (2020 - year) * (op_vals[i] - op_modelbase[len(op_modelbase)-1]) / (2020-2016)
    
    return op_vals;

def Get_Cp_GridPoints(year):
    
    # The input model runs have oil and carbon price that 
    # changes by year (the modelled range becomes greater 
    # over time). Get_Op_GridPoints and Get_Cp_GridPoints
    # account for this in the interpolation grid values

    # Baseline carbon price grid. These apply from 2050 onwards 
    # with a linear ramp up to this point from 2015
    cp_vals = [0,10,100,500,1000] # grid values are consistent between all sets of model runs
    
    if year < 2050:
        if year < 2016:
            for i in range(0,len(cp_vals)):
                cp_vals[i] = 0 + 0.0001*i # small delta so that the ascending condition is maintained 
        else:
            for i in range(0,len(cp_vals)):
                cp_vals[i] = cp_vals[i] - (2050 - year) * cp_vals[i] / (2050-2015)
    
    return cp_vals;

def KerosenePriceToModelInput(keroseneprice):
    
    # TIAM estimates kerosene price internally and uses this as a variable to 
    # pass to the aviation model. But the AIM grid runs use oil 
    # price as an input (and then make their own estimates of kerosene price
    # internally). So we need to estimate, for a given kerosene price, what
    # the oil price AIM would expect as input is which corresponds to that 
    # price. 
    # This is a function of various factors including lagged prices
    # due to hedging which we can't calculate exactly (because a given 
    # oil price input into AIM could be associated with multiple values
    # for previous-year fuel price). Given this, use a non-lagged model
    # to estimate what the oil price within AIM is. This is an estimated model
    # derived from a fit to AIM's internal fuel price routines. Because
    # hedging isn't included, the aviation system may be a little more 
    # sensitive to rapid changes in fuel price than it is in reality. 

    # first convert kerosene price to year 2015 dollars per kg
    keroseneprice = keroseneprice / 0.824 
       
    # now get an estimate of what the oil price AIM would have expected to 
    # produce this kerosene price is. This is generated by a model fit against
    # historical EIA data
    regGridPrice = 68.74 * ( ( keroseneprice / 0.783 ) - 0.1062 ) / 0.7930

    # this is what AIM expects as input, i.e. the oil price in year 2015/bbl which would 
    # correspond to a particular kerosene price in year 2005/kg
    
    return regGridPrice;

def Interpolate_Outcomes(year,reg_interp,kp_interp,cp5_interp,base_grid,country_lookup):
    
    # this routine actually does the interpolation

    # As the model grid runs are over oil price, get the
    # effective oil price that AIM would assume for a given 
    # kerosene price (excusive of carbon). This is year 2015 
    # dollars per barrel. It takes as input the expected TIAM
    # value for kerosene per kg in year 2005 USD.
    op_interp = KerosenePriceToModelInput(kp_interp)

    cp_interp = 1000.0 * cp5_interp / 0.824   
    # for carbon price we need price per tCO2 in year 2015 dollars
    # and are expecting costs in per kgCO2 in year 2005 dollars

    # Work out the right grid points to use.     
    # The model grid points are time-dependent (they cover
    # a smaller range of potential values for earlier time periods)

    op_vals = Get_Op_GridPoints(year)
    cp_vals = Get_Cp_GridPoints(year)  # grid values are consistent between model run sets

    vars_out = np.zeros([len(base_grid[0][0])]) # outputs the variables that we want - currently domestic and int'l fuel use, domestic and int'l RPK

    # loop over countries. If this country is in the region that we
    # want, interpolate and add its totals into the output array
    for c in range(0,len(country_lookup)):
    
        if country_lookup[c] == reg_interp:
            # if this is a country in the region we want, loop 
            # over variables adding them to the output
            for n in range(0,len(base_grid[0][0])):
                interp_array = base_grid[year-2005][c][n]
                # the interpolation routine itself. Note that this
                # is set to extrapolate for values outside the interpolation
                # domain. If points are used that are a long way outside the 
                # interpolation domain, then this may give nonsensical results
                # e.g. zero oil price, $10000/tCO2 carbon price or similar
                
                interp_fn = interp.RegularGridInterpolator((op_vals,cp_vals),interp_array,method='linear',bounds_error=False,fill_value=None)
                vars_out[n] += interp_fn([[op_interp,cp_interp]])[0]
          
    # check for negative values (possible if extremely high oil or carbon 
    # price s.t. flying is inaccessible apart from to the very rich) and set 
    # related variables to zero if found. Note not all variables behave
    # completely smoothly at the extrapolation point - e.g. there are complex
    # interactions around capacity for freight in passenger aircraft vs. 
    # capacity for freight in freighters.           
    
    check_negative_dom_pax = 0 # variables requiring setting dom pax to 0
    check_negative_int_pax = 0 # variables requiring setting int pax to 0
    check_negative_dom_freight = 0 # variables requiring setting dom freight to 0
    check_negative_int_freight = 0 # variables requiring setting int freight to 0
    check_negative_dom_all = 0 # variables requiring setting all dom variables to 0
    check_negative_int_all = 0 # variables requiring setting all int variables to 0
    
    for n in range(0,len(vars_out)):
        if vars_out[n] < 0:
            if (n == 0 or n == 12 or n == 14):  # variables such as dom fuel which imply no domestic flights if zero
                check_negative_dom_all = 1
            if (n == 1 or n == 13 or n == 15):  # variables such as int fuel which imply no int'l flights if zero
                check_negative_int_all = 1
            if (n == 2 or n == 8): # variables which imply no dom passenger flights if 0 
                check_negative_dom_pax = 0
            if (n == 3 or n == 9):  # variables which imply no int'l passenger flights if 0
                check_negative_int_pax = 0
            if (n == 6 or n == 10):  # variables which imply no dom freighter flights if 0    
                check_negative_dom_freight = 0
            if (n == 7 or n == 11):  # variables which imply no int'l freighter flights if 0 
               check_negative_int_freight = 0
            if (n == 4 or n == 5):  # dom and int'l hold freight RTK - just set to 0, does not affect other variables
               vars_out[n] = 0
        
    if check_negative_dom_all == 1: # implication is no domestic flights
        for n in (0,2,4,6,8,10,12,14):
            if n < len(vars_out):
               vars_out[n] = 0.0
     
    if check_negative_int_all == 1: # implication is no int'l flights
        for n in (1,3,5,7,9,11,13,15):
            if n < len(vars_out):
                vars_out[n] = 0.0
            
    if check_negative_dom_pax == 1:  # implication is no domestic pax flights (or hold RTK)   
        for n in (2,4,8):
            if n < len(vars_out):            
                vars_out[n] = 0.0

    if check_negative_int_pax == 1:  # implication is no int pax flights (or hold RTK)   
        for n in (3,5,9):
            if n < len(vars_out):
                vars_out[n] = 0.0            
    
    if check_negative_dom_freight == 1:  # implication is no domestic freighter flights   
        for n in (6, 10):
            if n < len(vars_out):
                vars_out[n] = 0.0
            
    if check_negative_int_freight == 1:  # implication is no int'l freighter flights   
        for n in (7, 11):
            if n < len(vars_out):
                vars_out[n] = 0.0
                     
    return vars_out;


def Generate_Test_Keroseneprice(year, rate):
    
    # generates a kerosene price trend for model testing, based
    # on a yearly growth rate after 2017

    # values to return for the 2005-2016 period, year 2015 dollars, US EIA data
    # these are per US gallon - convert to per kg
    kp0516 = [2.11,2.35,2.47,3.36,1.88,2.39,3.22,3.20,3.03,2.77,1.63,1.30,1.56]
   
    # per kg at typical density
    jeta1kgpergallon = 3.044
    
    # conversion to year 2005 dollars
    inflateFactor = 0.824
    
    if (year < 2017):
        kp_out = inflateFactor * kp0516[max(year-2005,0)]/jeta1kgpergallon
    else:
        kp_out = inflateFactor * kp0516[len(kp0516)-1] * ( rate ** ( year - 2017 ) ) / jeta1kgpergallon
    
    # this gets us year 2005 dollars per kg kerosene, which is what the 
    # model expects as input
  
    return kp_out;
 
def Generate_Test_Carbonprice(year, baseval, rate):
    
    # generates a carbon price trend for model testing, based
    # on a yearly growth rate after 2019 and assuming 0 before
    # then (i.e. ignoring the EU ETS). Note that this is the 
    # effective carbon price applied across all carbon on a 
    # given route group, i.e. no baseline is assumed. 
 
    
    if (year < 2020):
        cp_out = 0
    else:
        cp_out = baseval * ( rate ** ( year - 2020 ) )
    
    # for output, assume price per kgCO2
    # note this is year 2005 dollars
    # (input price is per tCO2)
    
    cp_out = cp_out / 1000.0;     
    
    return cp_out;

def CpricePerKGJetA(carbonprice):
    
    # given a carbon price per kgCO2, convert to per kg jet A1
    # assumes 3.15 kg CO2 per kg fuel burnt
    # this is just for test output
    
    cpriceperkg = 3.15 * carbonprice 
    
    return cpriceperkg;

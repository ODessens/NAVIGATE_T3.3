#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This program is a simple interpolation-based model which takes 
estimates of socieoconomic scenario and aviation fuel 
characteristics, carbon costs and technology characteristics 
by country for the period to 2100 and uses these to interpolate across 
a grid of outputs of the Aviation Integrated Model (AIM, www.atslab.org)
to generate simple rapid estimations of aviation fuel use. 

The main assumption inherent in the model is that large-scale reductions
in aviation emissions will largely be achieved by drop-in fuel use (either
biofuels or PTL); i.e. that the impact of fully electric aircraft on global
aviation emissions will be small due to battery energy density requirements, 
and that hydrogen will affect aviation emissions via inclusion in the PTL 
production process rather than as fuel for a redesigned aircraft. These 
assumptions are specifically made due to the long lifespan of aircraft models,
i.e. fuel changes that require fully redesigned aircraft are likely to 
be significantly slower than those that can apply to existing aircraft. 

The assumptions used for operational measures and retrofits are derived 
from Dray et al. (2018) and Schafer et al. (2015). The assumptions about 
new models of conventional aircraft to 2050 are derived from ATA and 
Ellondee (2018); these assume specific sets of technologies are applied in 
these new aircraft models (e.g. composites, higher aspect ratio wing, ultra
high bypass ratio engines). After 2050, consistent assumptions similar to those used in 
Dray et al. (2018) are applied for average improvement in fuel burn per year
for new aircraft models.

Before 2017, this returns a single value across assumptions for kerosene 
and carbon price, based on modelling using actual historical trends 
for these variables (AIM typically has a 2015 base year but the 2005-2014
values are filled in from a 2005 base year run). From 2017 onwards, it can be
called with a given kerosene and carbon price. 

It can be used to model biofuels as follows:
    1. uptake of biofuel is assumed either via a biofuel mandate or from biofuel
    being less expensive that fossil jet A once carbon price is factored in. This
    calculation is assumed done outside the metamodel in each NAVIGATE T3.3 IAM.
    2. given the calculated uptake/blend, the model input carbon price and kerosene
    price are adjusted. For example, if the blend is 20% biofuel and biofuel
    is exempt from carbon pricing, the carbon price to the model is reduced by
    20%. Similarly the input kerosene price is adjusted to take account of the
    biofuel uptake. 
    3. The model outputs aviation fuel use - it's assumed this will have appropriate 
    fuel lifecycle emissions factors applied to it appropriate for the fuel 
    blend used to calculate final co2.
    
    This version writes a csv file of outputs by world region, to support an 
    initial softlink of the aviation model with wider energy and emissions models. 

 """

######################################################################
# Importing required libraries for reading and working with the data #
######################################################################

import time    # so we can time each run and optimise accordingly
import numpy as np # needed to define n-dimensional arrays
import Functions_Aviation_NAVIGATE as func

# note the model functions additionally requires the scipy and csv libraries

###############################################################################
###############################################################################

# Input parameters which are the same throughout one whole
# run. These are used to select which data is read in.
soc_scen = "SSP2"
tech_scen = "t2"
# two potential run modes at present:
# basic (run_mode=0) - only reads in and outputs aviation fuel use
# full (run_mode=1) - reads in and outputs a range of metrics, including flights, RPK, RTK, NOx, distance flown etc.
# The read-in and run times increase with the number of variables, so basic
# mode is faster to use. Full mode allows a larger range of policy interactions
# and non-CO2 impacts to be calculated. 

run_mode = 0

# the processed grid AIM outputs are stored here in csv format
data_folder = "aviation_grid_data/"

print("Loading grid data...")

# Data to interpolate between - this is slow so ideally do only once
# base grid is the main grid of interpolation data by country
# country_lookup gives the relationship between country and NAVIGATE IAMs'region
start_time=time.time()

base_grid = func.Read_Grid(run_mode,data_folder + "grid_output_by_country_" + soc_scen + "_" + tech_scen + ".csv")
country_lookup = func.Read_Country_Lookup(data_folder + "country_region_lookup.csv")
price_IAM = func.Read_Price(data_folder + "Prices_KerCO2.csv")

end_time=time.time()
load_time=end_time-start_time
print("Read-in time:")
print(load_time)

# A routine loops over the TIAM-UCL 16 regions and all years 2020-2100, working out total fuel use. 

start_time=time.time()

# the TIAM regions to loop over
regs = ["AFR","AUS","CAN","CSA","CHI","EEU","FSU","IND","JPN","MEX","MEA","ODA","SKO","UK","USA","WEU"]

# year range to cover. 
ystart = 2005
yend = 2100

# output filename
filename_out = "output_byregion_"+soc_scen+"_"+tech_scen+".csv"

# global totals across all variables and regions to write out
data_out = np.zeros([yend-ystart+1,len(regs),len(base_grid[0][0])+4]) 


for year in range(ystart,yend+1):
    for r in range(0,len(regs)):
        kp_interp = price_IAM[year-ystart,r,0]   # kerosene price in year-2005-USD/kg 
        cp_interp = price_IAM[year-ystart,r,1]  # carbon price in year-2005-USD/kgCO2 in 2020 and increasing at 3%/year
    # note both kp_interp and cp_interp are in units year 2005 USD/kg for consistency with likely input values from TIAM for r in range(0,len(regs)):
    
        # store year, kerosene and carbon prices in variable output
        data_out[year-ystart,r,0] = year
        data_out[year-ystart,r,1] = kp_interp
        data_out[year-ystart,r,2] = cp_interp

        # for variable output, also store what the effective kerosene price is including 
        # carbon costs (not used as input to the interpolation model itself as this takes
        # carbon and fuel price separately)     
        data_out[year-ystart,r,3] = data_out[year-ystart,r,1] + func.CpricePerKGJetA(cp_interp)
        reg_interp = regs[r]

        # call the interpolation routine for this year, region, fuel and carbon price
        # if run_mode == 0 then this only returns fuel, if run_mode == 1 then it returns other metrics too
        vars_out = func.Interpolate_Outcomes(year,reg_interp,kp_interp,cp_interp,base_grid,country_lookup)

        for n in range(0,len(vars_out)):
            data_out[year-ystart,r,n+4] += vars_out[n]
     
end_time=time.time()

# write out test run outputs to a csv file for comparison with 
# full model runs using those outputs

if run_mode == 0:  # basic mode, i.e. fuel only
    func.Write_Data(filename_out,['Year','Region','KerosenePrice_Assumed_Year2005USDPerkg','CarbonPrice_Assumed_Year2005USDPerkg','EffectiveKerosenePrice_WithCarbon_Year2005USDPerkg','Domestic_Fuel_Mt','International_Fuel_Mt'],regs,data_out)
else:                    
    func.Write_Data(filename_out,['Year','Region','KerosenePrice_Assumed_Year2005USDPerkg','CarbonPrice_Assumed_Year2005USDPerkg','EffectiveKerosenePrice_WithCarbon_Year2005USDPerkg','Domestic_Fuel_Mt','International_Fuel_Mt','Domestic_RPK','International_RPK','Domestic_Hold_Freight_RTK','International_Hold_Freight_RTK','Domestic_Freighter_RTK','International_Freighter_RTK','Domestic_Passenger_Flights','International_Passenger_Flights','Domestic_Freighter_Flights','International_Freighter_Flights','Domestic_NOx_kt','International_NOx_kt','Domestic_AKM','International_AKM'],regs,data_out)
    
interp_time=end_time-start_time

print("Time for test interpolatation to 2100:")

print(interp_time)
###############################################################################


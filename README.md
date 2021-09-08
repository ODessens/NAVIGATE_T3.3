Aviation NAVIGATE metamodel.
The model is supplied as Python code files and a set of associated data tables.
1) Model_Aviation_NAVIGATE.py: routine which runs the aviation model in standalone mode, for a given set of parameters (socioeconomic scenario, technology scenario, oil price, carbon price). It calculates global-level aviation metrics between 2005 and 2100 for the given oil and carbon price, and writes these metrics to a results file.
2) Functions_Aviation_NAVIGATE.py: contains the functions necessary to run the model. There are two separate components: initial data read-in and the metamodel itself.
3) aviation_grid_data: contains all the data needed to run the model (the outputs from the AIM runs, the fuel and carbon prices ...)
4) TIAM-UCL_data: (example of interface files betwen TIAM-UCL and the aviation module) files with prices for fuel (blend) and carbon (different runs: temperature target/SSP) to be use by the aviation module and files with results from the aviation module (fuel use to be passed in TIAM-UCL enegy system: SSP/tech. dev.). 

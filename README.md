Aviation NAVIGATE metamodel.
The model is supplied as Python code files and a set of associated data tables.
1) Model_Aviation_NAVIGATE.py: routine which runs the aviation model in standalone mode, for a given set of parameters (socioeconomic scenario, technology scenario, oil price, carbon price). It calculates global-level aviation metrics between 2005 and 2100 for the given oil and carbon price, and writes these metrics to a results file.
2) Functions_Aviation_NAVIGATE.py: contains the functions necessary to run the model. There are two separate components: initial data read-in and the metamodel itself.
3) aviation_grid_data: contains all the data needed to run the model (the outputs from the AIM runs, the fuel and carbon prices ...)

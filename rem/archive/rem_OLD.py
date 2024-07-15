""" Script for Validation Study MDR requirement to show 
deviation from e-STAT 2.0 targets.

Written by: Travis M. Moore
Created: July 28, 2023
Last edited: July 10, 2024
"""

###########
# Imports #
###########
# Import custom modules
from models import verifitmodel
from models import estatmodel
from models import datamodel

"""
NOTE: To write print statements to file rather than console,
run using: 'python rem.py > output.txt'. This will
provide a .txt file with the results of the analyses.
"""

#############
# Constants #
#############
_PATH = r'\\starfile\Public\Temp\CAR Group\Afton Validation\REM and Targets'
FREQS = [250, 500, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
LOW = [250, 500, 1000, 2000]
HIGH = [3000, 4000, 6000]

# Create dictionary of arguments 
PARS = {
    'low_freqs': LOW,
    'low_ceiling': 5,
    'high_freqs': HIGH,
    'high_ceiling': 8
}

#################################
# Import VERIFIT and ESTAT Data #
#################################
# VERIFIT
v = verifitmodel.VerifitModel(_PATH, freqs=FREQS)
v.get_data()

# eSTAT
e = estatmodel.EstatModel(_PATH, freqs=FREQS)
e.get_targets()

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

#####################################
# Analyze Separate Form Factor Data #
#####################################
# Organize data
d = datamodel.DataModel(
        verifit_data=v.measured.copy(), 
        estat_data=e.estat_targets.copy()
    )

# Analyze data (number of ears meeting criteria)
d.analyze(d.vdf, d.edf, **PARS)

#############
# Plot Data #
#############
# Make deviation from target plots (BestFit and TargetMatch - eSTAT)
d.abs_diff_plots(freqs=LOW, criterion=PARS['low_ceiling'], 
                     show='n', save='y')

d.abs_diff_plots(freqs=HIGH, criterion=PARS['high_ceiling'], 
                     show='n', save='y')

# Make fine tuning plots (TargetMatch - EndStudy)
d.endstudy_targetmatch_fine_tuning_plots(
    endstudy_data=d.vdf,
    show='n', 
    save='y'
)

# Make fine tuning plots (BestFit - TargetMatch)
d.bestfit_targetmatch_fine_tuning_plots(
    verifit_data=d.vdf,
    show='n',
    save='y'
)

######################
# Write Data to File #
######################
# Write data to .csv
d.write_estat_diffs(d.estat_diffs, 'split_estat_diffs')
d.write_endstudy_diffs(d.endstudy_diffs, 'split_endstudy_diffs')

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

######################################
# Analyze Collapsed Form Factor Data #
######################################
#Organize data
d = datamodel.DataModel(
        verifit_data=v.measured.copy(), 
        estat_data=e.estat_targets.copy()
    )

# Collapse RIC and Wireless Customs for Verifit and estat dfs
d.collapse_form_factors()

# Analyze data (number of ears meeting criteria)
d.analyze(
    verifit_data=d.verifit_collapsed,
    estat_data=d.estat_collapsed, 
    **PARS
)

#############
# Plot Data #
#############
# Make deviation from target plots (BestFit and TargetMatch - eSTAT)
d.abs_diff_plots(freqs=LOW, criterion=PARS['low_ceiling'], 
                     show='n', save='y')

d.abs_diff_plots(freqs=HIGH, criterion=PARS['high_ceiling'], 
                     show='n', save='y')

# Make fine tuning plots (EndStudy - TargetMatch)
d.endstudy_targetmatch_fine_tuning_plots(
   endstudy_data=d.verifit_collapsed,
   show='n', 
   save='y'
)

# # Make fine tuning COLLAPSED plots (BestFit - TargetMatch)
# d.bestfit_targetmatch_fine_tuning_plots(
#     verifit_data=COLLAPSED_DATA_GO_HERE,
#     show='n',
#     save='y'
# )

######################
# Write Data to File #
######################
# Write data to .csv
d.write_estat_diffs(d.estat_diffs, 'collapsed_estat_diffs')
d.write_endstudy_diffs(d.endstudy_diffs, 'collapsed_endstudy_diffs')

################
# Module Guard #
################
if __name__ == '__main__':
    pass

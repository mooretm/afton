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
#_PATH = r'\\starfile\Public\Temp\CAR Group\Afton Validation\REM and Targets'
_PATH = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\REM and targets'
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

#bf, tm = d._diff_between_bestfit_targetmatch(d.vdf)


d.bestfit_targetmatch_fine_tuning_plots(
    verifit_data=d.vdf,
    show='y',
    save='y'
)



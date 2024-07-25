""" Script for Validation Study MDR requirement to show 
deviation from e-STAT 2.0 targets.

Written by: Travis M. Moore

Created: July 28, 2023

Last edited: July 24, 2024
"""

"""
NOTE: To write print statements to file rather than console,
run using: 'python rem.py > output.txt'. This will
provide a .txt file with the results of the analyses.
"""

###########
# Imports #
###########
# Standard library
import logging
from logging.handlers import RotatingFileHandler

# Custom modules
from models import verifitmodel
from models import estatmodel
from models import datamodel

##########
# Logger #
##########
def mb_to_bytes(mb):
    """ Convert megabytes to bytes. """
    return mb * 1024 * 1024

# Create a custom formatter
formatter = logging.Formatter(
    '[%(levelname)s|%(module)s|L%(lineno)d] %(message)s'
)

# Create new logger with module name
logger = logging.getLogger(__name__)
# Set new logger level
logger.setLevel(logging.DEBUG)

# Create stream handler for console output
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Create rotating file handler to write logs to file
file_handler = RotatingFileHandler(
    'rem_collapsed.log', 
    maxBytes=mb_to_bytes(2), 
    backupCount=2
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#############
# Constants #
#############
_PATH = r'\\starfile\Public\Temp\CAR Group\Afton Validation\REM and Targets'
FREQS = [250, 500, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
LOW = [500, 1000, 2000]
HIGH = [3000, 4000]

# Create dictionary of arguments 
PARS = {
    'low_freqs': LOW,
    'low_ceiling': 5,
    'high_freqs': HIGH,
    'high_ceiling': 8
}

COLLAPSE = {
    'MRIC': 'RIC',
    'RIC_RT': 'RIC',
    'RIC312': 'RIC',
    'ITE': 'ReCustom',
    'ITC': 'ReCustom',
    'CIC': 'CIC'
}

#################################
# Import VERIFIT and ESTAT Data #
#################################
# VERIFIT
logger.info("Grabbing Verifit data")
v = verifitmodel.VerifitModel(_PATH, freqs=FREQS)
v.get_data()

# eSTAT
logger.info("Grabbing e-STAT 2.0 data")
e = estatmodel.EstatModel(_PATH, freqs=FREQS)
e.get_targets()

#####################################
# Analyze Separate Form Factor Data #
#####################################
# Organize data
d = datamodel.DataModel(
        verifit_data=v.measured.copy(), 
        estat_data=e.estat_targets.copy()
)

# Collapse form factors
vdf, edf = d.collapse_form_factors(d.vdf, d.edf, COLLAPSE)

# Analyze data (number of ears meeting criteria)
d.analyze(vdf, edf, **PARS)

#############
# Plot Data #
#############
# Make deviation from target plots (BestFit and TargetMatch - eSTAT)
d.abs_diff_plots(
    freqs=LOW, 
    criterion=PARS['low_ceiling'], 
    show='n', 
    save='y'
)

# Make deviation from target plots (BestFit and TargetMatch - eSTAT)
d.abs_diff_plots(
    freqs=HIGH, 
    criterion=PARS['high_ceiling'], 
    show='n', 
    save='y'
)

# Make fine tuning plots (TargetMatch - EndStudy)
d.endstudy_targetmatch_fine_tuning_plots(
    endstudy_data=vdf,
    show='n', 
    save='y'
)

# Make fine tuning plots (BestFit - TargetMatch)
d.bestfit_targetmatch_fine_tuning_plots(
    verifit_data=vdf,
    show='n',
    save='y'
)

######################
# Write Data to File #
######################
# Write data to .csv
d.write_estat_diffs(d.estat_diffs, 'estat_diffs_collapsed')
d.write_endstudy_diffs(d.endstudy_diffs, 'endstudy_diffs_collapsed') 

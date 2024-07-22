""" Script to organize and clean DAM data for Afton. """

###########
# Imports #
###########
# Third party
import pandas as pd

# Custom modules
from models import dam

##########
# Script #
##########
# Define path
path=r'\\starfile\Public\Temp\CAR Group\Afton Validation\DAM\results'

# Import data from path
raw_data = dam.import_data(path)

# Only proceed if a DataFrame was returned
# (otherwise there was an error).
if isinstance(raw_data, pd.DataFrame):
    # Organize data 
    prepped_data = dam.organize_data(raw_data)
    # Remove incomplete datasets
    clean_data = dam.remove_incomplete_datasets(prepped_data)
    # Write DataFrame to CSV
    clean_data.to_csv('dam_clean.csv')
    
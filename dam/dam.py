""" Code to import and organize DAM results from Afton Validation. 
Returns two CSV files: raw df and df with complete datasets. 

Written by: Sarah Iverson and Travis M. Moore
Last Edited: July 2, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import os
import re
from pathlib import Path

# Third party
import pandas as pd
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

##########
# Logger #
##########
# Create a custom formatter
formatter = logging.Formatter(
    '[%(levelname)s|%(module)s|L%(lineno)d] %(message)s'
)
# Create new logger with module name
logger = logging.getLogger(__name__)
# Set new logger level
logger.setLevel(logging.DEBUG)
# Create a handler
handler = logging.StreamHandler()
# Add formatter to handler
handler.setFormatter(formatter)
# Add handler to logger
logger.addHandler(handler)

#############
# Constants #
#############
NOISE_TRACKS = ['119', '205', '193', '181', '170', '182', '160', '71']
COMPARISONS = {
    'DAM_3-DAM_OFF': 'DAM_OFF-DAM_3',
    'DAM_4-DAM_3': 'DAM_3-DAM_4',
    'DAM_3-MNR_3': 'MNR_3-DAM_3',
    'DAM_OFF-DAM_3': 'DAM_OFF-DAM_3',
    'DAM_3-DAM_4': 'DAM_3-DAM_4',
    'MNR_3-DAM_3': 'MNR_3-DAM_3',
}

#############
# Functions #
#############
def _validate_file_name(file_name):
    """ Make sure each data file has a valid name.

    :param filename: A CSV file name from Vesta for DAM
    :type filename: Path
    :return: True or False based on whether or not the filename matches the pattern
    :rtype: bool
    """
    # Get just the file name (minus path)
    file_name = os.path.basename(file_name)
    logger.info("Importing: %s", file_name)

    # File name pattern
    pattern = r"^\d{4}_\w+_\d{4}_(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)_\d{2}_\d{2}\d{2}\.csv$"
    
    # Check file_name against pattern
    if not re.match(pattern, file_name):
        return False
    return True

def import_data(path):
    """ Import DAM data and create a single DataFrame.

    :param path: Path to data folder 
    :type path: str
    :return: Organized DAM data
    :rtype: pd.DataFrame
    """
    logger.info("Attempting to create concatenated data set")
    # Get list of file names/paths
    logger.info("Getting list of file paths")
    files = Path(path).glob('*.csv')
    files=list(files)

    # Import data
    logger.info("Attempting to read files")
    df_list = []
    invalid_format = []
    for file in files:
        # Validate file names
        if not _validate_file_name(file):
            invalid_format.append(file)
        # Read in CSV as DataFrame
        temp = pd.read_csv(file)
        # Append to list
        df_list.append(temp)

    # Concatenate list of dfs into single df
    data = pd.concat(df_list)
    # Display and invalid file names found during import
    if invalid_format: 
        logger.error("Found the following invalid file names:")
        for f in invalid_format:
            logger.error(os.path.basename(f))
        logger.error("Stopping script until file names are fixed")
        return None
    else:
        # Only return data if all the file names were accurate
        # Otherwise, there will be problems later on
        return data

def organize_data(data):
    """ Combine button_A and button_B columns into a single column.
    Make one column for SNR from audio file name.

    :param data: Imported Vesta for DAM data
    :type data: DataFrame
    :return: 
    :rtype: DataFrame
    """
    logger.info("Creating additional columns")
    # Insert comparison column 
    # Populate it with the data from button a and button b columns
    logger.info("Adding 'comparison' colum")
    data.insert(
        loc=6, 
        column='comparison', 
        value=data["button_A"]+"-"+data["button_B"]
    )

    # Insert snr and track columns 
    # Populate it with the fifth value from audio_file
    audio_files = data["audio_file"]
    split_values = audio_files.str.split('_')
    # SNR column
    logger.info("Adding 'snr' column")
    snrs = split_values.apply(lambda z: z[4])
    data['snr'] = snrs
    # Tracks column
    logger.info("Adding 'tracks' column")
    tracks = split_values.apply(lambda z: z[0])
    data['tracks'] = tracks
    # Convert tracks to labels
    logger.info("Converting track numbers to condition labels")
    data['type'] = data['tracks'].apply(lambda value: 'noise' if value in NOISE_TRACKS else 'pref')

    # Flip mirrored conditions to the same direction
    logger.info("Adjusting mirrored conditions")
    data['comparison'] = data['comparison'].apply(lambda x: COMPARISONS[x])
    logger.info("Successfully prepared data")
    return data

def remove_incomplete_datasets(data):
    """ Write something here. """
    # Make data frames
    mli = data.copy()
    mask = mli['type'] == 'pref'
    prefs = mli[mask].copy()
    noise = mli[-mask].copy()
    df_list = [prefs, noise]

    for df in df_list:
        subject_ids = df["subject"].unique()
        conditions = df["condition"].unique()
        snrs = df["snr"].unique()
        comparisons = df["comparison"].unique()
        indices_to_remove = []
        df.set_index(['subject', 'comparison', 'snr', 'condition'], inplace=True)
        df.sort_index(level=['subject', 'comparison', 'snr', 'condition'], inplace=True)
        for subject in subject_ids:
            for comparison in comparisons:
                for snr in snrs:
                    for condition in conditions: 
                        try:
                            #temp = df.loc[(subject, comparison, snr, condition)]['outcome']
                            temp = df.loc[(subject, comparison, snr, condition)]
                            if temp.shape[0] != 4:
                                print(temp.shape)
                                print(temp)
                                #indices_to_remove.append((subject, comparison, snr, condition))
                                df.drop((subject, comparison, snr, condition), axis=0, inplace=True)
                        except KeyError:
                            continue
    return pd.concat(df_list)

################
# Module Guard #
################
if __name__ == '__main__':

    # The code below runs when dam.py is called as a module
    path=r'\\starfile\Public\Temp\CAR Group\Afton Validation\DAM\results'

    # Import data
    raw_data = import_data(path)

    if isinstance(raw_data, pd.DataFrame):
        # Organize data 
        prepped_data = organize_data(raw_data)

        # Remove incomplete datasets
        clean_data = remove_incomplete_datasets(prepped_data)
        clean_data.to_csv('dam_clean.csv')

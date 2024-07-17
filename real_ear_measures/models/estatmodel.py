""" Estat targets data class

    Create a dataframe of desired values from tech toolbox
    .csv file. 

    Written by: Travis M. Moore
    Created: Nov. 28, 2022
    Last edited: August 08, 2023
"""

###########
# Imports #
###########
# Import GUI packages
import tkinter as tk
from tkinter import filedialog

# Import system packages
import os
from pathlib import Path

# Import data science packages
import numpy as np
import pandas as pd


#########
# BEGIN #
#########
class EstatModel:
    def __init__(self, path=None, freqs=None, **kwargs):
        # Check for provided path
        if not path:
            # Show file dialog to get path
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askdirectory()
            print(path)

        # Get list of files
        files = Path(path).glob('*.csv')
        self.files = list(files)

        self._check_file_names()

        # Check for frequencies        
        if freqs:
            self.freqs = freqs
        else:
            raise AttributeError
        
        self.row_to_chop = None


    def _check_file_names(self):
        '''
        Check target files for naming errors
        Prints list of bad names and quits if bad names are found
        '''
        my_list = []
        print(f"\nestatmodel: Inspecting file names")
        for file in self.files:
            name = str(file).split("\\")[-1]
            if len(name.split("_")) != 2:
                my_list.append(name)
                print(f"estatmodel: Found bad name: {name}")

        if len(my_list) > 0:
            quit()


    def _get_form_factor(self, df):
        """ Tech toolbox data export files are organized differently 
            based on form factor. This function assigns the header 
            row (-1) and starting target column by form factor. 
        """
        device_info = str(df.iloc[0,0])
        if "MicroRIC" in device_info:
            self.form_factor = "MRIC"
            self.row_to_chop = 20
        elif " RIC RT" in device_info:
            self.form_factor = "RIC_RT"
            self.row_to_chop = 20
        elif " RIC 312" in device_info:
            self.form_factor = "RIC312"
            self.row_to_chop = 20
        elif "ITE" in device_info:
            self.form_factor = "ITE"
            self.row_to_chop = 20
        elif "ITC" in device_info:
            self.form_factor = "ITC"
            self.row_to_chop = 20
        elif "CIC" in device_info:
            self.form_factor = "CIC"
            self.row_to_chop = 19
        elif "IIC" in device_info:
            self.form_factor = "IIC"
            self.row_to_chop = None
        else:
            self.form_factor = "OTHER"


    def get_targets(self):
        """ Create e-STAT prescribed targets dataframe
        """
        # Display to console
        msg = "Pulling eSTAT Data"
        print('')
        print('-' * len(msg))
        print(msg)
        print('-' * len(msg))

        df_list = []
        for file in self.files:
            print(f"estatmodel: Processing {file}")
            # Get filename
            filename = os.path.basename(file)[:-4]
        
            # Read in .csv file as dataframe          
            df = pd.read_csv(file, header=None)

            # Get header row, starting target column, 
            # and form factor
            self._get_form_factor(df)

            # Truncate df to rows 20 and below to cut off header information
            data = df.iloc[self.row_to_chop:,0:3].copy()

            # Rename columns
            data.columns = ['freq', 'left', 'right']

            # Change data type to numeric for entire df
            data = data.apply(pd.to_numeric, errors='ignore')

            # Round estat target values
            data[['left', 'right']] = data[['left', 'right']].apply(np.round, decimals=1)

            # Set frequency column as index
            data = data.set_index(['freq'])

            # Subset by desired frequencies
            data = data.loc[self.freqs]

            # Convert freq index to column
            data.reset_index(inplace=True)

            # Insert subject number from file name
            data.insert(loc=0, column='filename', value=filename)

            # Add form factor column
            data.insert(loc=1, column='form_factor', value=self.form_factor)

            # Append df to list
            df_list.append(data)

        self.estat_targets = pd.concat(df_list)
        self.estat_targets.insert(loc=1, column='data', value='estat')
        self.estat_targets.reset_index(drop=True, inplace=True)
        print("estatmodel: Done")
        print(f"estatmodel: Records processed: {len(df_list)}")
        print('-' * len(msg))

        #self.estat_targets.to_csv('estat_model.csv')


    def long_format(self):
        self.estat_targets_long = pd.melt(self.estat_targets, 
            id_vars=['filename', 'data', 'form_factor', 'freq'], 
            value_vars=list(self.estat_targets.columns[4:]))

        self.estat_targets_long.rename(columns={
            'variable': 'side',
            'value': 'estat_target'
            }, 
            inplace=True
        )

        #self.to_csv('estat_model_long.csv')

################
# Module Guard #
################
if __name__ == '__main__':
    pass

""" Functions to organize and analyze speech in noise data.

These functions rely on a single CSV file containing only 
word and sentence score data for a given group (e.g., RIC, CIC). 

Written by: Travis M. Moore and Sarah Iverson

Last edited: July 18, 2024
"""

###########
# Imports #
###########
# Standard library
import itertools
import logging
import os

# Third party
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import seaborn as sns
import tkinter as tk
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
from tkinter import filedialog

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
logger.setLevel(logging.INFO) # DEBUG
# Create a handler
handler = logging.StreamHandler()
# Add formatter to handler
handler.setFormatter(formatter)
# Add handler to logger
logger.addHandler(handler)

#############
# Functions #
#############
def browse_for_data():
	""" Import raw CSV data using a tkinter file browser for file selection.
	
	:return: A DataFrame of the raw CSV data (no organization or 
		cleaning occurs here).
	:rtype: pd.DataFrame
	"""
	# Set up GUI root to use filedialog
	root = tk.Tk()
	# Hide root window
	root.withdraw()
	# Get path to data
	filename = filedialog.askopenfilename(
	    title="Choose SIN Data File",
	    filetypes=[('comma separated', '*.csv')]
	)
	# Read in data
	data = pd.read_csv(filename)
	return data

def organize_data(data):
	""" Create separate word and sentence DataFrames. 
	
	:param data: Raw SIN data from imported CSV.
	:type data: pd.DataFrame
	:return: Two DataFrames - 1 for words, 1 for sentences.
	:rtype: pd.DataFrame
	"""
	# Get original column names
	cols = data.columns
	# Filter col names by words and sentences
	word_col_names = [value for value in cols if 'Words' in value]
	sentence_col_names = [value for value in cols if 'Sentences' in value]
	# Create separate word and sentence DataFrames
	word_data = data[word_col_names].copy()
	sentence_data = data[sentence_col_names].copy()
	# Reformat column names for plots
	# Word column names
	new_word_col_names = []
	for col in word_col_names:
		# Split by underscore and remove last value
		temp = col.split('_')[:-1]
		# Concatenate items separated by a space
		temp = ' '.join(temp)
		# Add reformatted column name to list
		new_word_col_names.append(temp)
	# Sentence column names
	new_sentence_col_names = []
	for col in sentence_col_names:
		temp = col.split('_')[:-1]
		temp = ' '.join(temp)
		new_sentence_col_names.append(temp)
	# Rename DataFrame columns
	word_data.columns = new_word_col_names
	sentence_data.columns = new_sentence_col_names
	return word_data, sentence_data

def friedman_test(data, condition):
	""" Conduct Friedman Test and log results to console.
	
	:param data: A DataFrame of imported and organized CSV SIN data.
	:type data: pd.DataFrame
	:param condition: The name of the condition to display in the results.
	:type condition: str
	:return: Prints test results to console.
	:rtype: None
	"""
	# Pass DataFrame columns as lists (requires unpack operator: *)
	statistic, pvalue = stats.friedmanchisquare(*data.values.tolist())
	statistic = np.round(statistic, 3)
	pvalue = np.round(pvalue, 3)
	logger.info("")
	logger.info("Friedman Test for %s", condition)
	logger.info("statistic: %s", np.round(statistic, 3))
	logger.info("p-value: %s", np.round(pvalue, 3))

def wilcoxon_test(data, condition):
	""" Conduct Wilcoxon Test and log results to console. 
	
	:param data: A DataFrame of imported and organized CSV SIN data.
	:type data: pd.DataFrame
	:param condition: The name of the condition to display in the results.
	:type condition: str
	:return: Prints test results to console.
	:rtype: None
	"""
	for combo in itertools.combinations(data.columns, 2):
		i = combo[0]
		j = combo[1]
		statistic, pvalue = stats.wilcoxon(data.loc[:, i], data.loc[:, j])
		statistic = np.round(statistic, 3)
		pvalue = np.round(pvalue, 3)
		logger.info("")
		logger.info("Wilcoxon Test for %s", condition)
		logger.info("Conditions: %s vs. %s", i, j)
		logger.info("statistic: %s", np.round(statistic, 3))
		logger.info("p-value: %s", np.round(pvalue, 3))

def make_plots(data, title=None, save_name=None, show=True, save=False):
	""" Create box plots for SIN data. 
	
	Accepts custom plot title and saved PNG name. Optionally 
	displays and/or saves plots. 
	
	:param data: A DataFrame of fully organized word or sentence data.
	:type data: pd.DataFrame
	:param title: A title for the plot.
	:type title: str
	:param save_name: The name for the saved plot PNG file. 
		Only required if 'save' is set to True.
	:type save_name: str or None
	:param show: Either True or False. Determines whether or not to display
		the plots as they are created.
	:type show: bool
	:param save: Either True or False. Determines whether or not to save
		the plots as they are created. 
	:type save: bool
	:return: Optionally saves plots as PNG files.
	:rtype: None
	"""
	# Check for valid arguments
	if not isinstance(data, pd.DataFrame):
		logger.error("No data provided!")
		return
	if not title:
		logger.error("No plot title provided!")
		return
	if save:
		if not save_name:
			logger.error("You must provide a name for the saved plot!")
			return
	# Plot
	sns.boxplot(data=data, orient="v")
	plt.ylim([0,100])
	plt.title(title + f"\n(n={data.shape[0]})")
	plt.ylabel("Percent Correct (%)")
	# Check for save/show
	if save:
		filename = os.path.join(".", "Plots", save_name + ".png")
		try:
			plt.savefig(filename)
		except FileNotFoundError as e:
			logger.error(e)
			logger.info("Creating Plots directory")
			os.mkdir("Plots")
			plt.savefig(filename)
	if show:
		plt.show()

################
# Module Guard #
################
if __name__ == '__main__':
	pass

""" Script to organize and analyze speech in noise data.

This script relies on a single CSV file containing only 
word and sentence score data for a given group (e.g., RIC, CIC). 

Written by: Sarah Iverson, Travis M. Moore
Last edited: July 15, 2024
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
logger.setLevel(logging.INFO)
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
	""" Import CSV data using a tkinter filedialog for navigation. """
	# Set up GUI root to use filedialog
	root = tk.Tk()
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
	""" Return word and sentence data in separate dataframes. """
	# Get original column names
	cols = data.columns
	# Filter col names by words and sentences
	word_col_names = [value for value in cols if 'Words' in value]
	sentence_col_names = [value for value in cols if 'Sentences' in value]
	# Select word and sentence data separately
	word_data = data[word_col_names].copy()
	sentence_data = data[sentence_col_names].copy()
	# Reformat column names for plots
	new_word_col_names = []
	for col in word_col_names:
		temp = col.split('_')[:-1]
		temp = ' '.join(temp)
		new_word_col_names.append(temp)
	new_sentence_col_names = []
	for col in sentence_col_names:
		temp = col.split('_')[:-1]
		temp = ' '.join(temp)
		new_sentence_col_names.append(temp)
	# Rename dataframe columns
	word_data.columns = new_word_col_names
	sentence_data.columns = new_sentence_col_names
	return word_data, sentence_data

def friedman_test(data, condition):
	""" Conduct Friedman Test and log results to console. """
	statistic, pvalue = stats.friedmanchisquare(*data.values.tolist())
	statistic = np.round(statistic, 3)
	pvalue = np.round(pvalue, 3)
	logger.info("")
	logger.info("Friedman Test for %s", condition)
	logger.info("statistic: %s", np.round(statistic, 3))
	logger.info("p-value: %s", np.round(pvalue, 3))

def wilcoxon_test(data, condition):
	""" Conduct Wilcoxon Test and log results to console. """
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
	""" Generic plot with save and show/hide functionality. """
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
	sns.boxplot(
		data=sentence_data, 
		orient="v"
	)
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

	# Get data from file browser
	#data = browse_for_data()

	# Get data from file path ('./' refers to the code's root folder)
	data = pd.read_csv('./afton_sin_test_data.csv')

	# Prepare word and sentence data
	word_data, sentence_data = organize_data(data)

	# Friedman test
	friedman_test(word_data, "words")
	friedman_test(sentence_data, "sentences")

	# Wilcoxon Test
	wilcoxon_test(word_data, "words")
	wilcoxon_test(sentence_data, "sentences")

	# Make plots
	# Words
	make_plots(
		data=word_data,
		title="Word-Level PC at Fixed Level",
		save_name="word_data",
		show=True,
		save=False
	)
	# Sentences
	make_plots(
		data=sentence_data,
		title="Sentence-Level PC at Fixed Level",
		save_name="sentence_data",
		show=True,
		save=False
	)

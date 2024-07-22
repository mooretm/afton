""" Script to organize and analyze speech in noise data.

This script imports functions from 'sin.py' (located in 
the 'models' folder).

Written by: Travis M. Moore and Sarah Iverson

Last edited: July 22, 2024
"""

###########
# Imports #
###########
# Standard library
import logging

# Third party
import pandas as pd

# Custom modules
from models import sin

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

##########
# Script #
##########
# Get data from file browser
#data = browse_for_data()

# Get data from file path ('./' refers to the root folder)
data = pd.read_csv('./afton_sin_test_data.csv')

# Prepare word and sentence data
word_data, sentence_data = sin.organize_data(data)

# Friedman test
sin.friedman_test(word_data, "words")
sin.friedman_test(sentence_data, "sentences")

# Wilcoxon Test
sin.wilcoxon_test(word_data, "words")
sin.wilcoxon_test(sentence_data, "sentences")

# Make word-level plots
sin.make_plots(
	data=word_data,
	title="Word-Level PC at Fixed Level",
	save_name="word_data",
	show=True,
	save=False
)
# Make sentence-level plots
sin.make_plots(
	data=sentence_data,
	title="Sentence-Level PC at Fixed Level",
	save_name="sentence_data",
	show=True,
	save=False
)

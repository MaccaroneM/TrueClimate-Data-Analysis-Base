import requests
import pprint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# General structure of how I want to accomplish this:
"""
gather data (both through APIS and from manually uploaded data)
categorize and unify the data sets, isolating CO2 emissions
run data viz comparisons
    particularly 3d comparisons
run simple logic to append to explanations of sectors
store both results to program files
"""

coal_emissions = pd.read_excel('')

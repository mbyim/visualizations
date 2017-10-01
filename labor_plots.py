import sqlite3
import pandas as pd
import matplotlib as mpl
import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable
mpl.use('TkAgg')
import matplotlib.pyplot as plt
import geopandas as gp
import shapely

#Connect to sqlite databse
def connect():
    db = sqlite3.connect('world_indicators.sqlite')
    cursor = db.cursor()
    return cursor, db

def line_plot():
	cursor, db = connect()
	df = pd.read_sql_query("""SELECT CountryName, IndicatorName, IndicatorCode, Year, Value
	                                        FROM Indicators
	                                        WHERE IndicatorCode = 'SL.TLF.ACTI.ZS' 
	                                        AND CountryCode IN ('USA', 'JPN', 'CHN', 'DEU', 'FRA', 'CAN')
	                                        AND Year >= 1990 """, db)



	 
	plt.style.use('ggplot')
	fig, ax = plt.subplots(figsize=(8, 5.5))

	ax.set_facecolor('white')
	ax.tick_params(colors='black', labelsize=6.5)
	ax.spines['left'].set_color('black')
	ax.spines['bottom'].set_color('black')



	for country in df['CountryName'].unique():
	    ax.plot(df[df['CountryName'] == country].Year, 
	             df[df['CountryName'] == country].Value)
	    
	    if country == 'Germany':
	        y_position = max(df[(df['CountryName'] == country) & (df['Year'] == 2014)].Value) - .2
	    else:
	        y_position = max(df[(df['CountryName'] == country) & (df['Year'] == 2014)].Value)
	    ax.text(2014.2, y_position, country, fontsize = 8, verticalalignment='center')
	plt.xlim(1990, 2017)
	ax.grid(False)
	ax.text(1992, 85.5, 'Labor Force Participation Rates: % of Total Population aged 15-64 (ICO estimate)', fontsize=9)
	plt.savefig('labor_rates.jpg', dpi=1000, transparent=True)


def geo_plot():

	#Get labor data
	cursor, db = connect()
	df = pd.read_sql_query("""SELECT CountryName, Value
								FROM Indicators
								WHERE IndicatorCode = 'SL.TLF.ACTI.ZS' 
								AND Year = 2014 
								""", db)

	
	#Get polygon data
	countries = gp.GeoDataFrame.from_file('cntry00/cntry00.shp')
	
	#Merge dataframes
	countries = countries.merge(df, how='left', left_on='SOVEREIGN', right_on='CountryName')
	countries = countries[(countries.POP_CNTRY>0) & (countries.SOVEREIGN!="Antarctica")]
	#Get rid of columns we dont need
	countries = countries[['CountryName', 'SOVEREIGN', 'Value', 'geometry']]
	plt.style.use('ggplot')
	fig, ax = plt.subplots(figsize=(21,14))
	countries.plot(ax=ax, column='Value', cmap='winter', legend=False)
	ax.set_aspect('equal')

	#Colorbar
	print(countries['Value'].max(skipna=True))
	print(countries['Value'].min(skipna=True))

	nums=['43.9', '50', '60', '70', '80', '90.5']
	ax_legend = fig.add_axes([0.35, 0.14, 0.3, 0.03], zorder=3)
	cb = mpl.colorbar.ColorbarBase(ax_legend, cmap='winter', orientation='horizontal')
	cb.ax.set_xticklabels(nums, fontsize=13)



	ax.grid(False)
	ax.spines['right'].set_visible(True)
	ax.spines['top'].set_visible(True)
	ax.spines['bottom'].set_visible(True)
	ax.spines['left'].set_visible(True)
	ax.tick_params(axis='y',which='both',left='off',right='off',color='none',labelcolor='none')
	ax.tick_params(axis='x',which='both',top='off',bottom='off',color='none',labelcolor='none')
	plt.title('Labor Force Participation Rate (ages 15-64)')

	
	plt.savefig('labor_rates_geo.jpg', dpi=1000, transparent=True)






if __name__ == '__main__':
	line_plot()
	geo_plot()
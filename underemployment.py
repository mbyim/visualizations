###Underemployment Graphic Script###
import bs4
import csv
import requests
import pandas as pd
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from descartes import PolygonPatch
import geopandas as gp


url = 'https://www.bls.gov/lau/stalt.htm'
request = requests.get(url)

#website data
data = request.text
soup = bs4.BeautifulSoup(data, 'lxml')

#select first tbody tag, which is our table
table = soup.find('tbody')


#Grab Statename and U-5 and U-6
header = ['name', 'U-5', 'U-6']
employment_data = []
for i in range(0,52):
	raw_row = table.find_all('tr')[i]
	state = raw_row.find('p').text
	u5 = raw_row.find_all('td')[-2].text
	u6 = raw_row.find_all('td')[-1].text
	row = [state, u5, u6]
	#add row to employment_data
	employment_data.append(row)

#Move it into pandas df
df = pd.DataFrame(employment_data)
df.columns = header

#Calculate underemployment
df[['U-5','U-6']] = df[['U-5','U-6']].apply(pd.to_numeric)
df['underemployment'] = df['U-6'] - df['U-5']

#Shapefile data into dataframe
filename = 'shapefile_50_states/shapefile_50_states.shp'
data = gp.read_file(filename)
data = data[['name', 'geometry']]
data = data.merge(df,on=['name'])
data = data[(data.name != 'Alaska') & (data.name != 'Hawaii')]


#Begin Plotting
ax = data.plot(column='underemployment', cmap='OrRd')
fig = ax.get_figure()

cax = fig.add_axes([0.85,0.25,.01,.25])
vmin, vmax = float(df['underemployment'].min(axis=0)), float(df['underemployment'].max(axis=0))
sm = plt.cm.ScalarMappable(cmap='OrRd', norm=plt.Normalize(vmin=vmax, vmax=vmin))
sm._A = []
fig.colorbar(sm, cax=cax)

#Set title and other attributes
ax.set_title('Underemployment Rates: 2016 Q3 - 2017 Q2 Averages', fontsize=10)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y',which='both',left='off',right='off',color='none',labelcolor='none')
ax.tick_params(axis='x',which='both',top='off',bottom='off',color='none',labelcolor='none')

smallprint = ax.text(
    0.03, 0,
    'Data Source: https://www.bls.gov/lau/stalt.htm\nAuthor: Martin Yim',
    ha='left', va='bottom',
    size=5.5,
    color='#555555',
    transform=ax.transAxes)

plt.tight_layout()
plt.savefig('underemployment_choropleth.png', dpi=100, alpha=True)
plt.show()


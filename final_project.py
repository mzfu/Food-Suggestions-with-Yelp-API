import json
import sys
import requests
import urllib
import secret_data
import csv
import sqlite3
from bs4 import BeautifulSoup
import plotly.plotly as py
import plotly.graph_objs as go

from urllib.parse import quote


api_key = secret_data.API_KEY
MAPBOX_TOKEN = secret_data.MAPBOX_TOKEN

# for long term memory
STATECSV = 'states.csv'
DBNAME = 'yelp.db'
# CACHE_GOOGLE_MAP = "google_map_cache.json" 

########################################################################
# Part 1: Get business data from the REST API
########################################################################

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'


# Code for making requests from API, return a json dictionary
def request(host, path, api_key, url_params = None):
	"""Given your API_KEY, send a GET request to the API.
	Args:
		host (str): The domain host of the API.
		path (str): The path of the API after the domain.
		API_KEY (str): Your API Key.
		url_params (dict): An optional set of query parameters in the request.
	Returns:
		dict: The JSON response from the request.
	Raises:
		HTTPError: An error occurs from the HTTP request.
	"""
	url_params = url_params or {}
	url = '{0}{1}'.format(host, quote(path.encode('utf8')))
	headers = {
		'Authorization': 'Bearer %s' % api_key,
	}

	print(u'Querying {0} ...'.format(url))

	response = requests.request('GET', url, headers = headers, params = url_params)

	return response.json()


# Code for Caching
CACHE_FNAME = "business_cache.json" # for long term memory
try:
	f = open(CACHE_FNAME, 'r')
	fstr = f.read()
	f.close()
	CACHE_DICTION = json.loads(fstr)
except:
	CACHE_DICTION = {}

def params_unique_combination(baseurl, params_d):
	alphabetized_keys = sorted(params_d.keys())
	res = []
	for k in alphabetized_keys:
		res.append("{}-{}".format(k, params_d[k]))
	return baseurl + "_" + "_".join(res)


def make_request_using_cache(API_HOST, SEARCH_PATH, params_diction):
	base_url = API_HOST + SEARCH_PATH
	unique_ident = params_unique_combination(base_url, params_diction)

	if unique_ident in CACHE_DICTION:
		# print("Getting data from cached file...")
		return CACHE_DICTION[unique_ident]
	else:
		print("Getting data from REST API...")
		
		business_dic = request(API_HOST, SEARCH_PATH, api_key, url_params = params_diction)		
		
		CACHE_DICTION[unique_ident] = business_dic
		cache_dump = json.dumps(CACHE_DICTION)
		f = open(CACHE_FNAME,'w')
		f.write(cache_dump)
		f.close()
		return CACHE_DICTION[unique_ident]


########################################################################
# Part 2: Get the info for each business by web page scraping
########################################################################

# Cache the data from business website
CACHE_site = 'website_cache.json'
try:
	cache_file = open(CACHE_site, 'r')
	cache_contents = cache_file.read()
	CACHE_DICTION_bus = json.loads(cache_contents)
	cache_file.close()

except:
	CACHE_DICTION_bus = {}

def get_unique_key(url):
  return url

def make_request_using_cache_web(url):
	unique_ident = get_unique_key(url)

	## first, look in the cache to see if we already have this data
	if unique_ident in CACHE_DICTION_bus:
		# print("Getting cached data from website file...")
		return CACHE_DICTION_bus[unique_ident]

	## if not, fetch the data afresh, add it to the cache,
	## then write the cache to file
	else:
		print("Making a request for new data from yelp...")
		# Make the request and cache the new data
		resp = requests.get(url)

		# Here in order to decrease the size, we only store the useful information in our cached file
		business_text = resp.text
		business_soup = BeautifulSoup(business_text, 'html.parser')

		
		# Scrape from the 'Hours' section
		hour_dic = {}
		
		try:
			hour_info = business_soup.find('tbody')
			date_hour = hour_info.find_all('tr')
			
			for x in date_hour:
				
				info_date = x.text
				temp_lst = info_date.strip('\n').split()			
				
				if len(temp_lst) > 2 and len(temp_lst) <= 8:
					date = temp_lst[0]
					open_time = temp_lst[1] + temp_lst[2]
					close_time = temp_lst[4] + temp_lst[5]
				elif len(temp_lst) <= 2 and len(temp_lst) >=1:
					date = temp_lst[0]
					open_time = 'None'
					close_time = 'None'
				elif len(temp_lst) >= 8:
					date = temp_lst[0]
					open_time = temp_lst[1] + temp_lst[2]
					if temp_lst[-1] != 'now':
						close_time = temp_lst[-2] + temp_lst[-1]
					else:
						close_time = temp_lst[-4] + temp_lst[-3]
				
				hour_dic[date] = {}
				hour_dic[date]['open_time'] = open_time
				hour_dic[date]['close_time'] = close_time

		except:
			print('Hour information not found...')
			pass

		
		CACHE_DICTION_bus[unique_ident] = hour_dic
		dumped_json_cache = json.dumps(CACHE_DICTION_bus)
		fw = open(CACHE_site,"w")
		fw.write(dumped_json_cache)
		fw.close() # Close the open file
		return CACHE_DICTION_bus[unique_ident]


########################################################################
# Part 3: Make the caching using businesses info 
########################################################################

# Read in all the states data from a csv file
origin_lst = []

with open(STATECSV) as csvDataFile:
	csvReader = csv.reader(csvDataFile)
	for row in csvReader:
		origin_lst.append(row)

state_abbr_lst = []


for small_lst in origin_lst[1:]:
	state_abbr_lst.append(small_lst[1])
# print(state_abbr_lst)

# Make the big json cached file with all states' top 20 businesses info
# For the use of building the database
# !!! Remember to comment this every time run the file !!! 

# for state_abbr in state_abbr_lst:
# 	params_diction = {
# 			'categories': 'food',
# 			'sort_by': 'rating',
# 			'location': state_abbr,
# 			'limit': 20
# 		}
# 	try:
# 		business_for_state_dic = make_request_using_cache(API_HOST, SEARCH_PATH, params_diction)

# 		business_for_state_lst = business_for_state_dic['businesses']
# 		for business in business_for_state_lst:
# 			business_url = business['url']
# 			returned_dic = make_request_using_cache_web(business_url) 
# 			# return a dictionary of hours

# 	except:
# 		print('Fail to make request...')

########################################################################
# Part 4: Make the database using businesses info 
########################################################################

def create_yelp_db():
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
		
		statement = '''
			DROP TABLE IF EXISTS 'State';
		'''
		cur.execute(statement)

		statement = '''
			CREATE TABLE `State` (
				`Id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
				`Name`	TEXT NOT NULL,
				`Abbreviation`	TEXT NOT NULL
			);
		'''
		cur.execute(statement)

		statement = '''
			DROP TABLE IF EXISTS 'City';
		'''
		cur.execute(statement)

		statement = '''
			CREATE TABLE `City` (
				`Id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
				`Name`	TEXT NOT NULL,
				`StateId`	INTEGER
			);
		'''
		cur.execute(statement)

		statement = '''
			DROP TABLE IF EXISTS 'Business';
		'''
		cur.execute(statement)

		statement = '''
			CREATE TABLE `Business` (
				`Id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
				`Name`	TEXT NOT NULL,
				`Rating`	REAL,
				`Title`	TEXT,
				`Latitude`	REAL,
				`Longitude`	REAL,
				`Address`	TEXT,
				`City`	INTEGER,
				`State`	INTEGER,
				`URL` TEXT
			);
		'''
		cur.execute(statement)

		statement = '''
			DROP TABLE IF EXISTS 'Hours';
		'''
		cur.execute(statement)

		statement = '''
			CREATE TABLE `Hours` (
				`BusinessId`	INTEGER NOT NULL,
				`Monday`	TEXT,
				`Tuesday`	TEXT,
				`Wednesday`	TEXT,
				`Thursday`	TEXT,
				`Friday`	TEXT,
				`Saturday`	TEXT,
				`Sunday`	TEXT
			);
		'''
		cur.execute(statement)

		conn.commit()
		conn.close()

	except:
		print('Fail to create ' + DBNAME)

create_yelp_db()
# print("Created Yelp Database")

# Populates yelp database using info we get
def populate_yelp_db():

	# Connect to choc database
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()

	# Populate the State table
	origin_lst = []

	with open(STATECSV) as csvDataFile:
		csvReader = csv.reader(csvDataFile)
		for row in csvReader:
			origin_lst.append(row)

	for inst in origin_lst[1:]:
		insertion = (None, inst[0], inst[1])
		statement = 'INSERT INTO "State" '
		statement += 'VALUES (?, ?, ?)'
		cur.execute(statement, insertion)


	# Populate the City table using the API data
	f = open(CACHE_FNAME, 'r')
	fstr = f.read()
	f.close()
	CACHE_DICTION = json.loads(fstr)

	city_dic = {}
	for unique_ident in CACHE_DICTION.keys():
		single_business_lst = CACHE_DICTION[unique_ident]['businesses']
		
		for business in single_business_lst:
			city = business['location']['city']
			state = business['location']['state']

			if city not in city_dic.keys():
				city_dic[city] = state

	city_info_pop = []
	for key in city_dic:
		single_lst = []
		single_lst.append(key)
		single_lst.append(city_dic[key])
		city_info_pop.append(single_lst)

	for city_info in city_info_pop:
		insertion = (None, city_info[0], city_info[1])
		statement = 'INSERT INTO "City" '
		statement += 'VALUES (?, ?, ?)'
		cur.execute(statement, insertion)

	# Update the StateId in City table
	statement = 'SELECT City.StateId, State.Id '
	statement += 'FROM City LEFT JOIN State ON City.StateId = State.Abbreviation '
	cur.execute(statement)

	result_lst = cur.fetchall()
	no_state_city = []
	
	result_lst_dic = {}
	for return_tup in result_lst:
		if return_tup[0] not in result_lst_dic.keys():
			result_lst_dic[return_tup[0]] = return_tup[1]
		if return_tup[0] not in state_abbr_lst:
			if return_tup[0] not in no_state_city:
				no_state_city.append(return_tup[0])

	new_lst = list(result_lst_dic.items())

	for return_tup in new_lst:
		
		if return_tup[1] != None:
			statement = 'UPDATE City '
			statement += 'SET StateId = '			
			statement += str(return_tup[1]) + ' '				
			statement += "WHERE StateId = '"
			statement += str(return_tup[0]) + "'"
			cur.execute(statement)
	# Also update the StateId for the city not in the US
	for city in no_state_city:
		statement = 'UPDATE City SET StateId = NULL '
		statement += "WHERE StateId = '"
		statement += city + "'"
		cur.execute(statement)
	

	# Populate the Business table using API data
	total_business_lst = []
	for unique_ident in CACHE_DICTION.keys():
		single_business_lst = CACHE_DICTION[unique_ident]['businesses']

		for business in single_business_lst:
			info_for_pop = []
			name = business['name']
			rating = business['rating']
			title = business['categories'][0]['alias']
			latitude = business['coordinates']['latitude']
			longitude = business['coordinates']['longitude']
			address_lst = business['location']['display_address']
			address = ''
			index = 1
			for x in range(len(address_lst)):
				address += address_lst[x]
				if index != len(address_lst):
					address += ', '
				index += 1
			
			city = business['location']['city']
			state = business['location']['state']
			url = business['url']

			info_for_pop.append(name)
			info_for_pop.append(rating)
			info_for_pop.append(title)
			info_for_pop.append(latitude)
			info_for_pop.append(longitude)
			info_for_pop.append(address)
			info_for_pop.append(city)
			info_for_pop.append(state)
			info_for_pop.append(url)

			total_business_lst.append(info_for_pop)

	for business_info in total_business_lst:
		insertion = (None, business_info[0], business_info[1], business_info[2], business_info[3], business_info[4], business_info[5], business_info[6], business_info[7], business_info[8])
		statement = 'INSERT INTO "Business" '
		statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
		cur.execute(statement, insertion)

	# Update the City and State in Business table
	statement = 'SELECT Business.City, City.StateId, State.Abbreviation  '
	statement += 'FROM Business LEFT JOIN City ON Business.City = City.Name '
	statement += 'LEFT JOIN State ON City.StateId = State.Id'
	cur.execute(statement)

	result_lst = cur.fetchall()
	# print(result_lst)
	result_lst_dic = {}

	for return_tup in result_lst:
		if return_tup[0] not in result_lst_dic.keys():
			result_lst_dic[return_tup[0]] = return_tup[1]

	no_state_city = []
	for return_tup in result_lst:
		if return_tup[2] not in state_abbr_lst:
			if return_tup[2] not in no_state_city:
				no_state_city.append(return_tup[0])

	new_lst = list(result_lst_dic.items())

	for return_tup in new_lst:
		
		if return_tup[1] != None:
			statement = 'UPDATE Business '
			statement += 'SET State = '			
			statement += str(return_tup[1]) + ' '				

			statement += 'WHERE City = "'
			statement += str(return_tup[0]) + '"'
			cur.execute(statement)
	# Also update the StateId for the city not in the US
	for city in no_state_city:
		statement = 'UPDATE Business SET State = NULL '
		statement += "WHERE City = '"
		statement += city + "'"
		cur.execute(statement)

	statement = 'SELECT Business.City, City.Id '
	statement += 'FROM Business LEFT JOIN City ON Business.City = City.Name '
	cur.execute(statement)

	result_lst = cur.fetchall()
	
	result_lst_dic = {}
	for return_tup in result_lst:
		if return_tup[0] not in result_lst_dic.keys():
			result_lst_dic[return_tup[0]] = return_tup[1]
		
	new_lst = list(result_lst_dic.items())

	for return_tup in new_lst:
		
		if return_tup[1] != None:
			statement = 'UPDATE Business '
			statement += 'SET City = '			
			statement += str(return_tup[1]) + ' '				

			statement += 'WHERE City = "'
			statement += str(return_tup[0]) + '"'
			cur.execute(statement)


	# Populate the Hours table using date from web scraping
	total_hour_pop = []
	for unique_ident in CACHE_DICTION.keys():
		single_business_lst = CACHE_DICTION[unique_ident]['businesses']

		for business in single_business_lst:
			url = business['url']
			# name = business['name']
			
			single_hour_pop = []
			single_hour_pop.append(url)

			hour_info_dic = make_request_using_cache_web(url)
			
			for date in hour_info_dic.keys():				
				
				open_time = hour_info_dic[date]['open_time']
				close_time = hour_info_dic[date]['close_time']				
				
				if open_time == '12:00am':
					open_24 = '0:00'
				elif open_time == '12:30am':
					open_24 = '0:30'
				elif open_time == '12:00pm':
					open_24 = '12:00'
				elif open_time == '12:30pm':
					open_24 = '12:30'
				elif open_time[-2:] == 'am':
					open_24 = open_time[:-2]
				elif open_time[-2:] == 'pm':
					open_24 = str(int(open_time[:-5]) + 12) + open_time[-5:-2]
				elif open_time == None:
					open_24 = ''

				if close_time == '12:00am':
					close_24 = '24:00'
				elif close_time == '12:30am':
					close_24 = '0:30'
				elif close_time == '12:00pm':
					close_24 = '12:00'
				elif close_time == '12:30pm':
					close_24 = '12:30'
				elif close_time[-2:] == 'am':
					close_24 = close_time[:-2]
				elif close_time[-2:] == 'pm':
					close_24 = str(int(close_time[:-5]) + 12) + close_time[-5:-2]
				elif close_time == None:
					close_24 = ''
				
				date_pop = open_24 + ' - ' + close_24
				if len(date_pop) > 3:
					single_hour_pop.append(date_pop)
				else:
					single_hour_pop.append('None')

			total_hour_pop.append(single_hour_pop)

	for hour_info in total_hour_pop:
		try:
			insertion = (hour_info[0], hour_info[1], hour_info[2], hour_info[3], hour_info[4], hour_info[5], hour_info[6], hour_info[7])
			statement = 'INSERT INTO "Hours" '
			statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
			cur.execute(statement, insertion)
		except:
			pass

	# Update the BusinessId in 'Hours'
	statement = 'SELECT Hours.BusinessId, bus.Id '
	statement += 'FROM Hours LEFT JOIN Business AS bus ON Hours.BusinessId = bus.URL '
	cur.execute(statement)

	result_lst = cur.fetchall()

	for return_tup in result_lst:
		statement = 'UPDATE Hours '
		statement += 'SET BusinessId = '
		statement += str(return_tup[1]) + ' '
		statement += 'WHERE BusinessId = "'
		statement += str(return_tup[0]) + '"'
		cur.execute(statement)

	# Close connection
	conn.commit()
	conn.close()

populate_yelp_db()
# print("Populated Yelp Database")


########################################################################
# Part 5: Data presentation 
########################################################################

# Option 1: plot business for a state
def get_business_for_state(state_abbr):
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()

	statement = 'SELECT Business.Name, Business.Title, Business.Latitude, Business.Longitude, Business.URL '
	statement += 'FROM Business JOIN State ON Business.State = State.Id '
	statement += 'WHERE State.Abbreviation = "'
	statement += state_abbr + '"'
	cur.execute(statement)

	result_lst = cur.fetchall()

	conn.close()

	return result_lst

def plot_business_for_state(state_abbr):
	all_business = get_business_for_state(state_abbr)

	lat_vals = []
	lon_vals = []
	text_vals = []

	for single_bus in all_business:
		lat_vals.append(single_bus[2])
		lon_vals.append(single_bus[3])
		text = single_bus[0] + ' (' + single_bus[1] + ')'
		text_vals.append(text)

	# Find the center of the map
	min_lat = 10000
	max_lat = -10000
	min_lon = 10000
	max_lon = -10000

	for str_v in lat_vals:
		v = float(str_v)
		if v < min_lat:
			min_lat = v
		if v > max_lat:
			max_lat = v
	for str_v in lon_vals:
		v = float(str_v)
		if v < min_lon:
			min_lon = v
		if v > max_lon:
			max_lon = v
	
	lat_axis = [min_lat - 0.03, max_lat + 0.03]
	lon_axis = [min_lon - 0.03, max_lon + 0.03]

	center_lat = (max_lat + min_lat) / 2
	center_lon = (max_lon + min_lon) / 2

	data = [ dict(
		type = 'scattermapbox',
		lon = lon_vals,
		lat = lat_vals,
		text = text_vals,
		mode = 'markers',
		marker = dict(
			size = 10,
			symbol = 'star',
			color = '#FFF389'
		))]

	layout = dict(
		title = 'Foods in ' + state_abbr.upper() + ' on Mapbox<br>(Hover for business name and title)',
		autosize = True,
		showlegend = False,
		mapbox = dict(
			accesstoken = MAPBOX_TOKEN,
			bearing = 0,
			center = {'lat': center_lat, 'lon':center_lon},
			pitch = 0,
			zoom = 10
			),
	)

	fig = dict(data = data, layout = layout )
	py.plot(fig, validate = False, filename = 'Foods in ' + state_abbr.upper())

	return None

# plot_business_for_state('MI')


# Option 2: plot heatmap of the relationship between business title and rating for a list of state
def get_rating_for_states(state_abbr_lst):
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()

	# get a title list with all the titles
	title_lst = []
	
	for state in state_abbr_lst:
		
		statement = 'SELECT DISTINCT Business.Title '
		statement += 'FROM Business JOIN State ON Business.State = State.Id '
		statement += 'WHERE State.Abbreviation = "'
		statement += state + '"'
		cur.execute(statement)

		return_lst = cur.fetchall()
	
		for tup in return_lst:
			if tup[0] not in title_lst:
				title_lst.append(tup[0])

	# get ratings for each title in each state
	total_lst = []

	for state in state_abbr_lst:

		state_rating_lst = []

		for title in title_lst:

			statement = 'SELECT ROUND(AVG(Business.Rating), 2) '
			statement += 'FROM Business JOIN State ON Business.State = State.Id '
			statement += 'WHERE State.Abbreviation = "'
			statement += state + '" AND Business.Title = "'
			statement += title + '"'
			cur.execute(statement)

			rating_single = cur.fetchall()

			state_rating_lst.append(rating_single[0][0])

		total_lst.append(state_rating_lst)

	# print(total_lst)

	conn.close()

	return total_lst, title_lst


def plot_heatmap_for_states(state_abbr_lst):
	return_tup = get_rating_for_states(state_abbr_lst)
	
	trace = go.Heatmap(z = return_tup[0],
				   x = return_tup[1],
				   y = state_abbr_lst,
				   colorscale = [[0, '#B5CBFF'], [1, '#2D6CFF']])
	data=[trace]
	py.plot(data, filename='labelled-heatmap')

	return None

state_lst = ['MI', 'OH','CA', 'AK']
# plot_heatmap_for_states(state_lst)


# Option 3: input a state and a time (date and time), return a list of open business
def get_time_business_for_state(state_abbr, date):
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()

	statement = 'SELECT Business.Name, Business.Title, Business.Rating, Hours.'
	statement += date + ' '
	statement += 'FROM Business JOIN State ON Business.State = State.Id '
	statement += 'JOIN Hours ON Business.Id = Hours.BusinessId '
	statement += 'WHERE State.Abbreviation = "'
	statement += state_abbr + '"'
	
	cur.execute(statement)

	result_lst = cur.fetchall()

	conn.close()

	return result_lst

def give_open_business(state_abbr, date, time):
	all_in_state = get_time_business_for_state(state_abbr, date)
	time_num_input = int(time.split(':')[0]) * 60 + int(time.split(':')[1])

	open_business_lst = []

	for tup in all_in_state:
	
		open_time = tup[-1]
		time_lst = open_time.split(' ')
		final_time_lst = []
		final_time_lst.append(time_lst[0])
		final_time_lst.append(time_lst[-1])
		
		new_number_time = []
		for time in final_time_lst:
			
			time_num = int(time.split(':')[0]) * 60 + int(time.split(':')[1])
			new_number_time.append(time_num)			

		if time_num_input >= new_number_time[0] and time_num_input <= new_number_time[1]:
			open_business_lst.append(tup[0])

	return open_business_lst


# Opetion 4: input a list of state abbreviations, return the most famous type of business for each state and average rating
class FamousBusiness():
	"""docstring for FamousBusiness"""
	def __init__(self, name, title, rating):
		self.name = name
		self.title = title
		self.rating = rating

	def __str__(self):
		return "The best food type in {} is {}, and the average rating for it is {}.".format(self.name, self.title, self.rating)
		

def rate_title(state_abbr_lst):
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()

	all_highest_rate_lst = []

	for state in state_abbr_lst:

		statement = 'SELECT State.Name, Business.Title, ROUND(AVG(Business.Rating), 2) '
		statement += 'FROM Business JOIN State ON Business.State = State.Id '
		statement += 'WHERE State.Abbreviation = "'
		statement += state + '" GROUP BY Business.Title '
		statement += 'ORDER BY ROUND(AVG(Business.Rating), 2) DESC'
		cur.execute(statement)

		return_lst = cur.fetchall()

		highest_title_lst = []
		
		highest_title_lst.append(return_lst[0][0])
		highest_title_lst.append(return_lst[0][1])
		highest_title_lst.append(return_lst[0][2])

		all_highest_rate_lst.append(highest_title_lst)

	conn.close()

	return all_highest_rate_lst


# Make the program interactive
def process_command(command):
	command_lst = command.split(' ')

	if command_lst[0] == 'map':
		if len(command_lst) == 2:
			if command_lst[1] in state_abbr_lst:
				plot_business_for_state(command_lst[1])
			else:
				print(command_lst[1] + ' is not a valid state abbreviation!')
				
		else:
			print('Please input only one state abbreviation.')

	elif command_lst[0] == 'heatmap':
		state_lst = []

		for state_abbr in command_lst[1:]:
			if state_abbr in state_abbr_lst:
				state_lst.append(state_abbr)
			else:
				print(state_abbr + ' is not a valid state abbreviation!')

		if len(state_lst) != 0:
			plot_heatmap_for_states(state_lst)
		else:
			print('Nothing to be plotted for the heatmap for now!')

	elif command_lst[0] == 'open':
		date_lst = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', "Friday", 'Saturday','Sunday']
		if len(command_lst) == 4:
			if command_lst[1] in state_abbr_lst:
				if command_lst[2] in date_lst:
					time = command_lst[3]
					if ':' in time and int(time[:time.find(':')]) <= 24:			
						result_lst_open = give_open_business(command_lst[1], command_lst[2],time)
						print('The businesses open on ' + command_lst[2] + ' in ' + command_lst[1] + ' at ' + time + ':')
						index = 1
						for x in result_lst_open:
							print(str(index) + '. ' + x)
							index += 1
					else:
						print('Please input a valid time!')
				else:
					print('Please input a valid date!')
			else:
				print(command_lst[1] + ' is not a valid state abbreviation!')

		else:
			print('Please make sure to give enough commands to get open business information.')

	elif command_lst[0] == 'title':
		state_lst = []

		for state_abbr in command_lst[1:]:
			if state_abbr in state_abbr_lst:
				state_lst.append(state_abbr)
			else:
				print(state_abbr + ' is not a valid state abbreviation!')
				
		all_highest_rate_lst = rate_title(state_lst)

		for state_info in all_highest_rate_lst:
			famous_business = FamousBusiness(state_info[0], state_info[1],state_info[2])
			print(famous_business)
		
	else:
		print('Command not recognized: ' + command_lst[0])

	return None


def load_help_text():
	with open('help.txt') as f:
		return f.read()

def interactive_prompt():
	help_text = load_help_text()
	response = input('Enter a command:')
	while response != 'exit':

		if response == 'help':
			print(help_text)
			
		else:
			process_command(response)

		response = input('Enter a command: ')

	print('Bye!')

# Make sure nothing runs or prints out when this file is run as a module
if __name__=="__main__":
	interactive_prompt()








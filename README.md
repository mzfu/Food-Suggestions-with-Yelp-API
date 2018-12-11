# SI507_Final
2018Fall_SI507_Final project

#### Data sources ####
1. Yelp Fusion API (base_url: https://api.yelp.com/v3/businesses/search) -- challenge score: 4 
2. Scrape the URL returned by the API -- challenge score: 4

#### Before getting started ####
1. The program will use Plotly to display results, in order to get plotly graphs working, you will need to use a separate file called secret_data.py. This file should contain the plotly_key, plotly_username, a mapbox_token. Sign up for a plot.ly account and visit https://plot.ly/python/getting-started/ to install plotly modules necessary to run use graphs.
2. The program will get data from the Yelp Fusion API, you also need an API Key for Yelp(put in the same secret_data.py file). Visit https://www.yelp.com/developers/v3/manage_app to get one.
3. Use the requirements.txt to see all modules necessary to run the program.

#### Structure of the code ####

****** Main code: file final_project.py ******

Part 1: Access data

1. Get business data from the Yelp API (function: make_request_using_cache)
  a. Implement cache to avoid repeated requests
  b. Use state abbreviations, "food" as key words for searching to get 20 records for each state, sorted by rating.
    All the state abbreviations were downloaded from ‘https://github.com/jasonong/List-of-US-States.git’ as a csv file, 
    curtsy to jasonong!
2. Get the open hour info by web scraping (function: make_request_using_cache_web)
  a. Implement cache to avoid repeated requests
  b. The urls are the ones returned by API from step 1
  

Part 2: Build the database (yelp.db)

1. function: create_yelp_db() 
Create four tables:
  a. Business: containing information about each business
  b. State: including 51 states names and abbreviations
  c. City: including city names and state
  d. Hours: containing opening hours for each business
2. function: populate_yelp_db()
Populate information to each table, and link the tables using primary key - foreign key

Part 3: Data presentation

1. function: plot_business_for_state()
Given a state abbreviation and return a map using plotly with all 20 businesses plotted on the map
2. function: plot_heatmap_for_states()
Given a list of state abbreviations and return a heatmap displaying the relationship between state and food types, colors represents for ratings.
3. function: give_open_business()
Ask for user input of a state abbreviation, date, and time, return a list of open businesses at that time
4. class: FamousBusiness
Inputs are information of a business including name, title, and rating, __str__ print a formatted string displaying the best food type in the state, and the rating.
5. function: rate_title()
Given a list of state abbreviations and pretty print the strings defined in the class FamousBusiness.

Part 4: Make the program interactive

Nicely deal with the bad input.


****** Additional part: file test_final_project.py ******
A series of unittests that determine if data scraping, database building, and user interface are properly configured.

1. class TestSearch
Test for data access.
2. class TestDatabase
Test for database building.
3. class TestBusiness
Test for user interface.

#### User Guide ####

Commands available:

map
	Description: Plot all top 20 businesses for a state.
	Hover for business name and title.

	Input:
		* state=<state abbreviation>
		Description: an abbreviation of a state


heatmap
	Description: Plot a heatmap of the relationship between states and food titles.
	Hover for state abbreviation, name of the business, and average rating for 
	certain type.

	Input:
		* state_lst=<a list of state abbreviations>
		Description: a list of state abbreviations seperated by space


open
	Description: Given a certain state, date and time, return all the businesses 
	open at that time.

	Input:
		* state=<state abbreviation>
		Description: an abbreviation of a state

		* date=<date>
		Description: a valid date of a week, capital the first letter

		* time=<time>
		Description: a time input in 24hr format, e.g.: 18:23


title
	Description: Given a list of states, return the best food types with the average
	rating for that type.

	Options:
		* state_lst=<a list of state abbreviations>
		Description: a list of state abbreviations seperated by space

		
Enjoy playing with the program(;

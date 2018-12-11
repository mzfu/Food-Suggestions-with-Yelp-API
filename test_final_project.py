import unittest
from final_project import *

class TestSearch(unittest.TestCase):
	
	def test_web_scrape(self):
		url_eg = 'https://www.yelp.com/biz/steel-city-pops-homewood-homewood?adjust_creative=iQ75blvBGrTjLAf10hL2pQ&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=iQ75blvBGrTjLAf10hL2pQ'
		result = make_request_using_cache_web(url_eg)
		keys = result.keys()
		x_for_test = {}
		friday_info = result['Fri']['open_time']
		self.assertIn('Mon', keys)
		self.assertEqual(friday_info, "12:00pm")
		

class TestDatabase(unittest.TestCase):

	def test_state_table(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		sql = 'SELECT Name FROM State'
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertIn(('Michigan',), result_list)
		self.assertEqual(len(result_list), 51)

		conn.close()

	def test_city_table(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		sql = 'SELECT Name FROM City'
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertIn(('Detroit',), result_list)
		self.assertEqual(len(result_list), 230)

		sql = '''
			SELECT Name, StateId
			FROM City
			WHERE Name = 'Detroit'
		'''
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertEqual(result_list[0][1], 35)

		sql = '''
			SELECT StateId
			FROM City
			WHERE Name = 'Windsor'
		'''
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertEqual(result_list[0][0], None)

		conn.close()

	def test_business_table(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		sql = '''
			SELECT Name
			FROM Business
			WHERE Rating = 5.0 AND Title = 'coffee'
		'''
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertIn(('The Rolling Pin Bakeshop',), result_list)
		self.assertEqual(len(result_list), 87)

		sql = '''
			SELECT COUNT(*)
			FROM Business
		'''
		results = cur.execute(sql)
		count = results.fetchone()[0]
		self.assertTrue(count == 1020)

		conn.close()

	def test_joins(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		sql = '''
			SELECT City.Name, City.StateId
			FROM City
				JOIN State
				ON City.StateId = State.Id
		'''
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertIn(('Dearborn', 35), result_list)
		self.assertEqual(len(result_list), 229)
		
		sql = '''
			SELECT Business.Name
			FROM Business
				JOIN City
				ON Business.City = City.Id
			WHERE City.Name = "Detroit"
		'''
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertIn(('Honey Bee La Colmena', ), result_list)
		self.assertEqual(len(result_list), 8)

		sql = '''
			SELECT Business.Name
			FROM Business
				JOIN State
				ON Business.State = State.Id
			WHERE State.Abbreviation = "KY"
		'''
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertIn(("Limestone Branch Distillery", ), result_list)
		self.assertEqual(len(result_list), 19)

		conn.close()

class TestBusiness(unittest.TestCase):

	def test_business(self):
		results = give_open_business('MI', 'Friday', '23:45')
		self.assertEqual(results[0], 'Boostan Cafe')

		results = give_open_business('CA', 'Monday', '9:15')
		self.assertIn('Hi-Top Coffee', results)

		results = rate_title(['MI'])
		self.assertEqual(results[0][2], 5.0)

		results = rate_title(['NY', 'OH'])
		self.assertEqual(results[1][1], 'coffee')

unittest.main(verbosity = 2)

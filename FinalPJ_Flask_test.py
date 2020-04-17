import unittest
from FinalPJ_Flask import *

class TestMovieSearch(unittest.TestCase):

    def test_movie_search(self):
        results = process_command('movie year top')
        self.assertTrue(results[0][0]==2 and results[0][1]=='Avengers: Endgame')

        results = process_command('movie year bottom 5')
        self.assertEqual(results[0][1],'The Cabinet of Dr. Caligari (Das Cabinet des Dr. Caligari)')

        results = process_command('movie box_office top 5')
        self.assertEqual(results[0][1],'Star Wars: Episode VII - The Force Awakens')
        self.assertEqual(results[0][3],936658640)

class TestDirectorSearch(unittest.TestCase):

    def test_director_search(self):
        results = process_command('director year top')
        self.assertEqual(results[0][0],'Joe Russo')
        self.assertEqual(results[1][1],2019)
        
        results = process_command('director number_of_movies top')
        self.assertTrue(results[0][0]=='Alfred Hitchcock' and results[0][1]==6)

class TestStudioSearch(unittest.TestCase):

    def test_studio_search(self):
        results = process_command('studio year top 5')
        self.assertTrue(results[0][0]=='New Line Cinema' and results[0][1]==2019)

        results = process_command('studio year bottom')
        self.assertEqual(results[0][0],'Rialto Pictures')
        self.assertEqual(results[3][1],1931)

        results = process_command('studio number_of_movies top 5')
        self.assertEqual(results[0][0],'Warner Bros. Pictures')

        results = process_command('studio number_of_movies bottom')
        self.assertEqual(results[0][0],'21 Laps Entertainment')


class  TestRatingSearch(unittest.TestCase):

    def test_rating_search(self):
        results = process_command('rating year')
        self.assertEqual(results[0][1],1960)

        results = process_command('rating number_of_movies bottom 5')
        self.assertEqual(results[0][1],12)

        results = process_command('rating box_office top')
        self.assertEqual(results[0][0],'PG-13')
        self.assertGreater(results[0][1],290430198)

unittest.main()  
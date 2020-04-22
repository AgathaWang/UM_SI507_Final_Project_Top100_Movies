import requests
from bs4 import BeautifulSoup
import json
import secret
import sqlite3
from flask import Flask, render_template, request
import plotly.graph_objects as go

BASE_URL = 'https://www.rottentomatoes.com'
MOVIES_PATH = '/top/bestofrt/'
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}
endpoint_url = 'http://www.omdbapi.com/'
omdb_api_key = secret.omdb_api_key

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):  # cache is a dict
    if (url in cache.keys()): # the url is our unique key
        print("Using url cache")
        return cache[url]
    else:
        print("Fetching url")
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]
#######API################
def construct_unique_key(baseurl, params):
    param_strings = []
    connector = '_'
    for k in params.keys():
        if k != 'apikey':
            param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key

def make_request(baseurl, params):
    response = requests.get(endpoint_url, params=params)
    return response.json()

def make_api_request_using_cache(baseurl, params, cache):
    request_key = construct_unique_key(baseurl, params)
    if request_key in cache.keys():
        print('Using api cache')
        return cache[request_key]
    else:
        print("Fetching api")
        cache[request_key] = make_request(baseurl,params)
        save_cache(cache)
        return cache[request_key]


## Load the cache, save in global variable
CACHE_DICT = load_cache()

## Make the soup for the movies page
movies_page_url = BASE_URL + MOVIES_PATH
url_text = make_url_request_using_cache(movies_page_url, CACHE_DICT)
soup = BeautifulSoup(url_text, 'html.parser')

top100_movies = {}
## For each movie listed
movie_listing_parent = soup.find('table', class_='table')
movie_listing_trs = movie_listing_parent.find_all('tr',recursive=False)

for movie_listing_tr in movie_listing_trs:
    movie_rank = movie_listing_tr.find('td',class_='bold').string.strip('.')
    movie_name_link = movie_listing_tr.find('a',class_='unstyled articleLink')
    movie_name = movie_name_link.string[:-6].strip()
    movie_year = movie_name_link.string[-5:-1]
    movie_link = movie_name_link['href']  # extract each movie's detail partial url

    movie_details_url = BASE_URL + movie_link  # the complete url for each movie

    ## Make the soup for course details
    url_text = make_url_request_using_cache(movie_details_url, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')

    movie_detail_ul = soup.find('ul',class_='content-meta info')
    movie_detail_lis = movie_detail_ul.find_all('li', class_='meta-row clearfix',recursive=False)
    movie_rating = movie_detail_lis[0].find('div',class_='meta-value').string.split('(')[0].strip()
    movie_director = movie_detail_lis[2].find('a').string
    movie_director_fname = movie_director.split()[0]
    movie_director_lname = movie_director.split()[1]
    movie_runtime = int(movie_detail_lis[-2].find('div',class_='meta-value').find('time').string.strip().split()[0])
    movie_studio = movie_detail_lis[-1].find('div',class_='meta-value').string.strip()
    # get the movie's country and box office
    if ',' in movie_name:
        search_title = movie_name.split(',')[0]
    elif '(' in movie_name:
        search_title = movie_name.split('(')[0].strip()
    else:
        search_title = movie_name
    params = {'apikey': omdb_api_key,'t':search_title}
    result = make_api_request_using_cache(endpoint_url, params, CACHE_DICT)
    movie_country = result["Country"]
    if result["BoxOffice"] != 'N/A':
        movie_boxoffice = int(''.join(result["BoxOffice"].strip('$').split(',')))
    else:
        movie_boxoffice = None

    top100_movies[movie_name] = [movie_rank,movie_name,movie_year,movie_rating,movie_director_fname,movie_director_lname,
        movie_boxoffice,movie_runtime,movie_studio,movie_country]
# create database with movie and director tables
directors = []
movies = []
for key in top100_movies.keys():
    FLname = [top100_movies[key][4],top100_movies[key][5]]
    directors.append(FLname)
    movie_info = top100_movies[key]
    movies.append(movie_info)
# directors is a dict of all directors' name without repetition
directors = [list(t) for t in set(tuple(y) for y in directors)]
movies = [list(t) for t in set(tuple(y) for y in movies)]

DB_NAME = 'topmovies.sqlite'
def create_db():
    conn = sqlite3.connect('topmovies.sqlite')
    cur = conn.cursor()

    drop_movies_sql = 'DROP TABLE IF EXISTS "movie"'
    drop_directors_sql = 'DROP TABLE IF EXISTS "director"'
    
    create_movies_sql = '''
        CREATE TABLE IF NOT EXISTS "movie" (
            "Rank" INTEGER PRIMARY KEY, 
            "Name" TEXT NOT NULL,
            "Year" INTEGER NOT NULL, 
            "Rating" TEXT NOT NULL,
            "Box_office" INTEGER,
            "Runtime" INTEGER NOT NULL,
            "Studio" TEXT NOT NULL, 
            "Country" TEXT NOT NULL,
            "DirectorId" INTEGER NOT NULL
        )
    '''
    create_directors_sql = '''
        CREATE TABLE IF NOT EXISTS 'director'(
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Fname' TEXT NOT NULL,
            'Lname' TEXT NOT NULL
        )
    '''
    cur.execute(drop_movies_sql)
    cur.execute(drop_directors_sql)
    cur.execute(create_movies_sql)
    cur.execute(create_directors_sql)
    conn.commit()
    conn.close()

def load_directors(): 
    insert_director_sql = '''
        INSERT INTO director
        VALUES (NULL, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for director in directors:
        cur.execute(insert_director_sql, director)
    conn.commit()
    conn.close()

def load_movies():
    select_director_id_sql = '''
        SELECT Id FROM director
        WHERE Fname = ? AND Lname = ?
    '''

    insert_movie_sql = '''
        INSERT INTO movie
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
# ['100', 'I Am Not Your Negro', '2017', 'PG-13', 'Raoul', 'Peck', 7120626, 93, 'Magnolia Pictures', 'Switzerland, France, Belgium, USA']
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for movie in movies:
        # get Id for company location
        cur.execute(select_director_id_sql, [movie[4],movie[5]])
        did = cur.fetchone()
        director_id = None  # None is the default value
        if did is not None:
            director_id = did[0]

        cur.execute(insert_movie_sql, [
            movie[0], # rank
            movie[1], # name
            movie[2], # year
            movie[3], # rating
            movie[6], # box_office 
            movie[7], # runtime
            movie[8], # studio
            movie[9], # country
            director_id
        ])
    conn.commit()
    conn.close()

create_db()
load_directors()
load_movies()

# data processing
valid_command_list = ['movie','director','studio','rating']
valid_orderby_list = ['year','box_office','number_of_movies']
valid_tb_list = ['top','bottom']
valid_plot_list = ['barplot','scatterplot']

def formatted_input(word_list):
    formatted_input_dict = {'command':'movie','orderby':'year','tb':'top','limit':10}
    for word in word_list:
        if word.isnumeric():
            formatted_input_dict['limit'] = int(word)
        else:
            if word in valid_command_list:
                formatted_input_dict['command'] = word
            elif word in valid_orderby_list:
                formatted_input_dict['orderby'] = word
            elif word in valid_tb_list:
                formatted_input_dict['tb'] = word
            elif word == valid_plot_list:
                formatted_input_dict['figure'] = word
    return formatted_input_dict

def process_command(command):  # command is a string
    # Read data from a database called choc.db
    DBNAME = 'topmovies.sqlite'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    word_list = command.split()

    formatted_input_dict = formatted_input(word_list)
    query_orderby = ''
    query_where = ''
    # order by X
    if formatted_input_dict['orderby'] == 'year':
        agg = 'min(m.Year)'
        if formatted_input_dict['command'] != 'movie':
            query_orderby = f'order by {agg}'
        else:
            query_orderby = 'order by m.Year'
    elif formatted_input_dict['orderby'] == 'box_office':
        agg = 'round(avg(m.Box_office),1)'
        if formatted_input_dict['command'] == 'rating':
            query_orderby = f'order by {agg}'
        elif formatted_input_dict['command'] == 'movie':
            query_orderby = 'order by m.Box_office'
            query_where = 'where m.Box_office is not NULL'
    elif formatted_input_dict['orderby'] == 'number_of_movies':
        agg = 'count(*)'
        query_orderby = f'order by {agg}'
    if formatted_input_dict['tb'] == 'top':
        query_orderby += ' DESC'

    # select X from X
    if formatted_input_dict['command'] == 'movie':
        query_select = f'''
        SELECT m.Rank, m.Name, m.Year, m.Box_office, d.Fname || ' ' || d.Lname Director
        FROM movie m
        JOIN director d
        ON m.DirectorId = d.Id
        {query_where}
        '''
    elif formatted_input_dict['command'] == 'director':
        query_select = f'''
        SELECT d.Fname || ' ' || d.Lname Director, {agg}
        FROM movie m
        JOIN director d
        ON m.DirectorId = d.Id
        GROUP BY d.Fname
        '''
    elif formatted_input_dict['command'] == 'studio':
        query_select = f'''
        SELECT m.studio, {agg}
        FROM movie m
        GROUP BY m.studio
        '''
    elif formatted_input_dict['command'] == 'rating':
        query_select = f'''
        SELECT m.rating, {agg}
        FROM movie m
        GROUP BY m.rating
        '''
    query_limit = f'limit {formatted_input_dict["limit"]}'
    query_total = query_select + query_orderby + ' ' + query_limit
    print(query_total)
    cur.execute(query_total)
    result = cur.fetchall()  # a list of tuples
    conn.close()
    print(result)
    return result

# use flask
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def bars():
    command = request.form['command']
    sort_by = request.form['sort']
    sort_order = request.form['dir']
    limit = request.form['limit']
    input_str = command + ' ' + sort_by + ' ' + sort_order + ' ' + limit
    results = process_command(input_str)
    plot_result = request.form.get('plot', False)
    if (plot_result):
        if command == 'movie':
            x_vals = [r[1] for r in results]
            if sort_by == 'year':
                y_vals = [r[2] for r in results]
            elif sort_by == 'box_office':
                y_vals = [r[3] for r in results]
        else:
            x_vals = [r[0] for r in results]
            y_vals = [r[1] for r in results]
        bars_data = go.Bar(
            x=x_vals,
            y=y_vals
        )
        fig = go.Figure(data=bars_data)
        div = fig.to_html(full_html=False)
        return render_template('plot.html', plot_div=div)
    else:
            return render_template('results.html',
            column1=command, results=results, sort=sort_by)

if __name__ == '__main__':
    app.run(debug=True)

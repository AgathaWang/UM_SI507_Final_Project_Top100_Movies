# UM SI507 Final Project: Top100 Movies of all time
SI 507 Winter 2020

## Overview
I collected the rank, name, year, director, runtime, studio, and rating of the top 100 movies on the Rotten Tomatoes website. 
The box office and countries of these 100 movies are collected from Open Movie Database. 
I stored these data in the topmovies.sqlite database.

## Methods
### Access the original data
To extract data from Rotten tomatoes, I use scraping to get each movie’s URL and crawling multiple pages. 
To access Open Movie Database, I applied for an API key and get the JSON files. In order to run the file, the API key was stored as a variable called omdb_api_key in the secret.py file, which is not uploaded in this repository.
### Store the data
I stored the data into a database using python sqlite3 package. The director table and movie table are created to store the data.
The DirectorId in the movie table refers to Id in director table.
### Interaction and Presentation
Users can input their commands through websites created by Flask. The results can be shown as a table or bar plot.

## Dodumentation of the tables
### The movie table
Column|Type|Definition
:-|:-|:-
Rank|int|the movie’s rank in the Rotten Tomatoes website. Rank is the primary key.
Name|text|the name of the movie
Year|int|the released year of the movie
Rating|text|the MPAA film rating. The rating is one of G, PG, PG-13, R, and NC-17.
Box_office|int|the box office of the movie (dollar)
Runtime|int|the runtime of the movie (minute)
Studio|text|the studio which produced the movie
Country|text| the country which produced the movie
DirectorId|int| the id of the director in the director table
### The director table
Column|Type|Definition
:-|:-|:-
Id|int| the id of the director. Id is the primary key.
Fname|text| the first name of the director
Lname|text| the last name of the director

## Interact with the program
The users could select the command, sorting method, direction, number of rows, result presentation format through website.
The command is one of **movie(default), director, studio, and rating**. The presentation formation can be a **table or bar plot**.
The direction can be **descending(default) or ascending**. 
The combinition of available commands and attributes are listed in the following table.
Command|Valid options|Order by|Returned records
:-|:-|:-|:-
movie|year or box office|year or box_office|rank,movie name, year, box office, director
director|number of movies or year|number of movies or the minimum year (agg)|director name, agg
studio|number of movies or year|number of movies or the minimum year (agg)|studio, agg
rating|number of movies or year or box office|number of movies or the minimum year or the average box office (agg)|rating, agg

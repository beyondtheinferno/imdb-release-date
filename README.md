# imdb-release-date
Sends the release dates of latest episodes of TV Shows specified via mail. Saves the initial inputs provided by the user into a SQLite3 DB.

## Initial Configurations

Input your mail details into the `from` variable and `password` variable in the script. Also, while using Gmail, enable the ***Access to less secure apps*** in order to allow the python script to be able to send mails via it.

## Requirements

1. bs4 package - for scraping the web using python
2. Internet connectivity while running the script
3. imdb.com shouldn’t be a blocked website :)

## Input format -

Enter your email id and the TV Shows for which you want to find out the release dates of the next episode.

![input1](https://github.com/beyondtheinferno/imdb-release-date/blob/master/assets/input1.png)


The script will scrape the search results from IMDb and ask you for a choice, for each TV Series you mentioned.

![input2](https://github.com/beyondtheinferno/imdb-release-date/blob/master/assets/input2.png)

## OUTPUT - 

The output on the terminal will be as follows, for the TV Shows you’ve entered - 

![output1](https://github.com/beyondtheinferno/imdb-release-date/blob/master/assets/output1.png)

The mail will contain the HTML content as follows - 

![output2](https://github.com/beyondtheinferno/imdb-release-date/blob/master/assets/output2.png)












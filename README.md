# What is it

Parses site pages (all pages that have internal links on them) into graph for
SEO-statistics. Does not evaluate JS, finds and checks links in HTML only.

This simple tool was made for the very basic search engine analysis of big 
content websites. In the output report you will find how many clicks from 
homepage every page is, how many internal links points to it and page's HTTP 
status and redirect url (if it redirects somewhere).

HTTP status and redirects can be used to quickly locate some basic problems 
with pages.

Clicks from / and internal links will help you modify structure of the site 
as the most important to you pages should have more internal links and should 
have less clicks from homepage. Definitely less than 5 clicks, and this is a problem 
sometimes for big content websites.

## Install

```
git clone https://github.com/kilgoretrout1985/site-pages-graph.git
cd site-pages-graph/
python3 -m venv _env
source _env/bin/activate
pip3 install -r requirements.txt
cd site-pages-graph/
```

## Run

```
python3 run.py https://mysite.com/
```

Script generates 2 report options, both containg same data. Just choose the 
one you are comfortable with: 

* CSV file to open it in Excel for example,
* SQLite database for [DB Browser](https://sqlitebrowser.org/) 
  or something else you use for SQLite. 

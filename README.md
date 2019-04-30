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
have less clicks from homepage. Definitely less than 5, and this is a problem 
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

Then open output CSV to see the results.

### Settings

There is a `MAX_THREADS = 15` variable at the head of `run.py` file. Increase 
it to make parsing faster or decrease to lower the load on your website.

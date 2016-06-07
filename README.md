Цитатник Леся Подерв'янського
=============================


## Architecture

The site implemented as relatively primitive single-file PHP script
(since the web hosting provider is not very open to more modern
technologies). The script (web/index.php) implements the search logic
and accesses the data via a read-only SQLite database.


## Search implementation

Since the corpus is relatively small and we require fuzzy matching,
searching is done by matching the query against _all_ phrases
(properly cleaned up and tokenized) and selecting those with the
highest _match score_.

At the bottom level, we use a concept of a _word difference score_,
which measures the difference between two words. We define it as
follows:

![equation](https://latex.codecogs.com/gif.latex?d%20%3D%20%5Cfrac%7BL%28w_1%2C%20w_2%29%7D%7B%5Cmax%28l_1%2Cl_2%29%7D)

where _L_ is Levenshtein edit distance and _l_ is length of each
word. The reason for scaling by the longer word length is to reflect
the fact that for example, an edit distance of 2 between two 4-letter
words is not the same as an edit distance of 2 in 15-letter ones.

Defined this way, the difference score is a real number between 0 and
1, where it is 0 for two identical words (or, strictly speaking, an
insignificant difference between two infinite-length words).

With this score defined, we calculate the phrase similarity score as
follows:

![equation](https://latex.codecogs.com/gif.latex?s%20%3D%20%5Cfrac%7B1%7D%7B1%20&plus;%20N_q%20&plus;%200.01%20*%20N_p%7D)

where _Nq_ is number of _unmatched_ words in the query and _Np_ is
number of _unmatched_ words in candidate quote. The rationale for such
definition is given below:

* The more unmatched words in the query the less good the match is,
  since the user obvious considred those words important.

* On the other hand, a candidate quote in most cases has many more
  words than a query given (since the query will only have a handful
  of most important words). Therefore we don't want the number of
  unmatched words in the candidate quote to affect the score in a
  major way. We use it scaled down by 100 to break a tie when two
  quotes have a good match to query words. In this case a shorter
  quote would score slightly higher.

The similarity score defined this way is a real number from 0 to 1
which is 1 for nearly exact match between two phrases.


## Source data

As a source data we used the text of plays from
http://doslidy.kiev.ua/ . Most of the texts are HTML files (with
little document structure), so the parser does its best trying to make
sense from it. A couple of playes were available eslewhere as text
documents, so the parser is capable of handling them as well.

Although we tried to avoid modifying the source document, in several
cases it was unavoidable, so for now one is advised to use the
documents stored within this project instead of re-downloading the
files.

## Deployment

### Pre-requisites

* Python
* Korn shell
* SQLite3
* PHP5 with SQLite support (for web front-end)


### Deployment procedure

* Build the database

```
cd tools
./build_db
```

This step builds the database in _data/habib.db_.

* Deploy the database file
* Modify _web/config.php_ to reflect the location of the database
file.
* Deploy _web/config.php_, _web/index.php_, and _web/master.css_

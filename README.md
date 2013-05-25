film-habibulina
===============

Цитатник Леся Подерв'янського


Architecture

The site implemented as relatively primitive single-file PHP script
(since the web hosting provider is not very open to more modern
technologies). The script (web/index.php) implements the search logic
and accesses the data via a read-only SQLite database.


Search implementation

Since we require fuzzy matching, searching is done by matching the
query against _all_ phrases (properly cleaned up and tokenized) and
selecting those with the highest _match score_.

At the bottom level, we use a concept of a _word match score_, which
we define as follows:

![equation](http://latex.codecogs.com/gif.latex?s%28w_1%2C%20w_2%29%20%3D%20e%5E%7B-r%20%5Cfrac%7BD%28w_1%2C%20w_2%29%7D%7B%5Cmax%7Bl%28w_1%29%2Cl%28w_2%29%7D%7D%7D)

where _D_ is a Levenshtein word distance, _l(w)_ is a length of word
_w_, and _r_ is a _rate_ parameter. When defined this way, score
exhibits some desireable properties:

* The score value is between 0 and 1 (it is 1 when two words match).
* It is relative to the size of both words (i.e. a single letter
  mismatch for a two-letter words leads to a much lower score than a
  single-letter mismatch for a ten-letter one).
* There is a rate parameter affecting the impact of typos on the
  score, which we can vary to find an optimal value.


Having defined the words score, we define a score of macthing a query
against oin of the tokenized phrases in the DB as a sum of maximum
scores each query word can yield when macthed against each of the
tokens within the phrase we are searching against.



Source data


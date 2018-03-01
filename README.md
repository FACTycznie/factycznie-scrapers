#### Branch note
The goal of this branch is more accurate testing of how well article text is
downloaded. This will be done by measuring the Levenshtein distance between the
parsing result and the groundtruth.

# factscraper
This repository contains scrapers used by **FACTycznie.pl** to update its news database.

### Data to scrape
`factscraper` scrapers are supposed to retrieve the following data from news sites to the best possible extent:
* authors
* article text
* publish date
* sources
* tags

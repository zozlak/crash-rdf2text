# CRASH rdf2text

Scripts for turning RDF triples into continues text for the CRASH hackaton.

## How to run?

* Install deps with `composer update`
* Download sample data with
  ```
  curl https://arche.acdh.oeaw.ac.at/crash/arche_mylius.nt > mylius.nt
  curl https://arche.acdh.oeaw.ac.at/crash/arche_etmira.nt > etmira.nt
  ```
* Run the transormation with
  ```
  php -f rdf2text.php mylius.nt mylius.txt
  php -f rdf2text.php etmira.nt etmira.txt
  ```

# CRASH rdf2text

Scripts for turning RDF triples into continues text for the CRASH hackaton.

## How to run?

* Clone this repo.
* Download sample data with
  ```
  curl https://arche.acdh.oeaw.ac.at/crash/arche_mylius.nt > mylius.nt
  curl https://arche.acdh.oeaw.ac.at/crash/arche_etmira.nt > etmira.nt
  ```
* Continue depending on your prefered programming language.

### PHP

* Obtain the [compoers](https://getcomposer.org/)
* Install deps with `composer update`
* Run the transormation with
  ```
  php -f rdf2text.php mylius.nt mylius.txt
  php -f rdf2text.php etmira.nt etmira.txt
  ```

### Python

* Obtain the [uv](https://docs.astral.sh/uv/)
* Run the transformation with
  ```
  uv run rdf2text.py mylius.nt mylius.txt
  uv run rdf2text.py etmira.nt etmira.txt
  ```

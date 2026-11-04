# CRASH rdf2text

Scripts for transforming RDF triples into continuous text for the CRASH hackathon.

## How to run?

* Clone this repository.
* Download the sample data:
  ``` bash
  curl https://arche.acdh.oeaw.ac.at/crash/arche_mylius.nt > mylius.nt
  curl https://arche.acdh.oeaw.ac.at/crash/arche_etmira.nt > etmira.nt
  ```
* Continue with the instructions for your preferred programming language.

### PHP

* Install [Composer](https://getcomposer.org/)
* Install the dependencies:
  ``` bash
  composer update
  ```
* Run the transformation:
  ``` bash
  php -f rdf2text.php mylius.nt mylius.txt
  php -f rdf2text.php etmira.nt etmira.txt
  ```

### Python

* Install [uv](https://docs.astral.sh/uv/)
* Install the project dependencies:
  ```bash
  uv sync
  ```
  This installs the dependencies listed in `pyproject.toml` and `uv.lock`. If these files are not yet present, add the required dependencies first:
  ```bash
  uv add rdflib matplotlib seaborn python-dateutil
  ```
* Run the transformation:
  ```bash
  uv run rdf2text.py mylius.nt mylius.txt
  uv run rdf2text.py etmira.nt etmira.txt
  ```

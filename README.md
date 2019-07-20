# kgservice

The kgservice is a python module which allows you to query Neo4j databases via pre-defined functions.

## Getting Started

### Technical requirements
Which python version?

*  Python 2.7

Any required libraries? Which versions? How to install them?

*  py2neo version 4.2

   *  `https://py2neo.org/v4/`

   *  install via `$ pip install "py2neo==4.2"`

*  PyYAML

   *  `https://pyyaml.org/`

   *  install via `$ pip install pyyaml`

*  pytest

   *  `https://docs.pytest.org/`

   *  install via `$ pip install pytest pytest-cov`

*  Flake8

   *  `http://flake8.pycqa.org/`

   *  install via `$ pip install flake8`

### Installing
What needs to be entered in config files for the libtrary to run?

* Rename `config.yaml_` to `config.yaml`
*  The following information is stored within the `config.yaml` file:
   *  PROJECT (here: *SIMUTOOL*)
   *  DOMAIN_NAME (here: *http://example.org/*)
   *  BLACKLIST (here: *create, merge, delete, set, remove*)
   *  PARAMS: with notify_endpoint url

   Adjust them to fit your project"s needs.

## Usage

### Create
create node, properties and relations

input: payload (dict of list of dicts of properties, relations and type

i.e. 
```json
{"payload": [
    {
        "type": "http://example.org/tbox/user", 
        "name": "Nasr", 
        "email":"nasr@simutool.com", 
        "uploader":"http://example.org/tbox/production"
    }
]}
```
### Query
execute cypher query (modifying operations excluded)

input: cypher query

i.e. 
```cypher
MATCH (n) RETURN n
```
### Update
set new properties and relations to node

input: payload (dict of node uri, new properties and new relations)

i.e. 
```json
payload = 
{
    "uri": "http://example.org/abox/adrian", 
    "email":"adrian@simutool.com", 
    "contributor": ["http://example.org/abox/ecn", "http://example.org/abox/oven"]
}
```
### Delete
detach ABox-node from its relations and delete it (by given uri)

input: uri (of ABox node)

i.e. 
``
http://example.org/abox/agi
``
### Get
return node"s properties and relations by given uri

input: uri

i.e. 
``
http://example.org/tbox/activity
``
### Get instances
returns all instances and sub-instances of a class

input: class uri

i.e. 
``
http://example.org/tbox/activity
``
### Get self descendants
return TBox node"s properties and its subclasses

input: uri

i.e. 
``
http://example.org/tbox/activity
``

## Testing

### shell output (printings and loggings)
run the following command:

```bash
$ pytest -s -vvv -o log_cli=true
```

### inspect code coverage
run the following command:

```bash
$ pytest -v --cov-report term-missing --cov=kgservice_v_1_0
```

## Contributing

## Versioning

## Authors

* Adrian Lengenfelder - Development
* Nasr Kasrin - Architecture, Project Management
* Daniela Nicklas - Lead

## License

This project is licensed under

## Acknowledgements

* Py2Neo

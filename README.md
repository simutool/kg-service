# kgservice

The kgservice is a knowledge graph database interface, which allows to query the graph via API access, and checks for integrity constraints relative to the domain model (ontology) provided. It takes a pre-defined domain-model and thereby adds semantics to the graph. With use of included specialized queries this information can be retrieved by the user.

The KgService is python service which connects to a running Neo4j database instance.

**Note: This project is archived.**

## Getting Started

### Technical requirements
Python version:

*  Python 2.7

*  python-pip

Python packages (need installation):

*  py2neo version 4.2 (https://py2neo.org/v4/): install via `$ pip install "py2neo==4.2"`

*  PyYAML (https://pyyaml.org/): install via `$ pip install pyyaml`

*  pytest (https://docs.pytest.org/): install via `$ pip install pytest pytest-cov`

*  Flake8 (http://flake8.pycqa.org/): install via `$ pip install flake8`

### Installing
Clone this project into your local destination. It is recommended to access
the interface functions of KgService.py from a front-end application, or
directly via API. If not available or for development purposes, it is also
possible to run it on console.

## Configuration files
You need to adjust the following configuration files to fit your
project's needs:
*  config.yaml (just keep it as it is to start):
   *  PROJECT (e.g.: *SIMUTOOL*)
   *  DOMAIN_NAME (e.g.: *http://example.org/abox*)
   *  BLACKLIST (e.g.: *create, merge, delete, set, remove*)
   *  TERMS:
         - subclass_of (e.g. *subclass_of*)
         - instance_of: (e.g. *type*)
         - identifier: (e.g. *identifier*)
         - model: (e.g. *ABox*)
         - meta: (e.g. *TBox*)

* \_pass.yaml (file has to be created with the format below)
   *  url: *your neo4j instance, including port*
   *  user: *your neo4j user*
   *  pass: *your neo4j password*

## Usage

### Create
create node, properties and relations

```python
This function creates instances and also allows to
directly create relations and properties.

Parameters
______
payload : pl (see format below)
pl : {'payload': [{'att1': val1, ...}, {'att1': val1, ...}]}
    att[i] : relation or property
user : identifier
    Optional parameter. If available, given user will receive
    email notifications.

Example input
______
{'payload': [{
    "title": "Mr NK",
    "mbox": "n.k@uni-bamberg.de",
    "type": "http://example.org/user",
    "description": "Employee"
}]}

Returns
______
payload : pl (see format above)
    Returns the newly created instance and its relations and
    properties.

Example output
______
{'payload': [{
    "title": "Mr NK",
    "mbox": "n.k@uni-bamberg.de",
    "type": "http://example.org/user",
    "description": "Employee",
    "identifier": "http://example.org/xyz123"
}]}
```

### Query
```python
This function allows to perform cypher queries. Modifying operations
are excluded.

Parameters
______
query : cypher query

Example input
______
"MATCH (n) WHERE n.name = 'Mr N.K.' RETURN n.mbox"

Returns
______
payload : pl (see format above)
    Returns the query result

Example output
______
{'payload': [{"n.mbox": "n.k@uni-bamberg.de"}]}
```
### Update
```python
This function updates one or more instances, i.e. it sets new
properties and relations.

Parameters
______
payload : pl (see format below)
pl : {'payload': [{'att1': val1, 'identifier': id}]}
    att[i] : relation or property
    identifier : identifier

Example input
______
{'payload': [{
    "title": "Mr NK new",
    "identifier": "http://example.org/xyz123"
}]}

Returns
______
payload : pl (see format above)
    Returns the updated instance(s) and its relations and
    properties.

Example output
______
{'payload': [{
    "title": "Mr NK new",
    "mbox": "n.k@uni-bamberg.de",
    "type": "http://example.org/user",
    "description": "Employee",
    "identifier": "http://example.org/xyz123"
}]}
```
### Delete
```python
This function deletes instances and outputs True if successful.

Parameters
______
payload : pl (see format below)
pl : {'payload': [{'identifier1': id1}, {'identifier2': val2}]}
    identifier[i] : identifier

Example input
______
{'payload': [{"identifier": "http://example.org/xyz123"}]}

Returns
______
True : Bool
False : Bool

Example output
______
True
```
### Get
```python
This function queries for all attributes (i.e. relations and
properties) of a given instance and returns them if found.

Parameters
______
payload : pl (see format below)
pl : {'payload': [{'identifier1': val1}, {'identifier2': val1}]}
    identifier[i] : identifier

Example input
______
{'payload': [{"identifier": "http://example.org/xyz123"}]}

Returns
______
payload : pl (see format above)
    Returns the instance and its relations and properties.

Example output
______
{'payload': [{
    "title": "Mr NK",
    "mbox": "n.k@uni-bamberg.de",
    "type": "http://example.org/user",
    "description": "Employee",
    "identifier": "http://example.org/xyz123"
}]}
```
### Get instances
```python
This function takes a class identifier and returns all its instances.

Parameters
______
identifier : identifier
    the identifier needs to be a class identifier

Example input
______
"http://example.org/user"

Returns
______
payload : pl (see format above)
    Returns a list of dicts. The dicts contain the instances.

Example output
______
{'payload': [{
    "title": "Mr NK",
    "mbox": "n.k@uni-bamberg.de",
    "type": "http://example.org/user",
    "description": "Employee",
    "identifier": "http://example.org/xyz123"
}]}
```
### Internal functions
Internal used functions are named with an leading underscore ('_helper_function_x').
These functions are non-interface functions and only called internally from other functions.


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


## Versioning
KgService Version 1.0

## Authors

* Adrian Lengenfelder - Development
* Nasr Kasrin - Architecture, Product & Project Management
* Daniela Nicklas - Lead

## License

This project is licensed under Apache.

## Acknowledgements

* Py2Neo

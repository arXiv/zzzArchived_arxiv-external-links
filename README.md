# arXiv external links
Clearinghouse for relations between arXiv e-prints and external resources

## Background
A wide range of requirements and feature requests that we have received from
stakeholders and end users involve attaching metadata about relations between
arXiv e-prints and external resources. This includes things like links to
datasets, code, and other online content, and better support for information
about the published version of record. 

Including this kind of relational metadata in the core arXiv metadata record is
a poor fit given the way that e-prints are versioned, the requirement that
secondary metadata be maintainable outside of the submission process, and the
requirement that support for secondary metadata be as evolvable and extensible
as possible. 

Additionally, we need to bring forward into NG the automated routines that we
use to harvest relational metadata (e.g. DOIs, journal citations) from other
publishing platforms. A shortcoming of the classic system is that the
provenance of these kinds of metadata are not tracked, which presents
challenges for our partners to interpret and use those metadata downstream.

## Goals

1. Store information about relationships between e-prints and external
   resources:
    
    - Published versions, e.g. via DOIs
    - Datasets
    - Code repositories
    - Multimedia
    - Methods/protocols
    - Related works
    - Blogs and other websites
    - Etc

2. Track provenance/history of this information.

    - When it was added,
    - How/by whom

3. Provide APIs for retrieving this information, adding new relations.
4. Provide an intuitive user interface for authors to curate these relations
   for their e-prints.

## Requirements

1. Author-owners can add, edit, deactivate relationships via an html ui. View
   aggregated relations, view detailed provenance log. 
2. Authorized API clients can add, edit, deactivate relationships via JSON API.
   Read aggregated relations, read detailed provenance log. 
3. Anonymous users, clients can view/read aggregated relations, provenance of
   active relations.
3. Relation data are immutable. 

    - Add means create new assertion about relation.
    - Edit means create new assertion that supercedes a previous assertion.
    - Deactivate means create new assertion that a previous relation is
      incorrect, should be suppressed.

4. Relation data model includes  

    - Type of relation
    - E-print id and version
    - Type of resource
    - Canonical identifier for resource (doi, uri, etc)
    - Freeform description of relation
    - Datetime added
    - Client + user who created
    - identifier of relation superceded or suppressed

5. Emits event on Kinesis stream when data is added.
6. For each resource type, mechanism to verify that resource exists.

## Constraints

1. Flask app that follows the design approach outlined in  https://arxiv.github.io/arxiv-arxitecture/crosscutting/services.html . Can be deployed as a Docker image, e.g with uWSGI application server
2. Separate blueprints for API, user interface
3. Use [arXiv base](https://github.com/arXiv/arxiv-base) for base templates, error handling, etc
4. Use [arXiv auth](https://github.com/arXiv/arxiv-auth) for authn/z
5. API documented with OpenAPI 3 and JSON schema

## Code overview

This project follows the general design approach described
[here](https://arxiv.github.io/arxiv-arxitecture/crosscutting/services.html).

The application source lives in [``relations/``](tree/develop/relations). 

The application factory module
[``relations/factory.py``](blob/develop/relations/factory.py) defines the
construction of two [Flask](http://flask.pocoo.org/) apps: (1) an API
application that provides the REST API, and an UI application that provides
views for human users.

Note that these apps use the following general tooling from the arXiv project:

- [``arxiv.base.Base``](https://arxiv.github.io/arxiv-base/arxiv/arxiv.base.html#arxiv.base.Base),
  which adds some useful things like exception handlers, an ``arxiv`` URL
  converter, etc.
- The [``arxiv.users``](https://arxiv.github.io/arxiv-auth/) library, which
  adds tooling for authnz/.

In general, it's a good idea to get comfortable with the [``arxiv`` namespaced
packages](https://arxiv.github.io/arxiv-base), as there are several useful
tools there.

HTTP routing is implemented in the [``routes``
module](tree/develop/relations/routes). The API and UI each have their own
[blueprint](http://flask.pocoo.org/docs/1.0/blueprints/). Routing functions
don't implement much logic; they are there to provide an interface to the
controller functions.

Controller functions do the work of handling requests. They are defined in 
[``relations/controllers.py``](blob/develop/relations/controllers.py). 
Controllers orchestrate the real work; they use domain objects and services
(below) to carry out work to handle requests.

The service domain is defined in
[``relations/domain.py``](blob/develop/relations/domain.py). The domain is
comprised of classes or other structs that define the main concepts of the
application, and the core domain logic/rules. See
https://arxiv.github.io/arxiv-arxitecture/crosscutting/services.html#data-domain
for details.

[Service
modules](https://arxiv.github.io/arxiv-arxitecture/crosscutting/services.html#service-modules)
can be found in [``relations/services/``](tree/develop/relations/services).
This is where (for example) a Kinesis notification producer would be 
implemented.

## Quick-start

We use [Pipenv](https://github.com/pypa/pipenv) for dependency management.

```bash
pipenv install --dev
```

You can run either the API or the UI using the Flask development server.

```bash
FLASK_APP=ui.py FLASK_DEBUG=1 pipenv run flask run
```

Dockerfiles are also provided in the root of this repository. These use uWSGI and the
corresponding ``wsgi_[xxx].py`` entrypoints.

## Contributing

Please see the [arXiv contributor
guidelines](https://github.com/arXiv/.github/blob/master/CONTRIBUTING.md) for
tips on getting started.

## Code of Conduct

All contributors are expected to adhere to the [arXiv Code of
Conduct](https://arxiv.org/help/policies/code_of_conduct).
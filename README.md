# arXiv external links
Clearinghouse for relations between arXiv e-prints and external resources

## Background
A wide range of requirements and feature requests that we have received from stakeholders and end users involve attaching metadata about relations between arXiv e-prints and external resources. This includes things like links to datasets, code, and other online content, and better support for information about the published version of record. 

Including this kind of relational metadata in the core arXiv metadata record is a poor fit given the way that e-prints are versioned, the requirement that secondary metadata be maintainable outside of the submission process, and the requirement that support for secondary metadata be as evolvable and extensible as possible. 

Additionally, we need to bring forward into NG the automated routines that we use to harvest relational metadata (e.g. DOIs, journal citations) from other publishing platforms. A shortcoming of the classic system is that the provenance of these kinds of metadata are not tracked, which presents challenges for our partners to interpret and use those metadata downstream.

## Goals

1. Store information about relationships between e-prints and external resources:
    
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
4. Provide an intuitive user interface for authors to curate these relations for their e-prints.

## Requirements

1. Author-owners can add, edit, deactivate relationships via an html ui. View aggregated relations, view detailed provenance log. 
2. Authorized API clients can add, edit, deactivate relationships via JSON API. Read aggregated relations, read detailed provenance log. 
3. Anonymous users, clients can view/read aggregated relations, provenance of active relations.
3. Relation data are immutable. 
    - Add means create new assertion about relation.
    - Edit means create new assertion that supercedes a previous assertion.
    - Deactivate means create new assertion that a previous relation is incorrect, should be suppressed.
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
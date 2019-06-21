"""
Development entry-point for the API application.

Intended for use with the Flask development server. Run like:

.. code-block:: bash

   FLASK_APP=api.py FLASK_DEBUG=1 pipenv run flask run


"""
from relations.factory import create_api_app

app = create_api_app()

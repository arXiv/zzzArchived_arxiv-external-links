"""
Development entry-point for the UI application.

Intended for use with the Flask development server. Run like:

.. code-block:: bash

   FLASK_APP=ui.py FLASK_DEBUG=1 pipenv run flask run


"""
from relations.factory import create_ui_app

app = create_ui_app()

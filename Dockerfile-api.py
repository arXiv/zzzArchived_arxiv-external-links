# arxiv/external-relations-api
#
# Defines the runtime for the arXiv external relations service.

FROM arxiv/base:latest

WORKDIR /opt/arxiv

# Add Python application and configuration.
RUN pip install -U pip pipenv

ADD wsgi_api.py /opt/arxiv/wsgi.py
ADD uwsgi.ini Pipfile Pipfile.lock /opt/arxiv/
RUN pipenv install

ENV PATH "/opt/arxiv:${PATH}"

ENV LC_ALL en_US.utf8
ENV LANG en_US.utf8
ENV LOGLEVEL 40

ENV APPLICATION_ROOT "/"

EXPOSE 8000

ENTRYPOINT ["pipenv", "run"]
CMD ["uwsgi", "--ini", "/opt/arxiv/uwsgi.ini"]

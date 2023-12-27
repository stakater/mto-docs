# Multi Tenant Operator Documentation

Documentation for [Multi Tenant Operator](https://www.stakater.com/mto)


SAAP docs are built using [MkDocs](https://github.com/mkdocs/mkdocs) which is based on Python.

## GitHub Actions

This repository has Github action workflow which checks the quality of the documentation and builds the Dockerfile image on Pull Requests. On a push to the main branch, it will create a GitHub release and push the built Dockerfile image to an image repository.

## Build locally

There are at least three options to get fast continuous feedback during local development:

1. Build and run the docs using the Dockerfile image
2. Run the commands locally

### Build Dockerfile image and run container

Build Dockerfile test image:

```bash
$ docker build . -t test
```

Run test container:

```bash
$ docker run -p 8080:8080 test
```

Then access the docs on [`localhost:8080`](localhost:8080).

### Run commands locally

Use [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html) to set up Python virtual environments.

Install [Python 3](https://www.python.org/downloads/).

Install mkdocs-material and mermaid plugin:

```bash
$ pip3 install mkdocs-material mkdocs-mermaid2-plugin mkdocs-glightbox
```

Finally serve the docs using the built-in web server which is based on Python http server - note that the production build will use Nginx instead:

```bash
$ mkdocs serve
```

or

```bash
$ python3 -m mkdocs serve
```

### QA Checks

Markdown linting:

```bash
$ brew install markdownlint-cli
$ markdownlint -c .markdownlint.yaml content
```

Spell checking:

```bash
$ brew install vale
$ vale content
```

## Use Tilt

Install [Tilt](https://docs.tilt.dev/index.html), then run:

```bash
$ tilt up
```

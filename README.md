# Multi Tenant Operator Documentation

This repository contains the source for the documentation for [Multi Tenant Operator](https://www.stakater.com/mto). It is built using [MkDocs](https://github.com/mkdocs/mkdocs) which is based on Python. It is also versioned using [mike](https://github.com/jimporter/mike).

## Latest doc version

Before deploying or deleting a version, make sure to specify the correct latest version in the workflow files.

Make sure the latest doc version is also specified in the versioned branches.

## GitHub Actions

This repository has [GitHub action workflow](./.github/workflows/) which checks the quality of the documentation and builds the [`Dockerfile`](./Dockerfile) image on Pull Requests. On a push to the `main` branch, it will create a GitHub release and push the built image to an image repository.

## How to make changes

Fork the repository and make a pull request.

For MkDocs overrides, it is important to know that you should only make changes in the [`theme_override`](./theme_override/) and the [`content`](./content/) directory. Also, be mindful of only changing the [`theme_override/mkdocs.yml`](./theme_override/mkdocs.yml) file since there are more than one such file.

## Take update on git submodule

This project contains a git submodule and if you wish to take an update on it, you can use this command:

```bash
git submodule update --init --recursive --remote
```

View the [`.gitmodules`](./.gitmodules) file to see linked git submodules.

## Build locally

There are at least two options to get fast continuous feedback during local development:

1. Build and run the docs using the Dockerfile image
1. Run the commands locally

### Build Dockerfile image and run container

Build Dockerfile test image:

```bash
docker build . -t test -f Dockerfilelocal
```

Run test container:

```bash
docker run -p 8080:8080 test
```

Then access the docs on [`localhost:8080`](localhost:8080).

### Run commands locally

Use [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html) to set up Python virtual environment.

Install [Python 3](https://www.python.org/downloads/).

Install python environment dependencies if you are using any other than what is defined in `theme_common`.

Then run below script to prepare theme from local and common theme resources. It will output to `dist/_theme` directory and create `mkdocs.yml` file in root directory. We are also installing the python dependencies coming from `theme_common` here.

```bash
./prepare_theme.sh
```

Finally, serve the docs using the built-in web server which is based on Python http server - note that the production build will use `nginx` instead:

```bash
mike serve
```

or

```bash
python3 -m mike serve
```

Then, you can make changes in `content` or `dist/_theme` folder. Please note that `dist/_theme` is a build folder and any changes made here will be lost if you do not move them to the `theme_common` or the `theme_override` folder.

### QA Checks

You can run QA checks locally. They are also run as part of pull request builds.

To run markdown linting:

```bash
brew install markdownlint-cli
markdownlint -c .markdownlint.yaml content
```

Spell checking:

```bash
brew install vale
vale sync
vale content
```

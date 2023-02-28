FROM python:3.11-alpine
ARG VERSION

LABEL name="Multi Tenant Operator Documentation" \
      maintainer="Stakater <hello@stakater.com>" \
      vendor="Stakater" \
      release="1" \
      summary="Multi Tenant Operator Documentation"

RUN pip3 install mkdocs-material mkdocs-mermaid2-plugin mike

# Set workdir
RUN mkdir -p $HOME/handbook
WORKDIR $HOME/handbook

# Copy the entire content
COPY --chown=1001:root . .

# Build the content
RUN mike deploy --update-aliases $VERSION latest
RUN mike set-default latest

# Set non-root user
USER 1001

EXPOSE 8080
CMD ["python", "-m", "http.server", "8080", "-d", "./site"]

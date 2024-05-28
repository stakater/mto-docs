FROM python:3.12-alpine as builder

RUN pip3 install mkdocs-mermaid2-plugin mkdocs-table-reader-plugin mkdocs-include-markdown-plugin

# set workdir
RUN mkdir -p $HOME/application
WORKDIR $HOME/application

# copy the entire application
COPY --chown=1001:root . .

# build the docs
RUN chmod +x prepare_theme.sh && ./prepare_theme.sh
RUN mkdocs build

FROM nginxinc/nginx-unprivileged:1.26-alpine as deploy
COPY --from=builder $HOME/application/site/ /usr/share/nginx/html/mto/
COPY default.conf /etc/nginx/conf.d/

# set non-root user
USER 1001

LABEL name="Multi Tenant Operator Documentation" \
      maintainer="Stakater <hello@stakater.com>" \
      vendor="Stakater" \
      release="1" \
      summary="Documentation for Multi Tenant Operator"

EXPOSE 8080:8080/tcp

CMD ["nginx", "-g", "daemon off;"]
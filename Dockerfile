FROM python:3.12-alpine as builder

RUN pip3 install mkdocs-material mkdocs-mermaid2-plugin mkdocs-glightbox

# set workdir
RUN mkdir -p $HOME/application
WORKDIR $HOME/application

# copy the entire application
COPY --chown=1001:root . .

# pre-mkbuild step, we are infusing common and local theme changes
RUN python theme_common/scripts/combine_theme_resources.py theme_common/resources theme_override/resources dist/_theme
RUN python theme_common/scripts/combine_mkdocs_config_yaml.py theme_common/mkdocs.yml theme_override/mkdocs.yml mkdocs.yml

RUN rm -f 'prepare_theme.sh' && \
    rm -rf theme_global && \
    rm -rf theme_common

# build the docs
RUN mkdocs build
# remove the build theme because it is not needed after site is build.
RUN rm -rf dist

FROM nginxinc/nginx-unprivileged:1.25-alpine as deploy
COPY --from=builder $HOME/application/site/ /usr/share/nginx/html/
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

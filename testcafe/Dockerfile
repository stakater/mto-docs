FROM node:22-alpine
WORKDIR testcafe

ENV XDG_DOWNLOAD_DIR=/opt/JDownloader/Downloads

COPY src src
COPY package.json package.json

RUN echo "Install build deps.." \
  && apk --update --no-cache add \
    chromium \
    tzdata

RUN yarn

CMD ["yarn", "start"]

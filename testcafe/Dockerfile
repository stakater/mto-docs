# Pinned image ships TestCafe with a matching Chromium, so a distro browser update can't break the tests
FROM testcafe/testcafe:3.7.7

ARG CURRENT_BRANCH
ENV CURRENT_BRANCH=$CURRENT_BRANCH

COPY src /tests/src

CMD ["chromium:headless", "/tests/src/**.ts", "--disable-native-automation", "--browser-init-timeout", "60000", "--page-load-timeout", "30000"]

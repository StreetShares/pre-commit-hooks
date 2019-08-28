FROM python:2-alpine as builder
ENV PYLINT_VERSION=1.9.5
SHELL ["/bin/ash", "-o", "pipefail", "-c"]
RUN set -x && \
  pip install --no-cache-dir --no-compile "pylint>=${PYLINT_VERSION}" && \
  find /usr/local/lib/ -name '__pycache__' -print0 | xargs -0 -n1 rm -rf && \
  find /usr/local/lib/ -name '*.pyc' -print0 | xargs -0 -n1 rm -rf

FROM python:2-alpine as production
COPY --from=builder /usr/local/lib/python2.7/site-packages/ /usr/local/lib/python2.7/site-packages/
COPY --from=builder /usr/local/bin/pylint /usr/local/bin/pylint

WORKDIR /data
ENTRYPOINT ["pylint"]
CMD ["--version"]

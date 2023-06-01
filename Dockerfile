FROM curlimages/curl:latest AS builder

ARG VERSION
RUN set -eux; \
    ARCHIVE="nomad_${VERSION}_linux_amd64.zip"; \
    curl -s -o /tmp/nomad.zip https://releases.hashicorp.com/nomad/${VERSION}/${ARCHIVE}; \
    { \
      SHA256=$(curl -s https://releases.hashicorp.com/nomad/${VERSION}/nomad_${VERSION}_SHA256SUMS | grep "$ARCHIVE" | awk '{print $1}'); \
      sha256sum -c <(printf "$SHA256  /tmp/nomad.zip"); \
    }; \
    unzip -d /tmp /tmp/nomad.zip;

ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY --from=builder /tmp/nomad /usr/local/bin/nomad

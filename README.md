# ⚠️ Superseded by Officiel Docker Image since 1.4 (https://hub.docker.com/r/hashicorp/nomad)

# nomad-cli

This repository builds Docker image with [Nomad](https://www.nomadproject.io/) binary in it.
See https://github.com/BDelacour/nomad-cli for details.

*Disclaimer : It is an unofficial image and it is meant to be used as utility for your deployment pipelines.*

## Usage

```
docker run \
  --rm \
  --env NOMAD_ADDR=http://your-nomad-cluster:4646 \
  delaco/nomad-cli:latest \
  nomad status
```

## Build

The CI runs every night and builds the latest community version if needed (from https://releases.hashicorp.com/nomad/).

## Contributing

* Fork the project
* Modify or add what you need
* Send a pull request

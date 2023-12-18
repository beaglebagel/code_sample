#!/usr/bin/env bash

set -euo pipefail # Bash "strict mode"
script_dirpath="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dirpath="$(dirname "${script_dirpath}")"

# ==================================================================================================
#                                             Constants
# ==================================================================================================
DOCKER_IMAGE="kurtosis-ci-scheduler"

# =============================================================================
#                                 Main Code
# =============================================================================
# Checks if dockerignore file is in the root path
if ! [ -f "${root_dirpath}"/.dockerignore ]; then
  echo "Error: No .dockerignore file found in server root '${root_dirpath}'; this is required so Docker caching is enabled and the image builds remain quick" >&2
  exit 1
fi

# Build Docker image
dockerfile_filepath="${root_dirpath}/Dockerfile"
echo "Building server into a Docker image named '${DOCKER_IMAGE}'..."
if ! docker build -t "${DOCKER_IMAGE}" -f "${dockerfile_filepath}" "${root_dirpath}"; then
  echo "Error: Docker build of the server failed" >&2
  exit 1
fi
echo "Successfully built Docker image '${DOCKER_IMAGE}' containing the CI scheduler"

import json
import os
import re
from functools import cmp_to_key

import requests
import semver

#DOCKER_NAMESPACE = os.getenv("DOCKER_NAMESPACE")
DOCKER_NAMESPACE = "testing"
assert DOCKER_NAMESPACE is not None
DOCKER_IMAGE = os.getenv("DOCKER_IMAGE")
assert DOCKER_IMAGE is not None


def get_published_image_tags():
    response = requests.get(f"https://registry.hub.docker.com/v2/namespaces/{DOCKER_NAMESPACE}/repositories/{DOCKER_IMAGE}/tags?page_size=100")
    response.raise_for_status()

    return [result['name'] for result in response.json()['results']]


def get_repo_tags():
    response = requests.get("https://api.github.com/repos/hashicorp/nomad/git/refs/tags")
    response.raise_for_status()

    refs = [item['ref'] for item in response.json()]
    mapped_refs = map(lambda ref: ref.replace("refs/tags/v", ""), refs)
    valid_tag_regex = re.compile(r"^[1-9]+\.[0-9]+\.[0-9]+$")
    valid_tags = filter(lambda tag: valid_tag_regex.search(tag) is not None, mapped_refs)
    return sorted(list(valid_tags), key=cmp_to_key(semver.compare), reverse=True)


def generate_build_matrix(already_published, all_tags):
    not_published = [t for t in all_tags if t not in already_published]
    latest = all_tags[0]
    to_publish = []
    for tag in not_published:
        image_tag = f"{DOCKER_NAMESPACE}/{DOCKER_IMAGE}:{tag}"
        if tag == latest:
            # Github doesn't allow newline so we encode it
            image_tag += f"%0A{DOCKER_NAMESPACE}/{DOCKER_IMAGE}:latest"
        to_publish.append(image_tag)
    return f"TAGS=\"{json.dumps(to_publish)}\""


def main():
    already_published = get_published_image_tags()
    all_tags = get_repo_tags()
    build_matrix = generate_build_matrix(already_published, all_tags)
    print(build_matrix)


if __name__ == "__main__":
    main()

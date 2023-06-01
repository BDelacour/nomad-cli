import json
import os
import re
from functools import cmp_to_key

import requests
import semver

DOCKER_NAMESPACE = os.getenv("DOCKER_NAMESPACE")
assert DOCKER_NAMESPACE is not None
DOCKER_IMAGE = os.getenv("DOCKER_IMAGE")
assert DOCKER_IMAGE is not None

MATRIX_LIMIT = 256


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
    distrib_tagsuffix = {
        "alpine:3.17": "alpine-3.17",
        "alpine:3.18": "alpine-3.18",
        "debian:buster": "buster",
        "debian:bullseye": "bullseye",
        "debian:buster-slim": "buster-slim",
        "debian:bullseye-slim": "bullseye-slim"
    }
    shortened_tag_selected = {
        "latest": False,
        "alpine-3.17": False,
        "alpine-3.18": False,
        "buster": False,
        "bullseye": False,
        "buster-slim": False,
        "bullseye-slim": False
    }
    includes = []
    for tag in all_tags:
        for distrib, suffix in distrib_tagsuffix.items():
            suffixed_tag = f"{tag}-{suffix}"

            include = {
                "tags": suffixed_tag,
                "version": tag,
                "base_image": distrib
            }
            for st in shortened_tag_selected.keys():
                if (st == suffix or st == "latest" and suffix == "bullseye") and shortened_tag_selected[st] == False:
                    shortened_tag_selected[st] = True
                    include[st.replace("-", "").replace(".", "-")] = "true"
            if suffixed_tag not in already_published and len(includes) < MATRIX_LIMIT:
                includes.append(include)
    matrix = {
        "tags": list(map(lambda i: i["tags"], includes)),
        "include": includes
    }
    return f"MATRIX={json.dumps(matrix)}"


def main():
    already_published = get_published_image_tags()
    all_tags = get_repo_tags()
    build_matrix = generate_build_matrix(already_published, all_tags)
    print(build_matrix)


if __name__ == "__main__":
    main()

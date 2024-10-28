CURRENT_VERSION := $(shell poetry version -s)
SEMVERS := major minor patch
LAST_TAG := $(shell git describe --tags --abbrev=0)

tag_version:
	git commit -m "release: bump to ${CURRENT_VERSION}" pyproject.toml
	git tag ${CURRENT_VERSION}

$(SEMVERS):
	poetry version $@
	$(MAKE) tag_version

release:
	git push origin tag ${LAST_TAG}
	gh release create --verify-tag ${LAST_TAG} --notes-from-tag

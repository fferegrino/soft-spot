POETRY=poetry
POETRY_RUN=$(POETRY) run

SOURCE_FILES=$(shell find . -name '*.py' -not -path **/.venv/*)
SOURCES_FOLDER=soft_spot

BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
HASH := $(shell git rev-parse HEAD)
TAG := $(shell git tag -l --contains HEAD)

init:
	$(POETRY) config repositories.testpypi https://test.pypi.org/simple

format:
	$(POETRY_RUN) isort -rc $(SOURCES_FOLDER)
	$(POETRY_RUN) black $(SOURCE_FILES)

lint:
	$(POETRY_RUN) bandit -r $(SOURCES_FOLDER)
	$(POETRY_RUN) isort -rc $(SOURCES_FOLDER) --check-only
	$(POETRY_RUN) black $(SOURCE_FILES) --check
	$(POETRY_RUN) pylint $(SOURCES_FOLDER)

check_on_master:
ifeq ($(BRANCH),master)
	echo "You are good to go!"
else
	$(error You are not in the master branch)
endif

patch: check_on_master
	$(POETRY_RUN) bumpversion patch --verbose
	git push --follow-tags

minor: check_on_master
	$(POETRY_RUN) bumpversion minor --verbose
	git push --follow-tags

major: check_on_master
	$(POETRY_RUN) bumpversion major --verbose
	git push --follow-tags

build:
	$(POETRY) build

testpypi: build
	$(POETRY) publish -r testpypi

publish: build
ifeq ($(TAG),)
	@echo "Skipping PyPi publishing"
else
	$(POETRY) publish -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD}
endif


MAKEFILES:=$(shell find . -mindepth 2 -name "Makefile")


.PHONY: update

all: build

build: $(MAKEFILES)
	FAILED_MAKEFILES=""; \
	for MAKEFILE in $(MAKEFILES); do \
		$(MAKE) -C $$(dirname $${MAKEFILE}); \
		if [[ $$? -ne 0 ]]; then FAILED_MAKEFILES+="$${MAKEFILE} "; fi; \
	done; \
	if [[ ! -z "$${FAILED_MAKEFILES}" ]]; then \
		echo "Failed:"; \
		for FAILED_MAKEFILE in $${FAILED_MAKEFILES}; do \
			echo $${FAILED_MAKEFILE}; \
		done; \
		exit 1; \
	fi

push: $(MAKEFILES)
	FAILED_MAKEFILES=""; \
	for MAKEFILE in $(MAKEFILES); do \
		$(MAKE) -C $$(dirname $${MAKEFILE}) push; \
		if [[ $$? -ne 0 ]]; then FAILED_MAKEFILES+="$${MAKEFILE} "; fi; \
	done; \
	if [[ ! -z "$${FAILED_MAKEFILES}" ]]; then \
		echo "Failed:"; \
		for FAILED_MAKEFILE in $${FAILED_MAKEFILES}; do \
			echo $${FAILED_MAKEFILE}; \
		done; \
		exit 1; \
	fi

update:
	python2 update.py


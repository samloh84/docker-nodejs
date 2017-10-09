REPOSITORY_NAME := samloh84/nodejs
TAGS := 4.8.4 4.8.4-alpine3.6
CONTAINER_NAME := $(shell echo $(REPOSITORY_NAME) | sed -e 's/[^a-zA-Z0-9_.-]/-/g')

.PHONY: all clean build push bash sudo run exec rm rmi
.IGNORE: sudo run rm rmi

build:
	set -x && \
	DOCKER_BUILD_ARGS="$${DOCKER_BUILD_ARGS} " && \
	for TAG in $(TAGS); do DOCKER_BUILD_ARGS+="-t $(REPOSITORY_NAME):$${TAG} "; done && \
	sudo docker build $${DOCKER_BUILD_ARGS} .

push:
	set -x && \
	for TAG in $(TAGS); do sudo docker push $(REPOSITORY_NAME):$${TAG}; done;

run:
	set -x && \
	DOCKER_RUN_ARGS="$${DOCKER_RUN_ARGS} " && \
	DOCKER_RUN_ARGS+="--tty " && \
	DOCKER_RUN_ARGS+="--interactive " && \
	DOCKER_RUN_ARGS+="--rm " && \
	DOCKER_RUN_ARGS+="--name $(CONTAINER_NAME) " && \
	for TAG in $(TAGS); do IMAGE_NAME="$(REPOSITORY_NAME):$${TAG} "; break; done && \
	sudo docker run $${DOCKER_RUN_ARGS} $${IMAGE_NAME}

ash:
	set -x && \
	DOCKER_RUN_ARGS="$${DOCKER_RUN_ARGS} " && \
	DOCKER_RUN_ARGS+="--tty " && \
	DOCKER_RUN_ARGS+="--interactive " && \
	DOCKER_RUN_ARGS+="--rm " && \
	DOCKER_RUN_ARGS+="--name $(CONTAINER_NAME) " && \
	for TAG in $(TAGS); do IMAGE_NAME="$(REPOSITORY_NAME):$${TAG} "; break; done && \
	sudo docker run $${DOCKER_RUN_ARGS} $${IMAGE_NAME} ash

sudo:
	set -x && \
	DOCKER_RUN_ARGS="$${DOCKER_RUN_ARGS} "; \
	DOCKER_RUN_ARGS+="--tty "; \
	DOCKER_RUN_ARGS+="--interactive "; \
	DOCKER_RUN_ARGS+="--rm "; \
	DOCKER_RUN_ARGS+="--name $(CONTAINER_NAME) "; \
	DOCKER_RUN_ARGS+="--user 0 "; \
	DOCKER_RUN_ARGS+="--privileged "; \
	for TAG in $(TAGS); do IMAGE_NAME="$(REPOSITORY_NAME):$${TAG} "; break; done; \
	sudo docker run $${DOCKER_RUN_ARGS} $${IMAGE_NAME} ash

rm:
	set -x && \
	DOCKER_RM_ARGS="$${DOCKER_RM_ARGS} --force "; \
	sudo docker rm $${DOCKER_RM_ARGS} $(CONTAINER_NAME)

rmi:
	set -x && \
	DOCKER_RMI_ARGS="$${DOCKER_RMI_ARGS} --force "; \
	for TAG in $(TAGS); do IMAGE_NAMES="$(REPOSITORY_NAME):$${TAG} "; done; \
	sudo docker rmi $${DOCKER_RMI_ARGS} $${IMAGE_NAMES}

save:
	set -x && \
	for ORIGINAL_TAG in $(TAGS); do break; done && \
	ORIGINAL_IMAGE_NAME="$(REPOSITORY_NAME):$${ORIGINAL_TAG}" && \
	if [[ -z "$${IMAGE_NAME}" ]]; then \
	TAG="$${TAG:-$${ORIGINAL_TAG}}" && \
	IMAGE_NAME="$(REPOSITORY_NAME):$${TAG}"; \
	fi && \
	ARCHIVE_NAME="$$(echo $${IMAGE_NAME} | sed -e 's/[^a-zA-Z0-9_.-]\+/_/g').tar.gz" && \
	echo -e "#!/bin/bash -e\necho Importing $${IMAGE_NAME}\nARCHIVE=\$$(awk '/^__ARCHIVE_MARKER__/ { print NR + 1; exit 0; }' \$$0)\ntail -n+\$$ARCHIVE \$$0 | docker import -\ndocker push $${IMAGE_NAME}\nexit 0\n__ARCHIVE_MARKER__" > $${ARCHIVE_NAME}
	sudo docker tag $${ORIGINAL_IMAGE_NAME} $${IMAGE_NAME} && \
	sudo docker save $${IMAGE_NAME} | gzip -9 >> $${ARCHIVE_NAME}


clean: rm rmi

all: build push
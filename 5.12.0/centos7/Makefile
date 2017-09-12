REPOSITORY_NAME := samloh84/nodejs
TAGS := 5.12.0 5.12.0-centos7
CONTAINER_NAME := $(shell echo $(REPOSITORY_NAME) | sed -e 's/[^a-zA-Z0-9_.-]/-/g')

.PHONY: all clean build push bash sudo run exec rm rmi
.IGNORE: sudo run rm rmi

build:
	set -x; \
	DOCKER_BUILD_ARGS=""; \
	for TAG in $(TAGS); do DOCKER_BUILD_ARGS+="-t $(REPOSITORY_NAME):$${TAG} "; done; \
	sudo docker build $${DOCKER_BUILD_ARGS} .

push:
	set -x; \
	for TAG in $(TAGS); do sudo docker push $(REPOSITORY_NAME):$${TAG}; done;

run:
	set -x; \
	DOCKER_RUN_ARGS=""; \
	DOCKER_RUN_ARGS+="--tty "; \
	DOCKER_RUN_ARGS+="--interactive "; \
	DOCKER_RUN_ARGS+="--rm "; \
	DOCKER_RUN_ARGS+="--name $(CONTAINER_NAME) "; \
	for TAG in $(TAGS); do IMAGE_NAME="$(REPOSITORY_NAME):$${TAG} "; break; done; \
	sudo docker run $${DOCKER_RUN_ARGS} $${IMAGE_NAME}

bash:
	set -x; \
	DOCKER_RUN_ARGS=""; \
	DOCKER_RUN_ARGS+="--tty "; \
	DOCKER_RUN_ARGS+="--interactive "; \
	DOCKER_RUN_ARGS+="--rm "; \
	DOCKER_RUN_ARGS+="--name $(CONTAINER_NAME) "; \
	for TAG in $(TAGS); do IMAGE_NAME="$(REPOSITORY_NAME):$${TAG} "; break; done; \
	sudo docker run $${DOCKER_RUN_ARGS} $${IMAGE_NAME} bash

sudo:
	set -x; \
	DOCKER_RUN_ARGS=""; \
	DOCKER_RUN_ARGS+="--tty "; \
	DOCKER_RUN_ARGS+="--interactive "; \
	DOCKER_RUN_ARGS+="--rm "; \
	DOCKER_RUN_ARGS+="--name $(CONTAINER_NAME) "; \
	DOCKER_RUN_ARGS+="--user 0 "; \
	DOCKER_RUN_ARGS+="--privileged "; \
	for TAG in $(TAGS); do IMAGE_NAME="$(REPOSITORY_NAME):$${TAG} "; break; done; \
	sudo docker run $${DOCKER_RUN_ARGS} $${IMAGE_NAME} bash

rm:
	set -x; \
	DOCKER_RM_ARGS="--force "; \
	sudo docker rm $${DOCKER_RM_ARGS} $(CONTAINER_NAME)

rmi:
	set -x; \
	DOCKER_RMI_ARGS="--force "; \
	for TAG in $(TAGS); do IMAGE_NAMES="$(REPOSITORY_NAME):$${TAG} "; done; \
	sudo docker rmi $${DOCKER_RMI_ARGS} $${IMAGE_NAMES}

save:
	set -x; \
	for TAG in $(TAGS); do IMAGE_NAME="$(REPOSITORY_NAME):$${TAG}"; \
	ARCHIVE_NAME=$$(echo "$(REPOSITORY_NAME).$${TAG}.tar.gz" | sed -e 's/[^a-zA-Z0-9_.-]/-/g'); \
	break; done; \
	sudo docker save $${IMAGE_NAME} | gzip -9 > $${ARCHIVE_NAME}

clean: rm rmi

all: build push
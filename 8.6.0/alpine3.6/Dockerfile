FROM samloh84/alpine:3.6

ARG PRODUCT=nodejs
ARG PRODUCT_VERSION=8.6.0
ARG TEMP_DIR_ROOT=/tmp/${PRODUCT}
ARG TEMP_DIR=/${TEMP_DIR_ROOT}/${PRODUCT_VERSION}
ARG INSTALL_DIR_ROOT=/opt/${PRODUCT}
ARG INSTALL_DIR=${INSTALL_DIR_ROOT}/${PRODUCT_VERSION}

ARG NODEJS_SOURCE_URL="https://nodejs.org/dist/v8.6.0/node-v8.6.0.tar.xz"
ARG NODEJS_SOURCE="node-v8.6.0.tar.xz"

ARG NODEJS_GPG_KEYS="94AE36675C464D64BAFA68DD7434390BDBE9B9C5 B9AE9905FFD7803F25714661B63B535A4C206CA9 56730D5401028683275BD23C23EFEFE93C4CFFFE 71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 FD3A5288F042B6850C66B31F09FE44734EB7990E C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 DD8F2338BAE7501E3DD5AC78C273792F7D83545D"
ARG NODEJS_CHECKSUMS_URL="https://nodejs.org/dist/v8.6.0/SHASUMS256.txt.asc"
ARG NODEJS_CHECKSUMS="SHASUMS256.txt.asc"

USER ${ROOT_UID}

RUN \
mkdir -p ${TEMP_DIR} ${INSTALL_DIR} && \
cd ${TEMP_DIR} && \
curl -LjSs ${NODEJS_CHECKSUMS_URL} -o ${NODEJS_CHECKSUMS} && \
for GPG_KEY in ${NODEJS_GPG_KEYS}; do \
gpg --keyserver pgp.mit.edu --recv-keys ${GPG_KEY} || \
gpg --keyserver keyserver.pgp.com --recv-keys ${GPG_KEY} || \
gpg --keyserver ha.pool.sks-keyservers.net --recv-keys ${GPG_KEY} ; \
done && \
curl -LjSs ${NODEJS_CHECKSUMS_URL} -o ${NODEJS_CHECKSUMS} && \
gpg --verify ${NODEJS_CHECKSUMS} && \
apk-install libstdc++ && \
NODEJS_COMPILE_DEPENDENCIES="python gcc g++ make linux-headers zlib-dev openssl-dev readline-dev bzip2-dev xz-dev gdbm-dev tk-dev sqlite-dev" && \
apk-install ${NODEJS_COMPILE_DEPENDENCIES} && \
curl -LjSs ${NODEJS_SOURCE_URL} -o ${NODEJS_SOURCE} && \
grep ${NODEJS_SOURCE} ${NODEJS_CHECKSUMS} | sha256sum -c - && \
mkdir -p ${TEMP_DIR}/build && \
tar -xf ${NODEJS_SOURCE} --strip-components=1 -C ${TEMP_DIR}/build && \
cd ${TEMP_DIR}/build && \
./configure --prefix=${INSTALL_DIR} && \
make && \
make install && \
apk del -y ${NODEJS_COMPILE_DEPENDENCIES} && \
rm -rf /var/cache/apk/* && \
cd ${INSTALL_DIR} && \
PATH=${PATH}:${INSTALL_DIR}/bin ${INSTALL_DIR}/bin/npm install npm@latest -g && \
fix-ownership ${INSTALL_DIR} && \
fix-permissions ${INSTALL_DIR} && \
rm -rf ${TEMP_DIR_ROOT}

ENV NODEJS_HOME ${INSTALL_DIR}
ENV PATH ${NODEJS_HOME}/bin:${PATH}

USER ${APP_UID}
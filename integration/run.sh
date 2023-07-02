#!/usr/bin/env bash

if [[ -z "${GITHUB_ACTIONS}" ]]; then
  cd "$(dirname "$0")"
fi

if [ "${LOCAL_IMAGE_NAME}" == "" ]; then 
    docker build -t ${LOCAL_IMAGE_NAME} ..
else
    echo "no need to build image ${LOCAL_IMAGE_NAME}"
fi

docker run -p 5000:5000 ${LOCAL_IMAGE_NAME} 

sleep 10

pipenv run python test_docker.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker logs ${LOCAL_IMAGE_NAME} 
    docker-compose down
    exit ${ERROR_CODE}
fi

docker stop ${LOCAL_IMAGE_NAME}

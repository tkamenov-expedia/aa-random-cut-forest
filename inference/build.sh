#!/usr/bin/env bash

# Copyright 2018 Expedia Group, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

APP_NAME="rcf-inference"
HOST_PORT=8080
GUEST_PORT=8080

cd `cd -P -- "$(dirname -- "$0")" && pwd -P`

show_help() {
cat << EOF
Usage: ${0##*/} [-h] [-p] [-b] [-r] [--release]

    -h, --help      display this help and exit.
    -b, --build     docker build.
    -r, --run       run docker image.
    --release       release docker image
EOF
}

do_build() {
    echo 'Building image...'
    docker build ./src -f docker/Dockerfile -t $APP_NAME
}

do_run() {
    echo "Running $APP_NAME"
    echo "HOST_PORT  : $HOST_PORT"
    echo "GUEST_PORT : $GUEST_PORT"

    docker run $(pwd)/local_test/test_dir:/opt/ml -p $HOST_PORT:$GUEST_PORT  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN  --rm $APP_NAME serve
}

do_release() {
    echo 'Releasing...'
    export DOCKER_ORG="expediadotcom"
    export DOCKER_IMAGE_NAME=$APP_NAME
    #../scripts/publish-to-docker-hub.sh
}

while :; do
    case $1 in
        -h|-\?|--help)
            show_help
            exit
            ;;
        -b|--build)
            do_build
            break
            ;;
        -r|--run)
            do_run
            break
            ;;
        --release)
            do_release
            break
            ;;
        --)              # End of all options.
            shift
            break
            ;;
        -?*)
            printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
            ;;
        *)               # Default case
            show_help
            exit
            ;;
    esac

    shift
done

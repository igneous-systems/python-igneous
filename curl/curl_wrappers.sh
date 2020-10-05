#!/usr/bin/env bash
IGNEOUS_API_VERSION=v1

function igget() {
  IGGET_USAGE="\n\nUSAGE:\n\tigget ENDPOINT [CURL_ARGS]"
  [ -z "$IGNEOUS_API_KEY" ] && echo "Environment variable IGNEOUS_API_KEY must be set to the Igneous API key" && return 1
  [ -z "$IGNEOUS_API_SERVER" ] && echo "Environment variable IGNEOUS_API_SERVER must be set to the Igneous API server" && return 2
  ENDPOINT=$1
  [ -z "$ENDPOINT" ] && echo -e "Endpoint missing.$IGGET_USAGE" && return 3
  shift
  CURL_ARGS=$*
  ENDPOINT=$IGNEOUS_API_SERVER/x/igneous/IGNEOUS_API_VERSION/$ENDPOINT
  curl --header "Content: application/json" --header "Authorization: $IGNEOUS_API_KEY" $ENDPOINT $CURL_ARGS
}

function igpost() {
  IGPOST_USAGE="\n\nUSAGE:\n\tigpost ENDPOINT PAYLOAD_FILE [CURL_ARGS]"
  [ -z "$IGNEOUS_API_KEY" ] && echo "Environment variable IGNEOUS_API_KEY must be set to the Igneous API key" && return 1
  [ -z "$IGNEOUS_API_SERVER" ] && echo "Environment variable IGNEOUS_API_SERVER must be set to the Igneous API server" && return 2
  ENDPOINT=$1
  [ -z "$ENDPOINT" ] && echo -e "Endpoint missing.$IGPOST_USAGE" && return 3
  shift
  PAYLOAD=$1
  [ -z "$PAYLOAD" ] && echo -e "Payload file missing.$IGPOST_USAGE" && return 4
  shift
  CURL_ARGS=$*
  ENDPOINT=$IGNEOUS_API_SERVER/x/igneous/$IGNEOUS_API_VERSION/$ENDPOINT
  curl --header "Content: application/json" --header "Authorization: $IGNEOUS_API_KEY" -X POST $ENDPOINT -d @$PAYLOAD $CURL_ARGS
}

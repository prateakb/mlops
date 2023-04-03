#!/bin/bash
# format should be 
# curl -XPOST <your cf url> = "Authorization: Bearer $(gcloud auth print-identity-token)" -H "Content-Type:application/json" -d '<your data as json>'

source configurations.env && \
curl -XPOST ${CLOUD_FUNCTION_URL} -H "Authorization: Bearer $(gcloud auth print-identity-token)" -H "Content-Type:application/json" -d @model/sample_payload.json
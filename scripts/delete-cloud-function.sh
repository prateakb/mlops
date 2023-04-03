#!/bin/bash
gcloud functions delete $(cat PIPELINE_NAME) --region=us-east1 --gen2 --quiet
#!/bin/bash

set -e

# Run 'az devops login' to enable 'az pipelines' commands
echo $ACCESS_TOKEN | az devops login

run_output=$(az pipelines run --org "$ORG_URI" -p "$TEAM_PROJECT" --name "$PIPELINE_NAME" --branch "$BRANCH")
triggered_pipeline_build_number=$(echo $run_output | jq -r '.buildNumber')
triggered_pipeline_build_id=$(echo $run_output | jq -r '.id')
triggered_pipeline_id=$(echo $run_output | jq -r '.definition.id')
echo ">>> DevOps Pipeline '$PIPELINE_NAME' with build number '#$triggered_pipeline_build_number' has been triggered!"

if [[ $triggered_pipeline_build_number ]]; then
  status=$(echo $run_output | jq -r '.status')

  while [ "$status" != "inProgress" ]
  do
    echo "Pipeline has not started yet, current status is: $status"
    sleep 10
    run_output=$(az pipelines runs show --org "$ORG_URI" -p "$TEAM_PROJECT" --id $triggered_pipeline_build_id)
    status=$(echo $run_output | jq -r '.status')
  done
  echo ">>> Trigger pipeline has started!"

  # Wait trained_model_name exported by target triggered pipeline
  trained_model_name=$(az pipelines variable list --org "$ORG_URI" -p "$TEAM_PROJECT" --pipeline-name "$PIPELINE_NAME" | jq -r --arg VAR_NAME "MODEL_NAME_$triggered_pipeline_build_number" '."\($VAR_NAME)".value // ""')
  trained_model_zip_contents_md5=$(az pipelines variable list --org "$ORG_URI" -p "$TEAM_PROJECT" --pipeline-name "$PIPELINE_NAME" | jq -r --arg VAR_NAME "MODEL_ZIP_CONTENTS_MD5_$triggered_pipeline_build_number" '."\($VAR_NAME)".value // ""')
  triggered_pipeline_run_result=$(az pipelines runs show --org "$ORG_URI" -p "$TEAM_PROJECT" --id $triggered_pipeline_build_id | jq -r '.result')

  while [[ (-z "$trained_model_name" || -z "$trained_model_zip_contents_md5") && "$triggered_pipeline_run_result" != "failed" && "$triggered_pipeline_run_result" != "canceled" ]]
  do
    echo "Triggered pipeline is still running..."
    sleep 60
    trained_model_name=$(az pipelines variable list --org "$ORG_URI" -p "$TEAM_PROJECT" --pipeline-name "$PIPELINE_NAME" | jq -r --arg VAR_NAME "MODEL_NAME_$triggered_pipeline_build_number" '."\($VAR_NAME)".value // ""')
    trained_model_zip_contents_md5=$(az pipelines variable list --org "$ORG_URI" -p "$TEAM_PROJECT" --pipeline-name "$PIPELINE_NAME" | jq -r --arg VAR_NAME "MODEL_ZIP_CONTENTS_MD5_$triggered_pipeline_build_number" '."\($VAR_NAME)".value // ""')
    triggered_pipeline_run_result=$(az pipelines runs show --org "$ORG_URI" -p "$TEAM_PROJECT" --id $triggered_pipeline_build_id | jq -r '.result')
  done
  echo ">>> Pipeline stage of uploading model to blob storage has completed!"

  # Set output variable for next stage/job
  echo "##vso[task.setvariable variable=modelNameUploadedToBlobStorage;isOutput=true]$trained_model_name"
  echo "##vso[task.setvariable variable=modelZIPContentsMD5;isOutput=true]$trained_model_zip_contents_md5"

  # Delete temp pipeline variable
  az pipelines variable delete --org "$ORG_URI" -p "$TEAM_PROJECT" --pipeline-name "$PIPELINE_NAME" --pipeline-id $triggered_pipeline_id --name MODEL_NAME_$triggered_pipeline_build_number --yes
  az pipelines variable delete --org "$ORG_URI" -p "$TEAM_PROJECT" --pipeline-name "$PIPELINE_NAME" --pipeline-id $triggered_pipeline_id --name MODEL_ZIP_CONTENTS_MD5_$triggered_pipeline_build_number --yes
fi

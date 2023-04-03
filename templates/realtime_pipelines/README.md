# What this code does
This code will enable an MLOPS person to take a DS code, structure it as shown in the `dummy_ds_code.py` file, modify the `main.py` file and then deploy the DS model code as a realtime service to google cloud function


### How to use this Repository
Step 1: type `make configure` and enter the pipeline name (give a meaningful name). You should see output like below:

```
(base) jupyter@acs-bi-survival:~/mlops-framework/realtime_pipelines$ make configure
scripts/configure.sh
What is the name of the pipeline run? {eg. sparse person}pratiktest
pipeline name is pratiktest
your code has been configured. Please go to the folder pratiktest
then modify the files
    - pratiktest/main.py
    - pratiktest/dummydscode.py
    - pratiktest/requirements.txt
Once done with modifying correctly, type make deploy to deploy
```

Step 2: A folder with the name you specified in step1 will be created. Go to that folder and modify main.py, requirements.txt and the dummydscode.py to suit the pipeline needs.

Step 3: type `make deploy`. If everything goes right, you should see an output similiar to below:

```
deploying a cloud function called pratik_realtime_template
Deploying function (may take a while - up to 2 minutes)...⠹                                                         
For Cloud Build Logs, visit: https://console.cloud.google.com/cloud-build/builds;region=us-central1/7b835e3e-a1a4-4dac-bc3f-741e417a9c78?project=697878854467
Deploying function (may take a while - up to 2 minutes)...⠛                
```

Step 4: write the payload you are expecting in a `json` format in the file `model/sample_payload.json`

Step 5: test the pipeline using the command `bash test-cloud-functions.sh`. If your pipeline is successful, you will see a response to the payload you sent. eg.

```
(base) jupyter@acs-bi-survival:~/mlops-framework/realtime_pipelines$ bash scripts/test-cloud-function.sh && echo "\n"{"predictions": [0.7813820242881775]}
```

if this was a test run and the cloud function deployed doesn't need to exist beyond the current session, type `make cleanup` this will delete the cloud function deployment. 
**NOTE: DO NOT DO THIS ON DEPLOYED CUSTOMER MODELS**

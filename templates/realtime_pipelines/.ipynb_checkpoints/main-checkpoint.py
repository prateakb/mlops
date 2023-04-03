from flask import escape, abort, jsonify
import functions_framework

import pandas as pd
import json
from dummydscode import preprocess, predict_realtime, load_model

model = load_model()

@functions_framework.http
def <<pipeline_name>>(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'payload' in request_json:
        payload = request_json['payload']
        df = pd.DataFrame.from_dict(payload)
        return json.dumps({"predictions": predict_realtime(preprocess(df), model).tolist()})

    else:
        error_message = {"error_message": "either payload is missing or not structured properly"}
        return abort(400, jsonify(error_message ))
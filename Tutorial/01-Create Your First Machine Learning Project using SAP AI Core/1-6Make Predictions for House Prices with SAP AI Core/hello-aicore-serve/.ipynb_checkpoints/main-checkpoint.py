import os
import pickle
import numpy as np
from flask import Flask
from flask import request as call_request

# Creates Flask serving engine
app = Flask(__name__)

model = None

@app.before_first_request
def init():
    """
    Load model else crash, deployment will not start
    """
    global model
    model = pickle.load(open ('/mnt/models/model.pkl','rb')) # All the model files will be read from /mnt/models
    return None

@app.route("/v2/greet", methods=["GET"])
def status():
    global model
    if model is None:
        return "Flask Code: Model was not loaded."
    else:
        return "Model is loaded."

# You may customize the endpoint, but must have the prefix `/v<number>`
@app.route("/v2/predict", methods=["POST"])
def predict():
    """
    Perform an inference on the model created in initialize

    Returns:
        String value price.
    """
    global model
    #
    query = dict(call_request.json)
    input_features = [ # list of values from request call
        query['MedInc'],
        query['HouseAge'],
        query['AveRooms'],
        query['AveBedrms'],
        query['Population'],
        query['AveOccup'],
        query['Latitude'],
        query['Longitude'],
    ]
    # Prediction
    prediction = model.predict(
        np.array([list(map(float, input_features)),]) # (trailing comma) <,> to make batch with 1 observation
    )
    output = str(prediction)
    # Response
    return output

if __name__ == "__main__":
    print("Serving Initializing")
    init()
    print(f'{os.environ["greetingmessage"]}')
    print("Serving Started")
    app.run(host="0.0.0.0", debug=True, port=9001)

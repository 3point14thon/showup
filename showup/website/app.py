from flask import Flask, request, render_template, jsonify
import numpy as np
import pandas as pd
import dill
from ..pipeline.meetup_pipes import (FeatureSelector, MapFeature,
                                     CustomBinarizer, FillWith, RFRWrapper)
from ..pipeline.meetup_pipeline import random_forest_model, meetup_union, visibility

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/submit", methods=["POST"])
def submit():
    '''Retrieves prediction then returns in json format'''
    user_data = pd.DataFrame(request.json, index=[0])
    prediction = predict(user_data)
    return jsonify({'prediction': prediction})

def predict(text_input):
    '''Returns predicted event turn out range for text_input'''
    X = text_input
    with open('showup/website/static/model.pkl', 'rb') as f:
        model = dill.load(f)
    trees = model.named_steps['model'].estimators_
    predictions = np.zeros(len(trees))
    for i, tree in enumerate(trees):
        predictions[i] += (tree.predict(model.named_steps['meetup_features'].transform(X)))
    lower_bound, upper_bound = get_bounds(predictions)
    return str(lower_bound) + ' - ' + str(upper_bound)

def get_bounds(predictions, lower_percentile = 0.25, upper_percentile = 0.75):
    '''Gets first and third quartile indicies'''
    lower_bound = np.sort(predictions)[int(len(predictions)*lower_percentile)]
    lower_bound = int(round(np.expm1(lower_bound)))
    upper_bound = np.sort(predictions)[int(len(predictions)*upper_percentile)]
    upper_bound = int(round(np.expm1(upper_bound)))
    return lower_bound, upper_bound

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)

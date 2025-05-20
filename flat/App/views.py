from django.shortcuts import render, redirect
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
import pickle
import pandas as pd
from .models import Flat
import os
from django.conf import settings
from catboost import CatBoostRegressor


# Create your views here.

def create_X(total_area, living_area, floor, built_year, address, scaler_path, encoder_path):
    scaler = None
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)

    encoder = None
    with open(encoder_path, 'rb') as f:
        encoder = pickle.load(f)

    X = pd.DataFrame(
        {"total_area": [total_area],
         "living_area": [living_area],
         "floor": [floor],
         "built_year": [built_year],
         "address": [address]}
    )
    one_hot_df = pd.DataFrame(encoder.transform(X[["address"]]), columns=encoder.get_feature_names_out(), index=X.index)
    df_encoded = pd.concat([X, one_hot_df], axis=1)
    X = df_encoded.drop("address", axis=1)

    X = pd.DataFrame(scaler.transform(X), columns=scaler.feature_names_in_, index=X.index)
    return X


def predict(X, model_path):
    model = None
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    predict = model.predict(X)
    normalize_predict = predict[0] * 1000000
    return normalize_predict


def show_base_page(request):
    return render(request, "App/base.html")


def show_predictions_page(request):
    districts = Flat.CHOICES_DISTRICT

    if request.method == 'POST':
        total_area = float(request.POST.get('total_area'))
        living_area = float(request.POST.get('living_area'))
        floor = int(request.POST.get('floor'))
        built_year = int(request.POST.get('built_year'))
        address = request.POST.get('district')

        scaler_path = 'App/all_models/scaler.pkl'
        encoder_path = 'App/all_models/encoder.pkl'
        model_path = 'App/all_models/baseline.pkl'

        X = create_X(total_area, living_area, floor, built_year, address, scaler_path, encoder_path)
        prediction = predict(X, model_path)

        return render(request, "App/predictions.html", {
            'districts': districts,
            'prediction': prediction,
            'form_data': request.POST
        })

    return render(request, "App/predictions.html", {'districts': districts})

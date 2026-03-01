import pandas as pd
import pickle
import csv
import sys
import json
from functions import criteria_to_series, parse_ad, parse_ads, filter_ads_data
import xgboost as xgb
import sklearn
pd.options.mode.chained_assignment = None

def predict_from_csv(path):
    max_int = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_int)
            break
        except OverflowError:
            max_int = int(max_int / 10)

    try:
        test_ad = pd.read_csv(path, engine='python')
    except FileNotFoundError:
        return {'yandex_verdict' : 'error reading file'}
    test_ad_modified = test_ad[['desired_criteria',
           'service_change',
           'matched_orders_count',
           'inspected_cars_count',
           'recommended_cars_count',
           'offers_count',
           'ads_market_count',
           'market_saturation_coefficient',
           'region',
           'ads_data']]
    test_ad_modified[['brand', 'model', 'year', 'generation', 'mileage',
                      'budget', 'max_owners', 'min_volume', 'max_volume',
                      'trasmission', 'engine_type', 'body_type', 'wheel_drive', 'color',
                      'complectation', 'comment']]\
        = test_ad_modified['desired_criteria'].apply(criteria_to_series)

    test_ad_modified['ads_data'] = test_ad_modified['ads_data'].apply(parse_ad)
    mistakes = 0
    test_ad_modified['ads_data'] = test_ad_modified.apply(lambda row:
                                                      filter_ads_data(row['desired_criteria'], row['ads_data']), axis=1)
    test_ad_modified[['median_year',
                    'median_km_age',
                    'median_price',
                    'median_owners']] = test_ad_modified['ads_data'].apply(parse_ads)
    test_ad_modified['ads_count'] = test_ad_modified['ads_data'].apply(len)
    cleared_test_ad = test_ad_modified[['service_change', 'matched_orders_count', 'inspected_cars_count',
           'recommended_cars_count', 'market_saturation_coefficient', 'region',
           'brand', 'model', 'year', 'generation',
           'mileage', 'budget', 'max_owners', 'median_year',
           'median_km_age', 'median_price', 'median_owners', 'ads_count']]
    changed_test_ad = cleared_test_ad[['matched_orders_count', 'inspected_cars_count',
       'recommended_cars_count', 'market_saturation_coefficient', 'region',
       'brand', 'year', 'generation',
       'mileage', 'budget', 'max_owners',
       'ads_count']]
    changed_test_ad['generation'] = cleared_test_ad['model'] + " " + cleared_test_ad['generation']
    changed_test_ad['median_year'] = cleared_test_ad['year'] - cleared_test_ad['median_year']
    changed_test_ad['median_price'] = cleared_test_ad['budget'] - cleared_test_ad['median_price']
    changed_test_ad['median_km_age'] = cleared_test_ad['mileage'] - cleared_test_ad['median_km_age']
    changed_test_ad['median_owners'] = cleared_test_ad['max_owners'] - cleared_test_ad['median_owners']
    changed_test_ad['good_ads_prob_count'] = (changed_test_ad['recommended_cars_count'] /
                                           changed_test_ad['inspected_cars_count'] *
                                           changed_test_ad['ads_count'])
    changed_test_ad['year'] = changed_test_ad['year'].astype('Int64').astype(str)
    ohe_columns = [
        'region',
        'brand',
        'year',
        'generation'
    ]
    changed_test_ad[ohe_columns] = changed_test_ad[ohe_columns].astype('category')

    with open('xgb_model_v2.pkl', 'rb') as f:
        loaded_model = pickle.load(f)

    answer = loaded_model.predict(changed_test_ad)
    answer_probability = loaded_model.predict_proba(changed_test_ad)[:, 1].item()
    answer_json = {'yandex_verdict' : 'no_answer'}
    if answer == 1:
        answer_json['yandex_verdict'] = 'approved'
        answer_json['yandex_probability'] = answer_probability
    else:
        answer_json['yandex_verdict'] = 'denied'
        answer_json['yandex_probability'] = answer_probability

    return answer_json

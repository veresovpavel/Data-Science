import datetime
import re
import numpy as np
import pandas as pd
import json


dict_body = pd.read_csv('Словари_Данных_Объявлений\dict_body_type_202512021406.csv', sep=",", engine='python')
dict_color = pd.read_csv('Словари_Данных_Объявлений\dict_color_202512021406.csv', sep=",", engine='python')
dict_condition = pd.read_csv('Словари_Данных_Объявлений\dict_condition_status_202512021409.csv', sep=",", engine='python')
dict_custom_status = pd.read_csv('Словари_Данных_Объявлений\dict_custom_status_202512021409.csv', sep=",", engine='python')
dict_drive_type = pd.read_csv('Словари_Данных_Объявлений\dict_drive_type_202512021409.csv', sep=",", engine='python')
dict_engine_type = pd.read_csv('Словари_Данных_Объявлений\dict_engine_type_202512021410.csv', sep=",", engine='python')
dict_generation = pd.read_csv('Словари_Данных_Объявлений\dict_generation_202512021410.csv', sep=",", engine='python')
dict_mark = pd.read_csv('Словари_Данных_Объявлений\dict_mark_202512021410.csv', sep=",", engine='python')
dict_model = pd.read_csv('Словари_Данных_Объявлений\dict_model_202512021410.csv', sep=",", engine='python')
dict_model_noramlized = pd.read_csv('Словари_Данных_Объявлений\dict_model_normalized_202512021410.csv', sep=",", engine='python')
dict_source = pd.read_csv('Словари_Данных_Объявлений\dict_source_202512021410.csv', sep=",", engine='python')
dict_transmission = pd.read_csv('Словари_Данных_Объявлений\dict_transmission_type_202512021410.csv', sep=",", engine='python')
dict_wheel_type = pd.read_csv('Словари_Данных_Объявлений\dict_wheel_type_202512021410.csv', sep=",", engine='python')
dict_transmission = dict_transmission.replace(['автомат', 'Автомат'], 'АКПП')
dict_body = dict_body.replace('пятидверный внедорожник', 'внедорожник 5 дв.')
dict_body = dict_body.replace('трехдверный внедорожник', 'внедорожник 3 дв.')
dict_body = dict_body.replace('пятидверный хэтчбэк', 'хэтчбек 5 дв.')
dict_body = dict_body.replace('трехдверный хэтчбэк', 'хэтчбек 3 дв.')

def parse_criteria(text):
    data = {'brand': 'Любая',
            'model': 'Любая',
            'year': np.nan,
            'generation': 'Nan',
            'mileage': 1000,
            'budget': np.nan,
            'max_owners': np.nan,
            'min_volume': np.nan,
            'max_volume': np.nan,
            'trasmission': 'Любая',
            'engine_type': 'Любой',
            'body_type': 'Любой',
            'wheel_drive': 'Любой',
            'color': 'Любой',
            'complectation': 'Любая',
            'comment': 'Любая'}
    parts = [part.strip() for part in text.split(';') if part.strip()]
    for part in parts:
        if part.lower().startswith('марка'):
            key = 'brand'
            data[key] = part[5:].strip()
        elif part.lower().startswith('модель'):
            key = 'model'
            data[key] = part[6:].strip()
        elif part.lower().startswith('год от'):
            key = 'year'
            data[key] = int(re.sub(r'год от\s*', '', part).strip())
        elif part.lower().startswith('поколение'):
            key = 'generation'
            data[key] = re.sub(r'поколение\s*', '', part).strip()
        elif part.lower().startswith('пробег до'):
            key = 'mileage'
            data[key] = int(re.search(r'пробег\s+до\s+(\d+)', part).group(1))
        elif part.lower().startswith('бюджет до'):
            key = 'budget'
            data[key] = int(re.search(r'бюджет\s+до\s+(\d+)', part).group(1))
        elif part.lower().startswith('владельцев до'):
            key = 'max_owners'
            data[key] = int(re.sub(r'владельцев до\s*', '', part).strip())
        elif part.lower().startswith('объем'):
            match = re.search(r'от\s*(\d+(?:\.\d+)?)\s*до\s*(\d+(?:\.\d+)?)', part)
            if match:
                key = 'min_volume'
                data[key] = float(match.group(1))  # 2.0 (или 2.5)
                key = 'max_volume'
                data[key] = float(match.group(2))  # 3.0 (или 3.7)
        elif part.lower().startswith('трансмиссия'):
            key = 'trasmission'
            text = re.sub(r'трансмиссия\s*', '', part).strip()
            data[key] = text[:text.find('\n')] if '\n' in text else text
        elif part.lower().startswith('двигатель'):
            key = 'engine_type'
            text = re.sub(r'двигатель\s*', '', part).strip()
            data[key] = text[:text.find('\n')] if '\n' in text else text
        elif part.lower().startswith('кузов'):
            key = 'body_type'
            text = re.sub(r'кузов\s*', '', part).strip().lower()
            data[key] = (text[:text.find('\n')] if '\n' in text else text).strip().strip(',')
        elif part.lower().startswith('привод'):
            key = 'wheel_drive'
            text = re.sub(r'привод\s*', '', part).strip()
            data[key] = text[:text.find('\n')] if '\n' in text else text
        elif part.lower().startswith('комплектация'):
            key = 'complectation'
            text = re.sub(r'комплектация\s*', '', part).strip()
            data[key] = text[:text.find('\n')] if '\n' in text else text
        elif part.lower().startswith('комментарий'):
            key = 'comment'
            data[key] = re.sub(r'комментарий\s*', '', part).strip()
        elif part.lower().startswith('цвет'):
            key = 'color'
            text = re.sub(r'цвет\s*', '', part).strip().lower()
            text = text.replace('черный', 'чёрный')
            text = text.replace('желтый', 'жёлтый')
            data[key] = text[:text.find('\n')] if '\n' in text else text
    if data['mileage'] == 1000:
        if datetime.now().year - 1 > data['year']:
            data['mileage'] = np.nan
    return data


def criteria_to_series(text):
    data = parse_criteria(text)
    return pd.Series(data)

def parse_ad(text):
    try:
        ads = json.loads(text)
    except json.JSONDecodeError:
        print(f"Json обрывается:\n {text[:150]}...")
        pos = text.rfind('"}')
        if pos != -1:
            text = text[:pos + 2] + ']'
        ads = json.loads(text)
    return ads


def parse_ads(data):
    global mistakes
    try:
        if len(data) == 0:
            ads_info = {
                'median_year': np.nan,
                'median_km_age': np.nan,
                'median_price': np.nan,
                'median_owners': np.nan
            }
        else:
            search_data = pd.DataFrame(data)
            search_data['price'] = pd.to_numeric(search_data['price'], errors='coerce')
            search_data['owners_count'] = pd.to_numeric(search_data['owners_count'], errors='coerce')
            ads_description = search_data.describe()
            ads_info = {
                'median_year': float(ads_description['year']['50%']),
                'median_km_age': float(ads_description['km_age']['50%']),
                'median_price': float(ads_description['price']['50%']),
                'median_owners': float(ads_description['owners_count']['50%']),
            }

    except:
        mistakes += 1
        ads_info = {
            'median_year': np.nan,
            'median_km_age': np.nan,
            'median_price': np.nan,
            'median_owners': np.nan
        }
    return pd.Series(ads_info)


def filter_ads_data(criteria, ads_data):
    criteries = parse_criteria(criteria)
    filtered = []
    global mistakes
    for ad in ads_data:
        try:
            if criteries['year'] == criteries['year']:
                if ad['year'] < criteries['year']:
#                     print('year', ad['year'], '| критерий:', criteries['year'])
                    continue
            if ad['km_age'] is not None:
                if ad['km_age'] > criteries['mileage'] + 1000:
#                     print('km_age', ad['km_age'], '| критерий:', criteries['mileage'])
                    continue
            if float(ad['price']) > criteries['budget']:
#                 print('price', ad['price'], '| критерий:', criteries['budget'])
                continue
            if criteries['max_owners'] == criteries['max_owners']:
                if ad['owners_count'] == '4+':
                    if criteries['max_owners'] < 4:
#                         print('owners', ad['owners_count'], '| критерий:', criteries['max_owners'])
                        continue
                elif ad['owners_count'] != None:
                    if int(ad['owners_count']) > criteries['max_owners']:
#                         print('owners', ad['owners_count'], '| критерий:', criteries['max_owners'])
                        continue
#             if ad['generation_id'] != criteries['generation']:
#                 continue
            if criteries['max_volume'] == criteries['max_volume']:
                if not (criteries['min_volume'] <= float(ad['displacement']) <= criteries['max_volume']):
#                     print('volume', ad['displacement'], '| критерий:', criteries['min_volume'], criteries['max_volume'])
                    continue
            if criteries['trasmission'] != 'Любая':
                transmission = dict_transmission[dict_transmission['id'] == int(ad['transmission_type_id'])]
                transmission = transmission['label'].item()
                if transmission != criteries['trasmission']:
                    if transmission not in criteries['trasmission'].split(', '):
#                         print('transmission', transmission, '| критерий:', criteries['trasmission'])
                        continue
            if criteries['engine_type'] != 'Любой':
                engine = dict_engine_type[dict_engine_type['id'] == int(ad['engine_type_id'])]
                engine = engine['label'].item()
                if engine != criteries['engine_type']:
                    if engine not in criteries['engine_type'].split(', '):
#                         print('engine', engine, '| критерий:', criteries['engine_type'])
                        continue
            if criteries['body_type'] != 'Любой':
                body = dict_body[dict_body['id'] == int(ad['body_type_id'])]
                body = body['label'].item()
                if body != criteries['body_type']:
                    if body not in criteries['body_type'].split(', '):
#                         print('body', body, '| критерий:', criteries['body_type'])
                        continue
            if criteries['wheel_drive'] != 'Любой':
                wheel = dict_drive_type[dict_drive_type['id'] == int(ad['drive_type_id'])]
                wheel = wheel['label'].item()
                if wheel != criteries['wheel_drive']:
                    if wheel not in criteries['wheel_drive'].split(', '):
#                         print('wheel', wheel, '| критерий:', criteries['wheel_drive'])
                        continue
            if criteries['color'] != 'Любой':
                color = dict_color[dict_color['id'] == int(ad['color_id'])]
                color = color['label'].item()
                if color != criteries['color']:
                    if color not in criteries['color'].split(', '):
#                         print('color', color, '| критерий:', criteries['color'])
                        continue
            filtered.append(ad)
        except TypeError as e:
            print(f"Ошибка с элементом {ad}: {e}. Пропускаем...")
            mistakes += 1
            continue
    return filtered
import sys
from underwriting import predict_from_csv

# python app.py 'test_ad_2.csv'
def main(path):
    try:
        answer = predict_from_csv(path)
    except:
        answer = {'yandex_verdict': 'error', 'yandex_probability': 'error'}
    return answer

if __name__ == "__main__":
    args = sys.argv
    path = args[1]
    try:
        answer = main(path)
    except FileNotFoundError:
        answer = {'yandex_verdict' : 'error reading file', 'yandex_probability': 'error'}
    print(answer)

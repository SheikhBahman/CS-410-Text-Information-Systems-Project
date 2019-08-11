import textnorm
import split_canonical as split
import json


def getDataSet(file_name):
    with open(file_name) as json_data:
        data_list = json.load(json_data)

    return data_list


def getTextDataSet(file_name):
    text_data = set()
    f = open(file_name, 'r')
    for line in f:
        text_data.add(line.rstrip())
    f.close()
    return text_data


if __name__ == '__main__':
    scowl = getTextDataSet('./scowl.american.70/scowl.american.70')
    train_data = getDataSet('./lexnorm2015/train_data.json')
    norm = textnorm.TextNorm(train_data, None)
    split = split.SplitCanonical(norm, scowl)
    print(split.get_canonical("theyallloveyourcaraswell"))

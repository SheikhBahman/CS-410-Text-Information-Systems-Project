import json
import text_norm_classifier
import textnorm_eval as eval
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score


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


def saveDataSet(file_name, data_set):
    with open(file_name, 'w+') as json_data:
        json.dump(data_set, json_data)

if __name__ == '__main__':
    test_file = './lexnorm2015/test_data.json'
    truth_file = './lexnorm2015/test_truth.json'
    pred_file = './pred_out.json'
    train_set = getDataSet('./lexnorm2015/train_data.json')
    test_set = getDataSet(test_file)
    truth_set = getDataSet(truth_file)
    # features = [tn.getSupportFeature, tn.getConfidenceFeature,
    # tn.getStringLengthFeature, tn.getDeltaTokenCandidateFeature]
    classifier = RandomForestClassifier(n_estimators=10, criterion='entropy')
    # no need to override classifier cache unless features are being overridden
    tnc = text_norm_classifier.TextNormClassifier(
        classifier, train_set, truth_set)

    pred_out = tnc.predict(test_set)
    saveDataSet(pred_file, pred_out)
    eval.evaluate(pred_file, truth_file)
    #y_test = tnc.y_test()
    #cm = confusion_matrix(y_test, y_pred)
    #f1 = f1_score(y_test, y_pred)
    # print()
    #print("Confusion Matirx: \n{}".format(cm))
    #print("\nF1 Score: {}\n".format(f1))

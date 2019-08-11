import POS as pos
import json

def getDataSet(file_name):
    with open(file_name) as json_data:
        data_list = json.load(json_data)
    return data_list

if __name__ == '__main__':
    train_set = getDataSet('./lexnorm2015/train_data.json')
    tweet_set = []
    for tweet in train_set:
        tweet_set.append(' '.join(tweet['input']))
    
    print(tweet_set[:5]) 
    print('how many tweets? {}'.format(len(tweet_set)))
    data = pos.posTagged(tweet_set)
    
    print()
    print(data[:5])
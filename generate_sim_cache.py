import similarity as sm
import test_text_norm as test
from collections import defaultdict
import json

data_set = test.getDataSet('./lexnorm2015/train_data.json')
sim_map = sm.get_similarity_map(data_set, 2, 1)
m = 3
n = 2
k = 1

cache = defaultdict(list)
for tweet in data_set:
    for i in range(len(tweet['input'])):
        token = tweet['input'][i]
        if token not in cache:
            cache[token] = sm.get_top_m(token, sim_map, m, n, k)
            print('writing cache entry for {}'.format(token))
    for i in range(len(tweet['output'])):
        token = tweet['output'][i]
        if token not in cache:
            cache[token] = sm.get_top_m(token, sim_map, m, n, k)    
            print('writing cache entry for {}'.format(token))
with open('train_sim_cache.json', 'w') as fp:
    json.dump(cache, fp)
import similarity as sim
import test_text_norm as test

print('trigrams: ke$sha')
x = set(sim.get_ngrams('ke$sha', 3))
print(x)
print('Pass: ' + str(x == {'$ke<$>', 'sha$', 'e<$>s', '<$>sh'}))
print()

print('bigrams: hello world')
x = set(sim.get_ngrams('hello world', 2))
print(x)
print('Pass: ' + str(x == {'rl', 'el', 'll', 'or',
                           '$he', ' w', 'lo', 'ld$', 'o ', 'wo'}))
print()

print('bigrams: a')
x = set(sim.get_ngrams('a', 2))
print(x)
print('Pass: ' + str(x == set()))
print()

print('bigrams: an')
x = set(sim.get_ngrams('an', 2))
print(x)
print('Pass: ' + str(x == {'$an$'}))
print()

print('jacaard similarity between: love, looove')
j = sim.jacaard_similarity(sim.get_similarity_ngrams(
    'love', 2, 1), sim.get_similarity_ngrams('looove', 2, 1))
print(j)
print()

data_set = test.getDataSet('./lexnorm2015/train_data.json')
sim_map = sim.get_similarity_map(data_set, 2, 1)
print('train_data similarity map first 5 keys:')
print(list(sim_map.keys())[0])
print(sim_map[list(sim_map.keys())[0]])
print(list(sim_map.keys())[1])
print(sim_map[list(sim_map.keys())[1]])
print(list(sim_map.keys())[2])
print(sim_map[list(sim_map.keys())[2]])
print(list(sim_map.keys())[3])
print(sim_map[list(sim_map.keys())[3]])
print(list(sim_map.keys())[4])
print(sim_map[list(sim_map.keys())[4]])
print()

print('first m similarity matches for looove')
print(sim.get_top_m('looove',sim_map,20,2,1))

import textnorm
import json


def getDataSet(file_name):
    with open(file_name) as json_data:
        data_list = json.load(json_data)

    return data_list

def get_splits(token, canon):
    if token in canon:
        return [token]
    token = token.strip()
    splits = get_splits_help(token, canon)
    split_rank = []
    for split in splits:
        split = split.strip()
        split_rank.append((len(split.split(' ')),split))
    
    split_rank = sorted(split_rank, key=lambda x: x[0])
    return [x[1] for x in split_rank]
    
def get_splits_help(token, canon):
    if len(token)<2:
        if is_canonical_split_token(token, canon):
            return [token]
        return []
    
    candidates = []
    for i in range(1,len(token)+1):
        sub_cand = []
        if is_canonical_split_token(token[:i], canon):
            sub_cand = get_splits_help(token[i:], canon)
            for cand in sub_cand:
                candidates.append(token[:i] + ' ' + cand)
            if token[i:] == '':
                candidates.append(token[:i])
    return candidates
    
def is_canonical_split_token(token, canon):
    if token in canon and len(token)>1:
        return True
    if len(token)==1 and token in ['i','a']:
        return True
    return False
    
def getLexicon(data_set):
    words = []
    for word in data_set:
        words.append(word.lower())
    return words

if __name__ == '__main__':
    train_data = getDataSet('./lexnorm2015/train_data.json')
    norm = textnorm.TextNorm(train_data, None)
    canon = norm.getCanonical()
    print(get_splits('loveyourcar',canon))
    print(get_splits('treatyourself',canon))

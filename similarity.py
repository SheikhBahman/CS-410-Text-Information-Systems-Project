from collections import defaultdict
import re


def get_string_similarity(token, candidate, n, k):
    if token == candidate:
        return 1.0
    if len(token)<n or len(candidate)<n:
        return 0
    list1 = get_similarity_ngrams(token, n, k)
    list2 = get_similarity_ngrams(candidate, n, k)
    return jacaard_similarity(list1, list2)

def get_similarity_map(data_set, n, k):
    similarity_map = defaultdict(list)
    token_set = set()
    for tweet in data_set:
        for i in range(len(tweet['output'])):
            token = tweet['output'][i]
            if token.startswith('#') or token.startswith('@') or token.startswith('http://') or token.startswith('https://') or not re.match("^[a-zA-Z_\-]*$", token):
                continue
            if token not in token_set:
                token_set.add(token)
                ngrams = get_similarity_ngrams(token, n, k)
                for ngram in ngrams:
                    similarity_map[ngram].append(token)
    return similarity_map


def get_top_m(token, similarity_map, cache, m, n, k):
    candidates = []
    token = token.lower()
    if cache is not None and token in cache:
        return cache[token]
    # skip urls, expensive to compute, and similarity means nothing
    if token.startswith('#') or token.startswith('@') or token.startswith('http://') or token.startswith('https://') or not re.match("^[a-zA-Z_\-]*$", token):
        return []
    #print('get top {} for {}'.format(m,token))
    ngrams = get_similarity_ngrams(token, n, k)
    for ngram in ngrams:
        if ngram in similarity_map:
            candidates += similarity_map[ngram]

    candidates = list(set(candidates))

    c_similarity = []
    for candidate in candidates:
        c_ngrams = get_similarity_ngrams(candidate, n, k)
        j = jacaard_similarity(c_ngrams, ngrams)
        c_similarity.append((candidate, j))

    c_similarity.sort(key=lambda x: x[1], reverse=True)
    topm = [c[0] for c in c_similarity[:m]]
    if cache is not None:
        #print(cache)
        cache[token] = topm
    return topm


def jacaard_similarity(list1, list2):
    list1 = list(set(list1))
    list2 = list(set(list2))
    intersect = len(set(list1).intersection(list2))
    union = len(list(set(list1 + list2)))

    return 1.0*intersect/union

# current limitation, we can only get skip bigrams
# n is size of the largest grams to get. If n is 3 for example we will get
# bigrams and trigrams. k is the largest gap to use for skip grams. We will use
# bigrams that skip 1 character up to k.


def get_similarity_ngrams(token, n, k):
    gram_list = []
    for cur_n in range(2, n+1):
        gram_list += get_ngrams(token, cur_n)

    for cur_k in range(1, k+1):
        gram_list += get_skip_bigrams(token, cur_k)

    gram_list = list(set(gram_list))
    return gram_list


def get_ngrams(orig_string, n):

    term_char = '$'
    skip_char = '|'

    if (len(orig_string) < n):
        return []

    if (len(orig_string) == n):
        return [term_char + orig_string + term_char]

    begin_gram = orig_string[:n]
    end_gram = orig_string[-n:]

    # first, get n grams
    ngrams = get_char_ngrams(orig_string, n)

    found_begin = False
    found_end = False

    processed_list = []
    for char_tuple in list(ngrams):
        token = ''.join(list(char_tuple))
        # escape the dollar character, we want to preserve, but not confuse with begin/end dollars
        esc_token = token.replace(
            term_char, '<' + term_char + '>').replace(skip_char, '<' + skip_char + '>')

        if token == begin_gram and not found_begin:
            esc_token = term_char + esc_token
            found_begin = True

        elif token == end_gram and not found_end:
            esc_token = esc_token + term_char
            found_end = True

        processed_list.append(esc_token)

    # filter out duplicates
    processed_list = list(set(processed_list))

    return processed_list


def get_char_ngrams(orig_string, n):
    num_grams = len(orig_string)-n+1
    gram_list = list()
    for x in range(0, num_grams):
        gram = orig_string[x:x+n]
        gram_list.append(gram)
    return gram_list

# TODO: if we ever need to get skip trigrams we will need to reimplement


def get_skip_bigrams(orig_string, k):
    if k < 1:
        raise Exception('k must be >0')

    gram_len = 2 + k
    ngrams = get_ngrams(orig_string, gram_len)
    term_char = '$'
    skip_char = '|'

    processed_list = []
    for ngram in ngrams:
        prefix = ''
        suffix = ''

        # strip off the terminators
        if ngram[0] == term_char:
            ngram = ngram[1:]
            prefix = term_char

        if ngram[-1] == term_char:
            ngram = ngram[:-1]
            suffix = term_char

        # unescape special characters $ and |
        ngram = ngram.replace(
            '<' + term_char + '>', term_char).replace('<' + skip_char + '>', skip_char)
        skip_gram = ''

        char1 = ngram[0]
        # re-escape special characters
        char1 = char1.replace(term_char, '<' + term_char +
                              '>').replace(skip_char, '<' + skip_char + '>')

        char2 = ngram[-1]
        char2 = char2.replace(term_char, '<' + term_char +
                              '>').replace(skip_char, '<' + skip_char + '>')

        skip_gram = char1 + skip_char + char2

        # re-add begin & end chars
        processed_list.append(skip_gram)

    # filter out duplicates
    processed_list = list(set(processed_list))

    return processed_list

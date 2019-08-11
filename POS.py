"""
Created on Sat Oct 27 10:07:51 2018 -- Version 1.0
Modified on Fri, Nov 1 15:32:45 2-18 -- Version 2.0

@author: Bahman
"""
# import nltk
# import execnet
import CMUTweetTagger

# don't want to 0)do this ever time for performance reasons
# nltk.download('stopwords')
# nltk.download('punkt')


def posTagged(tweets):

    taggedData = CMUTweetTagger.runtagger_parse(tweets)
    posTagsPerTweet = []
    for tweet in taggedData:
        sumConf = 0.0
        count = 0
        for tokenTup in tweet:
            sumConf = sumConf + tokenTup[2]
            count = count + 1
        avgConf = 0 if count == 0 else (sumConf/count)
        posTagsPerTweet.append((tweet, avgConf))
    return posTagsPerTweet


def posConfi(tid, index, candidate, candidate_tweets, cache, data_map):
    if 'pos' not in cache or tid not in cache['pos']:
        __generatePosTags(cache, candidate_tweets, data_map)
    orig_pos = cache['pos'][tid]
    new_pos = cache['pos'][tid + '-' + str(index)][candidate]
    if (len(new_pos[0]) <= index):
        return 0
    return new_pos[0][index][2] - orig_pos[0][index][2]


def posConfiPrev(tid, index, candidate, candidate_tweets, cache, data_map):
    if 'pos' not in cache or tid not in cache['pos']:
        __generatePosTags(cache, candidate_tweets, data_map)
    if index == 0:
        return 0
    orig_pos = cache['pos'][tid]
    new_pos = cache['pos'][tid + '-' + str(index)][candidate]

    return new_pos[0][index-1][2] - orig_pos[0][index-1][2]


def posConfTweet(tid, index, candidate, candidate_tweets, cache, data_map):
    if 'pos' not in cache or tid not in cache['pos']:
        __generatePosTags(cache, candidate_tweets, data_map)

    orig_pos = cache['pos'][tid]
    new_pos = cache['pos'][tid + '-' + str(index)][candidate]

    return new_pos[1] - orig_pos[1]


def __generatePosTags(cache, candidate_tweets, data_map):
    pos_input = []
    tweet_ids = sorted(data_map.keys())
    cache['pos'] = dict()
    for tid in tweet_ids:
        tweet = data_map[tid]
        # append the base tweet
        pos_input.append(candidate_tweets[tid])
        # then all of the candidate tweets
        for i in range(len(tweet['input'])):
            if (tid + '-' + str(i)) in candidate_tweets:
                candidates = sorted(
                    candidate_tweets[tid + '-' + str(i)].keys())
                for candidate in candidates:
                    pos_input.append(
                        candidate_tweets[tid + '-' + str(i)][candidate])

    tags = posTagged(pos_input)

    tag_pos = -1
    for tid in tweet_ids:
        tweet = data_map[tid]
        tag_pos += 1
        tweet_tag = tags[tag_pos]
        # append the base tweet
        cache['pos'][tid] = tweet_tag
        # then all of the candidate tweets
        for i in range(len(tweet['input'])):
            if (tid + '-' + str(i)) in candidate_tweets:
                candidates = sorted(
                    candidate_tweets[tid + '-' + str(i)].keys())
                for candidate in candidates:
                    tag_pos += 1
                    if (tid + '-' + str(i)) not in cache['pos']:
                        cache['pos'][tid + '-' + str(i)] = dict()
                    cache['pos'][tid + '-' + str(i)][candidate] = tags[tag_pos]

    return ''


# ----------------------------------------------------------
# Old versions just save it in the case something is needed
# ----------------------------------------------------------

'''
def features(sentence, index):
    return {
        'word': sentence[index],
        'is_first': index == 0,
        'is_last': index == len(sentence) - 1,
        'is_capitalized': sentence[index][0].upper() == sentence[index][0],
        'is_all_caps': sentence[index].upper() == sentence[index],
        'is_all_lower': sentence[index].lower() == sentence[index],
        'prefix-1': sentence[index][0],
        'prefix-2': sentence[index][:2],
        'prefix-3': sentence[index][:3],
        'suffix-1': sentence[index][-1],
        'suffix-2': sentence[index][-2:],
        'suffix-3': sentence[index][-3:],
        'prev_word': '' if index == 0 else sentence[index - 1],
        'next_word': '' if index == len(sentence) - 1 else sentence[index + 1],
        'has_hyphen': '-' in sentence[index],
        'is_numeric': sentence[index].isdigit(),
        'capitals_inside': sentence[index][1:].lower() != sentence[index][1:]
    }

def posTagged(textData):

    from nltk.corpus import stopwords
    from nltk.tokenize import sent_tokenize

    stopWords = set(stopwords.words('english'))

    tokenizedData = sent_tokenize(textData)


    tagged_sentences = []
    for sentence in tokenizedData:

        allWords = []

        wordsList = nltk.word_tokenize(sentence)

        wordListCleaned = [
            word for word in  wordsList if not word in stopWords]

        for word in wordListCleaned:
            if word not in allWords and word:
                allWords.append(word)
        tagged_sentences.append(nltk.pos_tag(allWords))

    cutoff = int(.75 * len(tagged_sentences))
    training_sentences = tagged_sentences[:cutoff]
    test_sentences = tagged_sentences[cutoff:]

    def transform_to_dataset(tagged_sentences):
        X, y = [], []
        for tagged in tagged_sentences:
            for index in range(len(tagged)):
                X.append(features([w for w, t in tagged], index))
                y.append(tagged[index][1])

        return X, y

    X, y = transform_to_dataset(training_sentences)

    from sklearn.tree import DecisionTreeClassifier
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.pipeline import Pipeline

    clf = Pipeline([
        ('vectorizer', DictVectorizer(sparse=False)),
        ('classifier', DecisionTreeClassifier(criterion='entropy'))
    ])


    clf.fit(X[:10000], y[:10000])

    X_test, y_test = transform_to_dataset(test_sentences)

    return (tagged_sentences,clf.score(X_test, y_test))'''


'''Version 1
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
def posTagged(textData):

    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    stopWords = set(stopwords.words('english'))

    tokenizedData = sent_tokenize(textData)

    allWords = []
    for sentence in tokenizedData:

        wordsList = nltk.word_tokenize(sentence)

        removetable = str.maketrans('', '', '@#%.!?><,')

        wordListCleaned = [s.translate(removetable) for s in wordsList]

        wordListCleaned = [
            word for word in wordListCleaned if not word in stopWords]

        for word in wordListCleaned:
            if word not in allWords and word:
                allWords.append(word)


    return nltk.pos_tag(allWords)'''

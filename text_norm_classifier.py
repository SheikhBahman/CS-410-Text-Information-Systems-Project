import similarity as sm
import numpy as np
from textnorm import TextNorm
from split_canonical import SplitCanonical
from sklearn import preprocessing
import json
#import nltk
#import alt_split as split
#import splitter

class TextNormClassifier:
    __features = []
    #__y_test = []
    __classifier = None
    __text_normaliser = None
    __split = None
    __candidate_tweets = None
    __scaler = None

    def __init__(self,  classifier, train_data, test_data, cache=None, features="jin", feature_funcs=[]):

        # cache should be specified only if the default features are overridden, this is the default cache content for the default feature set
        if cache is None:
            cache = dict()
        if 'sim' not in cache:
            with open('./train_sim_cache.json') as json_data:
                cache['sim'] = json.load(json_data)

        self.__candidate_tweets = dict()

        self.__text_normaliser = TextNorm(train_data, cache)
        #self.__split = SplitCanonical(
            #self.__text_normaliser, lexicon)
        self.__define_feature_funcs(features, feature_funcs)
        self.__classifier = classifier
        #self.__y_test = self.__get_y_test(test_data)
        self.__train_classifier(train_data)

    def __define_feature_funcs(self, features, feature_funcs):
        if features == "jin" or len(feature_funcs) == 0:
            self.__add_jin_features()
        elif features == "jin+":
            self.__add_jin_features()
            self.__features.append(feature_funcs)
        else:
            self.__features = feature_funcs

    def __add_jin_features(self):
        self.__features.append(self.__text_normaliser.getSupportFeature)
        self.__features.append(self.__text_normaliser.getConfidenceFeature)
        self.__features.append(self.__text_normaliser.getStringLengthFeature)
        self.__features.append(
            self.__text_normaliser.getDeltaTokenCandidateFeature)
        self.__features.append(self.__text_normaliser.getJacaardFeature)
        
        # if using default features, initialize the pos tokenizer
        #nltk.download('stopwords')
        #nltk.download('punkt')
        self.__features.append(self.__text_normaliser.getPOSiFeature)
        self.__features.append(self.__text_normaliser.getPOSiPrevFeature)
        self.__features.append(self.__text_normaliser.getPOSTweetFeature)

    # def __get_y_test(self, test_data):
        # return self.__generate_y(test_data)

    def __generate_features(self, data_map, tid, token, index, candidate):
        feature_vec = []
        for feature in self.__features:
            feature_vec.append(feature(data_map, tid, token,
                                       index, candidate, self.__candidate_tweets))
        return feature_vec

    def __train_classifier(self, train_data):
        X_train, y_train = self.__generate_X_y(train_data)
        self.__scaler = preprocessing.StandardScaler().fit(X_train)
        self.__classifier.fit(self.__scaler.transform(X_train), y_train)

    def __generate_X_y(self, data_set):
        X = self.__generate_X(data_set)
        y = self.__generate_y(data_set)
        return X, y

    def __generate_X(self, data_set):
        X = []
        data_map = self.__get_data_map(data_set)

        self.__get_candidate_tweets(data_set)

        data_map = self.__get_data_map(data_set)
        pred = []
        for tweet in data_set:
            for i in range(len(tweet['input'])):
                tid = tweet['tid']
                token = tweet['input'][i].lower()
                if self.__text_normaliser.isCanonicalForm(token):
                    continue

                candidates = sorted(
                    self.__candidate_tweets[tid + '-' + str(i)].keys())

                for candidate in candidates:
                    X.append(self.__generate_features(
                        data_map, tid, token, i, candidate))

        return X

    def __get_candidate_tweets(self, data_set):
        # first generate all of the candidates and index them
        # into a multi level dictionary: tid-i, candidate, "tweet text"
        for tweet in data_set:
            tid = tweet['tid']
            self.__candidate_tweets[tid] = ' '.join(tweet['input'])
            for i in range(len(tweet['input'])):
                token = tweet['input'][i].lower()
                if self.__text_normaliser.isCanonicalForm(token):
                    continue
                self.__candidate_tweets[tid + '-' + str(i)] = dict()
                candidates = self.__get_candidates(token)
                for candidate in candidates:
                    cand_tweet = tweet['input'].copy()
                    cand_tweet[i] = candidate
                    self.__candidate_tweets[tid + '-' +
                                            str(i)][candidate] = ' '.join(cand_tweet)
        return

    def __get_data_map(self, data_set):
        data_map = dict()
        for tweet in data_set:
            for i in range(len(tweet['input'])):
                token = tweet['input'][i].lower()
                if self.__text_normaliser.isCanonicalForm(token):
                    continue
                # only add tweets that need normalization
                data_map[tweet['tid']] = tweet
                break
        return data_map

    def __generate_y(self, data_set):
        y = []
        for tweet in data_set:
            for i in range(len(tweet['input'])):
                token = tweet['input'][i].lower()
                if self.__text_normaliser.isCanonicalForm(token):
                    continue
                token_out = tweet['output'][i].lower()
                candidates = sorted(self.__get_candidates(token))
                for candidate in candidates:
                    y.append(int(candidate == token_out))
        return y

    def __get_candidates(self, token):
        candidates = []
        candidates.append(token)
        static_map = self.__text_normaliser.getStaticMappingDictionary()
        if token in static_map:
            candidates.extend(
                c for c in static_map[token] if c not in candidates)

        # todo: function to split into multiple canonical forms, example: 'loveyourcar'
        #if not self.__text_normaliser.isCanonicalForm(token):
            #cand = self.__split.get_canonical(token)
            #candidates.extend(cand)
        #not a canonical form, no other candidates
        #if not self.__text_normaliser.isCanonicalForm(token) and len(list(set(candidates)))==1:
            #cand = split.get_splits(token, self.__text_normaliser.getCanonical())
            #candidates.extend(cand)
        #if not self.__text_normaliser.isCanonicalForm(token) and len(list(set(candidates)))==1:
            #candidates.append(' '.join(splitter.split(token)))

        # constrained mode only gets similar forms for tokens with consecutive duplicate letters
        if self.__text_normaliser.hasConsecutiveDuplicateLetters(token) and not self.__text_normaliser.isCanonicalForm(token):
            candidates.extend(
                c for c in self.__text_normaliser.getTopMSimilar(token) if c not in candidates)

        return list(set(candidates))

    # construct the normalization output for this tweet set
    def predict(self, data_set):
        self.__get_candidate_tweets(data_set)

        data_map = self.__get_data_map(data_set)
        pred = []
        for tweet in data_set:
            tweet['output'] = tweet['input'].copy()
            for i in range(len(tweet['input'])):
                tid = tweet['tid']
                token = tweet['input'][i].lower()
                if self.__text_normaliser.isCanonicalForm(token):
                    continue

                candidates = sorted(
                    self.__candidate_tweets[tid + '-' + str(i)].keys())
                X = []

                for candidate in candidates:
                    X.append(self.__generate_features(
                        data_map, tid, token, i, candidate))
                X = self.__scaler.transform(X)
                y_prob = np.array(self.__classifier.predict_proba(X))[
                    :, 1].tolist()
                tweet['output'][i] = candidates[y_prob.index(max(y_prob))]
            pred.append(tweet)

        return pred

    # def y_test(self):
        # return self.__y_test

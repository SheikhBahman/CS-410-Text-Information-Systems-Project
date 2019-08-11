from collections import defaultdict
import similarity as sm
import POS as pos
#import nltk
import re


class TextNorm:

    __k = 0
    __n = 0
    __m = 0
    __static_map_dict = defaultdict(list)
    __similarity_map = defaultdict(list)
    __support = dict()
    __confidence = dict()
    __cache = dict()
    __canon = set()

    def __init__(self, data_set, cache, k=1, n=2, m=3):
        for tweet in data_set:
            self.__updateStaticMap(tweet)
            self.__updateSupportCount(tweet)
            self.__updateCanon(tweet)
        self.__k = k
        self.__m = m
        self.__n = n
        self.__similarity_map = sm.get_similarity_map(
            data_set, n=self.__n, k=self.__k)
        self.__cache = cache

    def __updateStaticMap(self, tweet):
        for i in range(len(tweet['input'])):
            token = tweet['input'][i].lower()
            candidate = tweet['output'][i].lower()
            if self.__newCandidate(token, candidate):
                self.__static_map_dict[token].append(candidate)
            self.__incrementConfidenceCount(token, candidate)
        return

    def __newCandidate(self, token, candidate):
        return (token not in self.__static_map_dict) or (candidate not in self.__static_map_dict[token])

    def __incrementConfidenceCount(self, token, candidate):
        if token not in self.__confidence:
            self.__confidence[token] = dict()
        if candidate not in self.__confidence[token]:
            self.__confidence[token][candidate] = 1
            return
        self.__confidence[token][candidate] += 1        
        #if token+candidate not in self.__confidence:
            #self.__confidence[token + candidate] = 0
        #self.__confidence[token + candidate] += 1
        return

    def __updateSupportCount(self, tweet):
        for token in tweet['input']:
            token = token.lower()
            if token not in self.__support:
                self.__support[token] = 0
            self.__support[token] += 1
        return

    def __getSupport(self, token):
        if token.lower() not in self.__support:
            return 0
        return self.__support[token]

    def __getConfidence(self, token, candidate):
        token = token.lower()
        candidate = candidate.lower()
        if self.__invalidTokenCandidatePair(token, candidate):
            return 0
        if self.__getSupport(token) == 0:
            return 0
        return self.__confidence[token][candidate]*1.0 / self.__support[token]

    def __invalidTokenCandidatePair(self, token, candidate):
        return self.__notCandidateOfToken(token, candidate) or self.__zeroConfidence(token, candidate)

    def __notCandidateOfToken(self, token, candidate):
        return token not in self.__confidence or candidate not in self.__confidence[token]
        #return token+candidate not in self.__confidence

    def __zeroConfidence(self, token, candidate):
        #return self.__confidence[token + candidate] == 0
        return self.__confidence[token][candidate]==0

    def ___getBestCandidate(self, token):
        token = token.lower()
        best_candidate = ""
        best_candidate_confidence = -1
        for candidate in self.__static_map_dict[token]:
            confidence = self.__getConfidence(token, candidate)
            if confidence > best_candidate_confidence:
                best_candidate_confidence = confidence
                best_candidate = candidate
        return best_candidate

    def __updateCanon(self, tweet):
        for token in tweet['output']:
            if token not in self.__canon:
                self.__canon.add(token)
        return

    def generateCanonical(self, token):
        new_tokens = []
        start = 0
        end = start + 1
        while end <= len(token):
            part_token = token[start:end]
            if not self.isCanonicalForm(part_token):
                end += 1
            else:
                new_tokens.append(part_token)
                start = end + 1
                end = start + 1
        return new_tokens

    def hasConsecutiveDuplicateLetters(self, token):
        #at least 3 of the same letters in a row, two letters was too loose of a constraint because many canonical words have two of the same letter in a row
        if len(token)<3:
            return False
        for i in range(len(token) - 2):
            if token[i] == token[i + 1] == token[i + 2]:
                return True
        return False

    def getCanonical(self):
        return self.__canon

    def isCanonicalForm(self, token):
        # special unique forms
        if token.startswith('#') or token.startswith('@') or token.startswith('http://') or token.startswith('https://') or not re.match("^[a-zA-Z_\-]*$", token):
            return True
        if len(self.__static_map_dict[token]) == 0:
            return token in self.__canon
        # has translations not equal to the token itself
        if len(self.__static_map_dict[token]) > 1 or self.__static_map_dict[token][0] != token:
            return False
        return token in self.__canon

    def getSupport(self, token):
        return self.__getSupport(token)

    def getStringLengthFeature(self, data_map, tid, token, index, candidate, candidate_tweets):
        return len(token)

    def getDeltaTokenCandidateFeature(self, data_map, tid, token, index, candidate, candidate_tweets):
        return abs(len(candidate) - len(token))

    def getSupportFeature(self, data_map, tid, token, index, candidate, candidate_tweets):
        return self.__getSupport(token)

    def getConfidenceFeature(self, data_map, tid, token, index, candidate, candidate_tweets):
        return self.__getConfidence(token, candidate)

    def getPOSiFeature(self, data_map, tid, token, index, candidate, candidate_tweets):
        return pos.posConfi(tid, index, candidate, candidate_tweets, self.__cache, data_map)

    def getPOSiPrevFeature(self, data_map, tid, token, index, candidate, candidate_tweets):
        return pos.posConfiPrev(tid, index, candidate, candidate_tweets, self.__cache, data_map)

    def getPOSTweetFeature(self, data_map, tid, token, index, candidate, candidate_tweets):
        return pos.posConfTweet(tid, index, candidate, candidate_tweets, self.__cache, data_map)
        
    def getJacaardFeature(self, data_map, tid, token, index, candidate, candidate_tweets):
        return sm.get_string_similarity(token, candidate, self.__n, self.__k)

    def getStaticMappingDictionary(self):
        return self.__static_map_dict

    def getTopMSimilar(self, token):
        return sm.get_top_m(token, self.__similarity_map, self.__cache['sim'], m=self.__m, n=self.__n, k=self.__k)

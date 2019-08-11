import string
import operator
import math


class SplitCanonical:
    __norm = None
    __lexicon = None
    __use_lexicon = False
    __use_canon = True

    def __init__(self, text_normalizer, lexicon=None, use_all=True):
        self.__norm = text_normalizer
        self.__lexicon = lexicon
        if not lexicon is None:
            self.__use_lexicon = True
            self.__use_canon = use_all

    def __get_all_canonicals(self, token):
        canonicals = dict()
        for nchars in range(1, len(token)):
            canonicals = {**canonicals, **
                          self.__canonicals_in_token(token, nchars)}
        canonicals = sorted(canonicals.items(), key=lambda kv: kv[1])
        return canonicals

    def __canonicals_in_token(self, token, length):
        canonicals = dict()
        start_pos = 0
        while start_pos + length <= len(token):
            part = token[start_pos:start_pos+length]
            if self.__valid_canoncial(part, length):
                canonicals[part] = start_pos
            start_pos += 1
        return canonicals

    def __valid_canoncial(self, token, length):
        if length == 1:
            return self.__is_valid_1_char(token)
        return self.__is_canonical(token)

    def __is_valid_1_char(self, part):
        non_canoncical = ''
        valid_1_chars = ['i', 'a']
        if part in valid_1_chars:
            return part
        return non_canoncical

    def __is_canonical(self, token):
        is_canonical = False
        if self.__use_lexicon:
            is_canonical = token in self.__lexicon
        if self.__use_canon:
            is_canonical = is_canonical or self.__norm.isCanonicalForm(token)
        return is_canonical

    def __get_candidates(self, canonicals, length):
        new_base = []
        matrix = self.__adjacency(canonicals)
        while not self.__is_empty(matrix):
            del new_base[:]
            for i in range(len(matrix)):
                for j in range(1, len(matrix[0])):
                    if matrix[i][j] == 1:
                        new_base.append(
                            (canonicals[i][0] + ' ' + canonicals[j][0], 0))
            canonicals = self.__new_canonicals(new_base, canonicals, length)
            matrix = self.__adjacency(canonicals)
        return self.__final_candidates(canonicals, length)

    def __adjacency(self, canonicals):
        matrix = self.__new_matrix(canonicals)
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if len(canonicals[i][0].replace(' ', '')) == canonicals[j][1]:
                    matrix[i][j] = 1
        return matrix

    def __new_matrix(self, canonicals):
        col_dim = len(canonicals)
        row_dim = self._count_base_strings(canonicals)
        matrix = [[0 for x in range(col_dim)]
                  for y in range(row_dim)]
        return matrix

    def _count_base_strings(self, canonicals):
        count = 0
        for canonical in canonicals:
            if canonical[1] == 0:
                count += 1
        return count

    def __is_empty(self, matrix):
        counter = 0
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                counter += matrix[i][j]
        return counter == 0

    def __final_candidates(self, canonicals, length):
        candidates = [x for x in canonicals if x[1] == 0]
        candidates = [x for x in canonicals if len(
            x[0].replace(' ', '')) == length]
        candidates.sort(key=operator.itemgetter(1))
        return candidates

    def __most_likely(self, canonicals):
        candidate_scores = dict()
        for canonical in canonicals:
            candidate_scores[canonical[0]
                             ] = self.__canonical_support(canonical[0])
        return max(candidate_scores, key=lambda k: candidate_scores[k])

    def __canonical_support(self, token):
        support = 1
        words = token.lower().split()
        for word in words:
            word_support = self.__support(word)
            log_value = 1 if word_support == 0 else math.log2(word_support+1)
            support *= log_value
        return support

    def __support(self, token):
        return self.__norm.getSupport(token)

    def __new_canonicals(self, new_base_strings, canonicals, token_length):
        canonicals = self.__remove_old_base(canonicals, token_length)
        canonicals = self.__add_new_base(new_base_strings, canonicals)
        canonicals.sort(key=operator.itemgetter(1))
        return canonicals

    def __remove_old_base(self,  canonicals, token_length):
        new_canonicals = []
        for canonical in canonicals:
            if canonical[1] != 0 or len(canonical[0].replace(' ', '')) == token_length:
                new_canonicals.append(canonical)
        return new_canonicals

    def __add_new_base(self, new_base_strings, canonicals):
        for i in range(len(new_base_strings)):
            canonicals.append(new_base_strings[i])
        return canonicals

    def get_canonical(self, token):
        token = token.lower()
        all_canonicals = self.__get_all_canonicals(token)
        candidates = self.__get_candidates(all_canonicals, len(token))
        if len(candidates) == 0:
            return token
        return self.__most_likely(candidates)

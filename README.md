# A Classifier for Text Normalization on Twitter

This project is an implementation of the normalization system described by Jin in this (<http://noisy-text.github.io/2015/pdf/WNUT13.pdf>) paper. We have implemented the constrained mode described in the paper as our course project for CS-410 Text Information Systems at UIUC.

## Getting Started

git pull https://github.com/SheikhBahman/CS-410-Text-Information-Systems-Project

### Installation

You will need to use a linux based machine. The following instructions have been tested on Ubuntu 18.04

* sudo apt-get update

If you do not have java installed:

* sudo apt-get install default-jdk

If you do not have python installed: 

* sudo apt-get install python3
* sudo apt-get install python3-pip

Install sklearn

* pip install sklearn

To get the lexnorm data:

* wget http://noisy-text.github.io/2015/files/lexnorm2015.tgz<br/>
* tar xvzf lexnorm2015.tgz

To download the tweet tagger from source (not required, included in this repository):

* https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/ark-tweet-nlp/ark-tweet-nlp-0.3.2.tgz
* tar xvzf ark-tweet-nlp-0.3.2.tgz

### POS Tagger

The compiled CMU pos tagger, ark-tweet-nlp-0.3.2.jar, is included for convenience but you can also compile from source from this repository to get the latest version: https://github.com/brendano/ark-tweet-nlp. 

### Running the Sample Code

Sample code that uses a random forest classifier is in test_text_norm.py. To run the sample case and see the F1, precision and recall:

python3 test_text_norm.py

## Implementation

This project is implemented in a series of modules that handle different parts of the normalization process.

### text_norm_classifier.py

Generates the candidates, trains the classifier from the training data, and generates the predictions from the test data. 

### textnorm.py

Generates the static mapping dictionary, support and confidence data structures, generates support confidence and string features, builds the canonical forms dictionary, and has wrappers for all of the classifier features.

### similarity.py

Generates n-grams and skip-grams, builds the similarity index, generates similarity features, and calculates Jacaard similarity between strings.

### POS.py

Preps tweet data for POS tagging, generates POS confidence features.

### textnorm_eval.py

Adapted from the evaluation script for the W-NUT 2015 Lex English Lexical Normalization competition. We modified this script to dump out the specific tweets the system classified incorrectly into error_out.txt.

### Implementation Notes

This implementation does not use a text splitter as mentioned in the paper. See lessons learned for explanation.

## How to Use

This tool can be used with any binary classifier from the sklearn library. Example:

classifier = RandomForestClassifier(n_estimators=10, criterion='entropy')<br/>
tnc = text_norm_classifier.TextNormClassifier(classifier, train_set, truth_set)<br/>
pred_out = tnc.predict(test_set)<br/><br/>
See test_text_norm.py for a more thorough example. You can also just run test_text_norm.py to see the results for the default settings we used.

## Evaluation

With the default features and candidate generation the performance is:

precision: 0.9059<br/>
recall:   0.7673<br/>
F1:       0.8308<br/><br/>
This is slightly lower than the Jin paper, likely because text splitting is not implemented. See lessons learned section

### Error Output
When this tool is run, an error output file is generated: error_out.txt. This file has the following format:

Token   Canonical   Freq    Actual<br/>
ya      your    11      ['you', 'you', 'you', 'you', 'you', 'you', 'you', 'you', 'you', 'you', 'you']

Token: the token that the tool attempted to normalize<br/>
Canonical: the correct normalization<br/>
Freq: The number of times this token and canonical pair were seen in the training data<br/>
Actual: The canonical form the word was normalized to in each instance

## Lessons Learned

### Text Splitting

Text splitting phrases like “loveyourcar” into their proper canonical forms is difficult, because in multiple cases there are multiple possible candidates (e.g. “lovey our car”). Every attempt we made to introduce a splitter generated many erroneous candidates and brought down the performance of the classifier dramatically to around F1 = 0.5. We tried https://github.com/TimKam/compound-word-splitter as well as two of our own implementations and neither of them were successful (see split_canonical.py and alt_split.py). The Jin paper does not discuss how they achieved splitting without reducing performance. However, without implementing word splitting, we have achieved an F1 score of 0.83 which is only 0.01 lower than the paper. This shows that word splitting is not a large contributor to accuracy.

### Similarity Candidates

According to the Jin paper, the constrained mode only generates candidates from the similarity index when there are repeated letters, such as “looove”. We found that setting the minimum at three repetitions is appropriate for this task. Many English words have two of the same letter in a row, but none have three. Setting the limit to 2 generates many false positives.

## Ideas for Improvement

Many of the errors we found in error_out.txt are related to the lack of dictionary entries in the static mapping dictionary. From our research we have found that abbreviations of words are often novel and invented by users often. A static mapping dictionary is expected to have limited success. 

There are many options for better abbreviation detection. Phonetic similarity, statistical models for deletion-based abbreviations, or even deep learning are possibilities.

Another idea that might help is creating a classifier that decides whether a word is a canonical form or not. In this project, we used our training data to decide whether a given word is a canonical form. A classifier that detects whether a word is likely a canonical form or not, might be helpful for increasing precision.

## Authors

* Nathan Soule
* Paul Nel
* Bahman Sheikh

## Acknowledgments

* CMU tweet tagger: http://www.cs.cmu.edu/~ark/TweetNLP/
* Python CMU tweet tagger wrapper adapted from: https://github.com/ianozsvald/ark-tweet-nlp-python/blob/master/CMUTweetTagger.py
* LexNorm W-NUT competition data and scripts: http://noisy-text.github.io/2015/norm-shared-task.html

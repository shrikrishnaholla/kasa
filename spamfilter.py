import nltk
import os
import re
from collections import defaultdict      

hamstringlist = [open(os.getcwd() + '/datasets/enron1/ham/' + f).read() 
					for f in os.listdir(os.getcwd() + '/datasets/enron1/ham')]
spamstringlist = [open(os.getcwd() + '/datasets/enron1/spam/' + f).read() 
					for f in os.listdir(os.getcwd() + '/datasets/enron1/spam')]

ham_trainset = hamstringlist[:1500]
ham_testset = hamstringlist[1500:]

spam_trainset = spamstringlist[:500]
spam_testset = spamstringlist[500:]

def get_msg_words(msg, stopwords = nltk.corpus.stopwords.words('english')):
    '''
    Returns the set of unique words contained in an e-mail message. Excludes 
    any that are in an optionally-provided list. 

    NLTK's 'wordpunct' tokenizer is used, and this will break contractions.
    For example, don't -> (don, ', t). Therefore, it's advisable to supply
    a stopwords list that includes contraction parts, like 'don' and 't'.
    '''
    
    # Note, remove '=' symbols before tokenizing, since these are
    # sometimes occur within words to indicate, e.g., line-wrapping.
    msg_words = set(nltk.wordpunct_tokenize(msg.replace('-\n', '').lower()))
     
    # Get rid of stopwords
    msg_words = msg_words.difference(stopwords)
    
    # Get rid of punctuation tokens, numbers, and single letters.
    msg_words = [w for w in msg_words if re.search('[a-zA-Z]', w) and len(w) > 1]
    
    return msg_words

def word_indicator(msg, **kwargs):
    '''
    Feature Extractor
    -----------------
    Create a dictionary of entries {word: True} for every unique
    word in a message.

    Note **kwargs are options to the word-set creator,
    get_msg_words().
    '''
    features = defaultdict(list)
    msg_words = get_msg_words(msg, **kwargs)
    for  w in msg_words:
            features[w] = True
    return features

def features_from_messages(messages, label, feature_extractor, **kwargs):
    '''
    Make a (features, label) tuple for each message in a list of a certain,
    label of e-mails ('spam', 'ham') and return a list of these tuples.

    Note every e-mail in 'messages' should have the same label.
    '''
    features_labels = []
    for msg in messages:
        features = feature_extractor(msg, **kwargs)
        features_labels.append((features, label))
    return features_labels


def make_train_test_sets(feature_extractor, **kwargs):
    '''
    Make (feature, label) lists for each of the training 
    and testing lists.
    '''
    spam_features_train = features_from_messages(spam_trainset, 'spam', 
                                        feature_extractor, **kwargs)
    ham_features_train = features_from_messages(ham_trainset, 'ham', 
                                       feature_extractor, **kwargs)
    features_train_set = spam_features_train + ham_features_train

    spam_features_test = features_from_messages(spam_testset, 'spam',
                                       feature_extractor, **kwargs)

    ham_features_test = features_from_messages(ham_testset, 'ham',
                                      feature_extractor, **kwargs)
    
    return features_train_set, spam_features_test, ham_features_test

def check_classifier(feature_extractor, **kwargs):
    '''
    Train the classifier on the training spam and ham, then check its accuracy
    on the test data, and show the classifier's most informative features.
    '''
    
    # Make training and testing sets of (features, label) data
    features_train_set, spam_features_test, ham_features_test = \
        make_train_test_sets(feature_extractor, **kwargs)
    
    # Train the classifier on the training set
    classifier = nltk.NaiveBayesClassifier.train(features_train_set)
    
    # How accurate is the classifier on the test sets?
    print ('Test Spam accuracy: {0:.2f}%'
       .format(100 * nltk.classify.accuracy(classifier, spam_features_test)))
    print ('Test Ham accuracy: {0:.2f}%'
       .format(100 * nltk.classify.accuracy(classifier, ham_features_test)))

    # Show the top 20 informative features
    print classifier.show_most_informative_features(20)

def create_classifier(feature_extractor, **kwargs):
    spam_features = features_from_messages(spamstringlist[:500], 'spam', 
                                        feature_extractor, **kwargs)
    ham_features = features_from_messages(hamstringlist, 'ham', 
                                        feature_extractor, **kwargs)
    features_set = spam_features + ham_features

    #Train the classifier on the training set
    classifier = nltk.NaiveBayesClassifier.train(features_set)
    return classifier

classifier = create_classifier(word_indicator)
print "Spam Filter is ready"

def isSpam(message):
    if classifier.classify(word_indicator(message)) == "spam":
        return True
    else:
        return False

if __name__ == '__main__':
    print classifier.classify(word_indicator("""Hi,
        We are an Online SEO Consultant.
        I hope you are doing well and have time to read my proposal.
        Advertising in the online world is one of the most inexpensive and highly effective methods of promoting a business.
        We are Leading Indian Based SEO & Web Development Company and one of the very few companies which offer organic SEO Services with a full range of supporting services such as one way themed text links, blog submissions, directory submissions, article writing and postings, etc.
        We are a team of 85+ professionals which includes 28 full time SEO experts. We are proud to inform you that our team handled 180+ SEO projects and obtained 100000+ manually built links in the past 1 year"""))
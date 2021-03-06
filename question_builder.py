from mturk import MTurkSurveyFactory, ACCESS_ID, SECRET_KEY, HOST, https_connection_factory
from boto.mturk.connection import MTurkConnection
import sys
from articles import *
from extractor import *
from nltk import tokenize
import itertools
import pickle
from algorithm_test import Topic, Document

missing = []

ACCESS_ID = ''
SECRET_KEY = ''
HOST = 'mechanicalturk.amazonaws.com'

def build_survey_list(listOfLinks=[]):
    """ Build the survey from the list of links passed. Uses the extractor classes to request, parse and 
        extract the article from the URL. This function then builds the survey questions from the first
        paragraph of the article and returns a tuple list of [(url, title, sentences)]
    """
    tuple_list = []
    for item in listOfLinks:
        try:
            article = build_extractor(item).article()
            #print article
            #url, title, first paragraph
            para = get_paragraph(article['paragraphs'][1:len(article['paragraphs'])-1],
                                 [tokenize.sent_tokenize(article['paragraphs'][0])])
            para = list(itertools.chain(*para))
            para = ' '.join(para)
            tuple_list.append([item, article['title'],
                               para.decode(encoding='UTF-8', errors='strict')])
        except:
            missing.append(item)
    print len(tuple_list)
    return tuple_list

def get_paragraph(listOfParagraphs, first):
    """We want at least 3 sentences to compare"""
    return get_first_paragraph(listOfParagraphs, first)


def submit_forms():
    """
    Creates all of the surveys for processing as HITs on Mechanical Turk. Article sources are pulled from
    articles.py
    """
    fact = MTurkSurveyFactory()
    mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                         aws_secret_access_key=SECRET_KEY,
                         host=HOST, is_secure=True,
                         https_connection_factory=(https_connection_factory, ()))
    #loop over every article
    tuple_list = []
    tuple_list.extend(build_survey_list(mississippi))
    tuple_list.extend(build_survey_list(boston_miranda))
    tuple_list.extend(build_survey_list(bangladesh))
    tuple_list.extend(build_survey_list(sunil_tripathi))
    tuple_list.extend(build_survey_list(syria))
    tuple_list.extend(build_survey_list(spain))
    tuple_list.extend(build_survey_list(virgin_galactic))
    tuple_list.extend(build_survey_list(michigan))
    tuple_list.extend(build_survey_list(jason_collins))
    tuple_list.extend(build_survey_list(american_held_nk))
    tuple_list.extend(build_survey_list(sherpa_fight))
    tuple_list.extend(build_survey_list(faa_furloughs))
    tuple_list.extend(build_survey_list(bagram))
    tuple_list.extend(build_survey_list(jackson))
    tuple_list.extend(build_survey_list(pills))
    tuple_list.extend(build_survey_list(poison))
    print 'Retrieved', len(tuple_list)
    print 'Missing: ', len(missing)
    print missing
    print 'Sending it to mechanicalturk'
    fact = MTurkSurveyFactory()
    questionForms = fact.buildSurvey(tuple_list)
    print len(questionForms)
    missing_forms = []
    for questionForm in questionForms:
        try:
            fact.submitHITs(mtc=mtc, questionForms=[questionForm])
        except:
            missing_forms.extend(questionForm)

    print len(missing_forms), ' forms could not be submitted'
    print missing_forms

def get_first_paragraph(listOfParagraphs, first):
    """We want at least 3 sentences to compare"""
    #print listOfParagraphs

    if len(first) >= 3:
        return_value = first
        return return_value

    if len(listOfParagraphs) is 0:
        #nothing left...
        return first
    #alright, append the next paragraph
    if len(tokenize.sent_tokenize(listOfParagraphs[0])) >= 3:
        #append string to first
        tokenized = tokenize.sent_tokenize(listOfParagraphs[0])
        first.extend(tokenized)
        return first
    else:
        #well append the whole next paragraph and continue
        tokenized = tokenize.sent_tokenize(listOfParagraphs[0])
        first.extend(tokenized)
        para = get_first_paragraph(listOfParagraphs[1:len(listOfParagraphs)-1],
                                   first)
        return para

def load_from_file():
    """Loads the topics from file"""
    dev_topics = pickle.load(open("dev_set.p", "rb"))
    eval_topics = pickle.load(open("eval_set.p", "rb"))
    total_topics = []
    total_topics.extend(dev_topics)
    total_topics.extend(eval_topics)
    return total_topics

if __name__=='__main__':
    topics = load_from_file()
    print len(topics)
    tuple_list = []
    #loop over all the documents
    for topic in topics:
        for document in topic.documents:
            document.split_sections()
            text = document.begining
            title = document.title
            url = document.url
            print url, title, text
            tuple_list.append([url, title, ' '.join(text)])
        
    print len(tuple_list)
    print 'Retrieved', len(tuple_list)
    print 'Missing: ', len(missing)
    print missing
    print 'Sending it to mechanicalturk'
    mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                         aws_secret_access_key=SECRET_KEY,
                         host=HOST, is_secure=True,
                         https_connection_factory=(https_connection_factory, ()))
    
    print mtc.get_all_hits()

    fact = MTurkSurveyFactory()
    questionForms = fact.buildSurvey(tuple_list)
    print len(questionForms)
    missing_forms = []
    for questionForm in questionForms:
        try:
            fact.submitHITs(mtc=mtc, questionForms=[questionForm])
        except:
            missing_forms.extend(questionForm)
            print "Unexpected error:", sys.exc_info()[0]

    print len(missing_forms), ' forms could not be submitted'
    print missing_forms



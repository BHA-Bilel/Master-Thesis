from flask import current_app
from gensim import corpora, models, similarities, utils
from gensim.test.utils import get_tmpfile
from webapp.model.preprocess_docs import pre_process
from webapp.models import SimAnnex, VolFatwa, QuestFatwa, Fatwa
from webapp.qasystem.serialize import Data
import os


def iter_documents(dataset):
    file_no = 0
    training_files = 0
    for data in dataset:
        document = pre_process(data.question)
        training_files += 1
        file_no += 1
        yield utils.tokenize(document, lower=True, errors='ignore')


class TxtSubdirsCorpus(object):
    def __init__(self, dataset):
        self.dataset = dataset
        self.dictionary = corpora.Dictionary(iter_documents(self.dataset))

    def __iter__(self):
        for tokens in iter_documents(self.dataset):
            yield self.dictionary.doc2bow(tokens)


def create_lsi_model(cl_id, dataset):
    bow_corpus, mydictionary = create_corp(cl_id=cl_id, dataset=dataset)
    create_model(cl_id=cl_id, bow_corpus=bow_corpus, mydictionary=mydictionary)


def create_corp(cl_id, dataset):
    DICT_PATH = os.path.join(current_app.config['MODELS_PATH'], cl_id, 'lsi', 'dict')
    CORPUS_PATH = os.path.join(current_app.config['MODELS_PATH'], cl_id, 'lsi', 'corp')
    if not os.path.exists(DICT_PATH) and not os.path.exists(CORPUS_PATH):
        os.mkdir(DICT_PATH)
        os.mkdir(CORPUS_PATH)

    bow_corpus = TxtSubdirsCorpus(dataset=dataset)
    mydictionary = bow_corpus.dictionary
    mydictionary.save(DICT_PATH)
    corpora.MmCorpus.serialize(CORPUS_PATH, bow_corpus)
    return bow_corpus, mydictionary


def create_model(cl_id, bow_corpus, mydictionary):
    MODEL_PATH = os.path.join(current_app.config['MODELS_PATH'], cl_id, 'lsi', 'model')
    INDEX_PATH = os.path.join(current_app.config['MODELS_PATH'], cl_id, 'lsi', 'index')

    if not os.path.exists(MODEL_PATH) and not os.path.exists(INDEX_PATH):
        os.mkdir(MODEL_PATH)
        os.mkdir(INDEX_PATH)

    tfidf_model = models.TfidfModel(bow_corpus)
    corpus_tfidf = tfidf_model[bow_corpus]
    lsi_model = models.LsiModel(corpus_tfidf, id2word=mydictionary)

    corpus_lsi = lsi_model[corpus_tfidf]
    index_tmpfile = get_tmpfile("index")
    index_lsi = similarities.Similarity(index_tmpfile, corpus_lsi, num_features=len(mydictionary))
    lsi_model.save(MODEL_PATH)
    index_lsi.save(INDEX_PATH)


def get_dictionary(cl_id):
    DICT_PATH = os.path.join(current_app.config['MODELS_PATH'], cl_id, 'lsi', 'dict')
    return corpora.Dictionary.load(DICT_PATH)


def get_index(cl_id):
    INDEX_PATH = os.path.join(current_app.config['MODELS_PATH'], cl_id, 'lsi', 'index')
    return similarities.Similarity.load(INDEX_PATH)


def get_model(cl_id):
    MODEL_PATH = os.path.join(current_app.config['MODELS_PATH'], cl_id, 'lsi', 'model')
    return models.LsiModel.load(MODEL_PATH)


def get_sims(cl_id, tokenized_doc):
    mydictionary = get_dictionary(cl_id)
    query_bow = mydictionary.doc2bow(tokenized_doc.split())
    index = get_index(cl_id)
    mymodel = get_model(cl_id)
    sims = index[mymodel[query_bow]]
    lsi_sim = sorted(enumerate(sims), key=lambda item: -item[1])
    return lsi_sim

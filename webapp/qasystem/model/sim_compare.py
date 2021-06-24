from os import path

from gensim import corpora, models, similarities, utils
from gensim.test.utils import get_tmpfile

from webapp import ctx
from webapp.fatwas.models import Hadj, Salat, Sawm, Zakat
from webapp.qasystem.model.preprocess_docs import pre_process

# provided for code
from webapp.qasystem.serialize import Data

THIS_FOLDER = path.dirname(path.abspath(__file__))
with ctx:
    MODELS_PATH = THIS_FOLDER + '/models/sim_compare/'
    INDEX_PATH = THIS_FOLDER + '/models/sim_compare/'
    CORPUS_PATH = THIS_FOLDER + '/models/sim_compare/corp/'
    DICT_PATH = THIS_FOLDER + '/models/sim_compare/dict/'


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
        # create dictionary = mapping for documents => sparse vectors
        self.dictionary = corpora.Dictionary(iter_documents(self.dataset))

    def __iter__(self):
        for tokens in iter_documents(self.dataset):
            # transform tokens (strings) into a sparse vector, one at a time
            yield self.dictionary.doc2bow(tokens)


topic_to_id = {'Hadj': 0, 'Salat': 1, 'Sawm': 2, 'Zakat': 3}


def create_corp_models(topic, dataset):
    bow_corpus, mydictionary = create_corp(topic=topic, dataset=dataset)
    create_models(topic, bow_corpus, mydictionary)


def create_corp(topic, dataset):
    bow_corpus = TxtSubdirsCorpus(dataset=dataset)
    mydictionary = bow_corpus.dictionary
    mydictionary.save(DICT_PATH + topic)
    corpora.MmCorpus.serialize(CORPUS_PATH + topic, bow_corpus)
    return bow_corpus, mydictionary


def create_models(topic, bow_corpus, mydictionary):
    # model no 1: tfidf
    tfidf_model = models.TfidfModel(bow_corpus)
    corpus_tfidf = tfidf_model[bow_corpus]
    index_tmpfile = get_tmpfile("index_tfidf_" + topic)
    index_tfidf = similarities.Similarity(index_tmpfile, corpus_tfidf, num_features=len(mydictionary))  # build the index
    tfidf_model.save(path.join(MODELS_PATH, 'tfidf', topic + "_model"))
    # corpus_tfidf.save()
    index_path = path.join(INDEX_PATH, 'tfidf', topic + "_index")
    index_tfidf.save(index_path)

    # model no 2: lsi
    lsi_model = models.LsiModel(bow_corpus, id2word=mydictionary)
    corpus_lsi = lsi_model[bow_corpus]
    index_tmpfile = get_tmpfile("index_lsi_" + topic)
    index_lsi = similarities.Similarity(index_tmpfile, corpus_lsi, num_features=len(mydictionary))  # build the index
    lsi_model.save(path.join(MODELS_PATH, 'lsi', topic + "_model"))
    # corpus_lsi.save()
    index_path = path.join(INDEX_PATH, 'lsi', topic + "_index")
    index_lsi.save(index_path)

    # moel no 3: Latent Dirichlet Allocation, LDA
    # lda_model = models.LdaModel(bow_corpus, id2word=mydictionary, passes=100)
    # corpus_lda = lda_model[bow_corpus]
    # index_tmpfile = get_tmpfile("index_lda_" + topic)
    # index = similarities.Similarity(index_tmpfile, corpus_lda, num_features=len(mydictionary))  # build the index
    # lda_model.save(path.join(MODELS_PATH, 'lda', topic + "_model"))
    # # corpus_lda.save()
    # index_path = path.join(INDEX_PATH, 'lda', topic + "_index")
    # index.save(index_path)


def get_dictionaries(topic):
    if topic == 'Hadj':
        return corpora.Dictionary.load(DICT_PATH + 'Hadj')
    elif topic == 'Salat':
        return corpora.Dictionary.load(DICT_PATH + 'Salat')
    elif topic == 'Sawm':
        return corpora.Dictionary.load(DICT_PATH + 'Sawm')
    else:
        return corpora.Dictionary.load(DICT_PATH + 'Zakat')


def get_indexes(topic):
    indexes = [similarities.Similarity.load(path.join(INDEX_PATH, 'tfidf', topic + "_index")),
               similarities.Similarity.load(path.join(INDEX_PATH, 'lsi', topic + "_index"))]
    # similarities.Similarity.load(path.join(INDEX_PATH, 'lda', str(topic + "_index")))]
    return indexes


def get_modelss(topic):
    modelss = [models.TfidfModel.load(path.join(MODELS_PATH, 'tfidf', topic + "_model")),
               models.LsiModel.load(path.join(MODELS_PATH, 'lsi', topic + "_model"))]
    # models.LdaModel.load(path.join(MODELS_PATH, 'lda', topic + "_model"))]
    return modelss


def get_sims(topic, tokenized_doc):
    mydictionary = get_dictionaries(topic)
    query_bow = mydictionary.doc2bow(tokenized_doc.split())
    indexes = get_indexes(topic)
    mymodels = get_modelss(topic)

    if topic == 'Hadj':
        dbmodel = Hadj
    elif topic == 'Salat':
        dbmodel = Salat
    elif topic == 'Sawm':
        dbmodel = Sawm
    else:
        dbmodel = Zakat
    model_names = ['TF-IDF', 'LSI']
    result_arr = []
    for i in range(2):
        sims = indexes[i][mymodels[i][query_bow]]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        result = []
        document_order = 1
        for similarity in sims:
            if similarity[1] < 0.5 or document_order > 5:
                break
            doc_id = similarity[0] + 1
            # 'select question, answer from '+topic+' where id='+file_path
            instance = dbmodel.query.filter_by(id=doc_id).first()
            result.append(
                Data(model=model_names[i], similarity=str(similarity[1]), path=int(doc_id),
                     question=instance.question, answer=instance.answer,
                     fatwa_id=instance.id, mufti_id=instance.mufti_id))
            document_order += 1
        result_arr.append(result)
    return result_arr

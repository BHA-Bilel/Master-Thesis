import gensim
from flask import current_app
from gensim.models import Doc2Vec

from webapp.models import Fatwa, FatwaClass, SimAnnex, QuestFatwa, VolFatwa
from webapp.model.preprocess_docs import pre_process
from webapp.qasystem.serialize import Data
from os.path import join


def read_corpus(dataset):
    i = 0
    file_no = 0
    train_corpus = []
    for data in dataset:
        document = pre_process(data.question)
        words = document.split(" ")
        train_corpus.append(gensim.models.doc2vec.TaggedDocument(words, [i]))
        i += 1
        file_no += 1
    return train_corpus


def create_doc2vec_model(cl_id, dataset):
    train_corpus = read_corpus(dataset)
    model = gensim.models.doc2vec.Doc2Vec(vector_size=50, window=10, min_count=1, workers=8, alpha=0.025,
                                          min_alpha=0.015, epochs=100, dm=0)
    model.build_vocab(train_corpus)
    model.train(train_corpus, total_examples=len(train_corpus), epochs=model.epochs)
    model.save(join(current_app.config['MODELS_PATH'], cl_id, 'DOC2VEC', 'DOC2VEC.model'))

    return len(train_corpus)


def get_sim(tokenized_doc, cl_id):
    model = Doc2Vec.load(join(current_app.config['MODELS_PATH'], cl_id, 'DOC2VEC', 'DOC2VEC.model'))
    inferred_vector = model.infer_vector(tokenized_doc.split())
    doc2vec_sim = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
    return doc2vec_sim

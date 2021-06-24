from io import StringIO

import pickle
import pandas as pd
from flask import current_app
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from csv import DictReader, DictWriter
from random import shuffle
import joblib
from sklearn import metrics

from webapp import ctx
from webapp.model.preprocess_docs import pre_process

with ctx:
    MODEL_PATH = current_app.config['MODELS_PATH'] + "/scikit_class/class.model"
    TFIDF_PATH = current_app.config['MODELS_PATH'] + "/scikit_class/tfidf"
    TOPIC_ID_DF_PATH = current_app.config['MODELS_PATH'] + "/scikit_class/topic_id_df"


def create_csv(dataset, eligible):
    new_csvfile = StringIO()
    columns = ['document', 'topic']
    writer = DictWriter(new_csvfile, fieldnames=columns)
    writer.writeheader()
    for data in dataset:
        document = pre_process(data.question)
        writer.writerow({'document': document, 'topic': eligible[data.class_id]})
    new_csvfile.seek(0)
    return new_csvfile


def shuffle_csv(csv):
    reader = DictReader(csv)
    data = []
    for row in reader:
        data.append(row)
    rest = data[1:]
    shuffle(rest)

    new_csvfile = StringIO()
    columns = ['document', 'topic']
    writer = DictWriter(new_csvfile, fieldnames=columns)
    writer.writeheader()
    for row in rest:
        writer.writerow(row)

    new_csvfile.seek(0)
    return new_csvfile


df = None
topic_to_id = None
id_to_topic = None
features = None
labels = None


# creating and shuffling the csv file (corpus)
def prepare_corp(dataset, eligible):
    csv = create_csv(dataset=dataset, eligible=eligible)
    shuffled_csv = shuffle_csv(csv)
    global df, topic_to_id, id_to_topic, features, labels
    df = pd.read_csv(shuffled_csv)
    df.head()
    col = ['document', 'topic']
    df = df[col]

    df['topic_id'] = df['topic'].factorize()[0]
    topic_id_df = df[['topic', 'topic_id']].drop_duplicates().sort_values('topic_id')
    pickle.dump(topic_id_df, open(TOPIC_ID_DF_PATH, "wb"))
    topic_to_id = dict(topic_id_df.values)
    id_to_topic = dict(topic_id_df[['topic_id', 'topic']].values)
    tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='utf-8', ngram_range=(1, 2))
    features = tfidf.fit_transform(df.document).toarray()
    labels = df.topic_id
    pickle.dump(tfidf, open(TFIDF_PATH, "wb"))


def create(model):
    X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(features, labels, df.index,
                                                                                     test_size=0.33, random_state=0,
                                                                                     stratify=labels)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    joblib.dump(model, MODEL_PATH)

    out_dict = metrics.classification_report(y_test, y_pred, target_names=df['topic'].unique(), output_dict=True)
    data_frame = pd.DataFrame(out_dict).transpose()
    file = StringIO()
    data_frame.to_csv(file)
    return file, out_dict


def create_model(dataset, eligible):
    prepare_corp(dataset=dataset, eligible=eligible)
    model = LinearSVC()
    return create(model=model)


def predict_class(query_document):
    tfidf = pickle.load(open(TFIDF_PATH, "rb"))
    transformed_query = tfidf.transform([query_document])
    loaded_model = joblib.load(MODEL_PATH)
    predict = loaded_model.predict(transformed_query)
    topic_id_df = pickle.load(open(TOPIC_ID_DF_PATH, "rb"))
    prediction = topic_id_df.values[predict]
    return prediction[0][0]

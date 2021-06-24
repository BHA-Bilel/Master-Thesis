import pickle
from os import path

from nltk import ISRIStemmer
from nltk.corpus import stopwords

stop_exp = ['ّ', 'ِ', '؟', '،', 'ً', '.', 'ُ', ':', 'َ', '(', ')', '?', '/', '-', 'ْ', 'ٍ', 'ٌ', '«', '»', 'ـ', '–', '{', '}', '[', ']', '!', '_',
            's', '%', '`', '`', '!', '@', '#', '$', ':', '.', '¤', ';', ',', '٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩', '0', '1', '2', '3',
            '4', '5', '6', '7', '8', '9', '»', '«', 'ٚ', 'ٛ', 'ٜ', 'ٝ', 'ٞ', 'ٙ']

# added_words = ['خيرا', 'وجزاكم', 'نص', 'السؤال', 'وسئل', 'سئل', 'فضيلة', 'الشيخ', 'رحمه', 'وهو', 'في', 'من', 'على', 'حفظه', 'تعالى', 'عن', 'هل', 'ما',
#                'علما', 'وعندما', 'أثابكم', 'وعن', 'جزاكم', 'الإجابة', 'وهل', 'وأنه', 'أفيدونا', 'بارك', 'فقال', 'وعلى', 'وهي', 'وغيرها', 'وقد',
#                'أرجو', 'وهم', 'شيخنا', 'تقوم', 'وقال', 'عبارة', 'وأنا', 'وفي', 'وكيف', 'ونحن', 'وبعد', 'وذلك', 'وأن', 'يقول', 'والسؤال', 'وهذا',
#                'التوضيح', 'الإفادة', 'وفقكم', 'ذلك', 'رأي', 'وكل', 'المذكور', 'أفيدوني', 'وله', 'ويسأل', 'وبين', 'قالوا', 'سماحتكم', 'والآن',
#                'الجواب', 'خمس', 'ثلاث', 'واحد', 'خمسة', 'تسعة', 'الأول', 'فضيلتكم', 'ستة', 'وكنت', 'وعند', 'حفظكم', 'فأجاب', 'شاء', 'بقوله', 'عز',
#                'وجل', 'والحمد', 'وسلم', 'فضيلته', 'رضي', 'المبارك']

added_words = ['السؤال', 'سئل', 'ويسأل' 'فقال', 'شيخنا', 'أفيدوني', 'الجواب', 'فضيلتكم', 'خيرا']

short_exp = ['هو', 'في', 'من', 'على', 'عن', 'هل', 'ما', 'هي', 'هم', 'في', 'أن', 'هذا']

long_exp = ['إن شاء الله', 'بارك الله فيكم', 'صلى الله عليه وسلم']

expressions = ['فضيلة الشيخ', 'رحمه الله', 'حفظه الله', 'نص السؤال', 'جزاكم الله', 'الله تعالى', 'أثابكم الله', 'والحمد لله', 'رضي الله',
               'أرجو الإجابة', 'من فضيلتكم', 'من سماحتكم', 'وفقكم الله', 'فأجاب بقوله', 'فأجاب فضيلته', 'أرجو التوضيح', 'أرجو الإفادة', 'الجواب من']


# stopwords : before 1782 / 1897 after

# def add_words_stopwords():
#     stop_words = []
#     with open(STOPWORDS_PATH + '.txt', 'r', encoding='utf-8') as f:
#         lines = f.readlines()
#         for line in lines:
#             words = line.split("-")
#             for word in words:
#                 if word not in stop_words:
#                     stop_words.append(word)
#     print("before : ", len(stop_words)) # before :  1782
#     for word in added_words:
#         if word not in stop_words:
#             stop_words.append(word)
#     print("after : ", len(stop_words)) # after : 1790
#     pickle.dump(stop_words, open(STOPWORDS_PATH + "-list", "wb"))


# add_words_stopwords()


def pre_process(document):
    # removing stop expressions
    for exp in stop_exp:
        document = document.replace(exp, "")

    for exp in long_exp:
        document = document.replace(exp, "")

    for exp in expressions:
        document = document.replace(exp, "")
    # stemming words
    stemmer = ISRIStemmer()
    dirpath = path.dirname(__file__)
    stop_words = pickle.load(open(path.join(dirpath, "stopwords-list"), "rb"))
    words = document.split()
    filtered_file = []
    for w in words:
        # excluding stop words and stemming
        if w not in stop_words:
            if len(w) < 4:  # only check short words to prevent removing other words
                if w not in short_exp:
                    filtered_file.append(stemmer.stem(w) + ' ')
            else:
                filtered_file.append(stemmer.stem(w) + ' ')
    filtered = ''.join(filtered_file)
    return filtered

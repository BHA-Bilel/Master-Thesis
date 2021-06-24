class Data:

    def __init__(self, model, similarity, doc_id):  # for web app
        super(Data, self).__init__()
        self.model = model
        self.similarity = similarity
        self.doc_id = doc_id

    def to_list(self):
        return [self.model, self.similarity]

    def add_model(self, model, similarity):
        self.model += ' / ' + model
        self.similarity += ' / ' + similarity

    def __eq__(self, other):
        if not isinstance(other, Data):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.doc_id == other.doc_id

    def __lt__(self, other):  # less than
        if not isinstance(other, Data):
            return NotImplemented

        return self.similarity < other.similarity

    def __le__(self, other):  # less or equal
        if not isinstance(other, Data):
            return NotImplemented

        return self.similarity <= other.similarity

    def __ne__(self, other):  # not equal
        if not isinstance(other, Data):
            return NotImplemented

        return self.path != other.path

    def __gt__(self, other):  # greater than
        if not isinstance(other, Data):
            return NotImplemented

        return self.similarity > other.similarity

    def __ge__(self, other):  # greater or equal
        if not isinstance(other, Data):
            return NotImplemented

        return self.similarity >= other.similarity

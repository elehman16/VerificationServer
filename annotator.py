
class Annotator(object):
    """Annotate articles.

    The main object of the application. Takes a
    `Reader` and a `Writer,` and uses them to
    provide an interface for annotating articles
    and submitting their annotations.
    """

    def __init__(self, reader):
        self.reader = reader

    def get_next_article(self, next_file):
        tmp = self.reader.get_next_article(next_file)
        return tmp

    def get_next_file(self, id_ = None):
        return self.reader._get_next_file(id_)

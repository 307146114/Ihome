from   .BaseHandler import BaseHandler
class IndexHandler(BaseHandler):

    def get(self):
        self.write('hello test')
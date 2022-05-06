class QuestionSource:
    def __init__(self, name, url=None, count__get_param=None):
        self.name = name
        self.api_url = url
        self.question_count_get_param = count__get_param

jservice = QuestionSource('jservice.io', 'https://jservice.io/api/random', 'count')
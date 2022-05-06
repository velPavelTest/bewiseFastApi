import requests

class QuestionSource:
    def __init__(self, name, url=None, count__get_param=None):
        self.name = name
        self.api_url = url
        self.question_count_get_param = count__get_param

    def get_questions_from_source(self, count: int) -> list:
        '''Получение у источника указанное число вопросов, возвращаем полученный из json список'''
        r = requests.get(self.api_url, params={self.question_count_get_param: count})
        if r.status_code != 200:
            r.raise_for_status()
        return r.json()

jservice = QuestionSource('jservice.io', 'https://jservice.io/api/random', 'count')
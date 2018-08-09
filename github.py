from urllib import request
from urllib.parse import urlencode
import json
import base64


PER_PAGE_MAX = 100


class Api():
    base_url = 'https://api.github.com'

    def __init__(self):
        self.auth = 'Basic ' + base64.b64encode(open('auth.txt', 'rb').read()).decode('utf-8')

    def get(self, path, **kwargs):
        url = f'{self.base_url}{path}?' + urlencode([*filter(lambda x: x[1], kwargs.items())])
        rq = request.Request(url)
        rq.add_header("Authorization", self.auth)
        response = request.urlopen(rq)
        return json.loads(response.read())

    def get_all_pages(self, path, **kwargs):
        result = []
        page = 1
        kwargs['per_page'] = PER_PAGE_MAX
        while True:
            kwargs['page'] = page
            chunk = self.get(path, **kwargs)
            result += chunk
            if len(chunk) < PER_PAGE_MAX:
                return result
            page += 1


api = Api()


class Repo():
    def __init__(self, url=None, owner=None, name=None):
        if not (url or (owner and name)):
            raise TypeError('Repo object needs url or owner and name')
        if not (owner and name):
            if 'github.com/' in url:
                url = url.split('github.com/', 1)[1]
            path = url.split('/')
            owner, name = path[:2]
        self.path = f'/repos/{owner}/{name}'

    def get_commits(self, sha=None, since=None, until=None):
        return api.get_all_pages(self.path + '/commits', sha=sha, since=since, until=until)

    def get_pulls(self, state='open'):
        return api.get_all_pages(self.path + '/pulls', state=state)

    def get_issues(self, state='open'):
        return api.get_all_pages(self.path + '/issues', state=state)

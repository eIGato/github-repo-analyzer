from urllib.request import urlopen
import json


class Api:
    base_url = 'https://api.github.com'

    def get(self, path, **kwargs):
        url = f'{self.base_url}{path}?' + '&'.join(f'{k}={v}' for k, v in kwargs.items() if v)
        response = urlopen(url)
        return json.loads(response.read())

    def get_all_pages(self, path, **kwargs):
        result = []
        page = 1
        while True:
            kwargs['page'] = page
            chunk = self.get(path, **kwargs)
            if not chunk:
                return result
            result += chunk
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

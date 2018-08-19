"""Simple Github API bindings module.

Attributes:
    api (Api): Github API instance.
    PER_PAGE_MAX (int): Maximum items count per page.
    ISO_DATE_FORMAT (str): Date format returned from Github.
"""
from urllib import request
from urllib.parse import urlencode
import json
import base64
from datetime import datetime


PER_PAGE_MAX = 100
ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class Struct():

    """Dot-notated version of dict."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Commit(Struct):

    """Git commit."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.author = Struct(**self.author)
        self.committer = Struct(**self.committer)


class Ticket(Struct):

    """Base class for pulls and issues"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.created_at = datetime.strptime(self.created_at, ISO_DATE_FORMAT)
        self.updated_at = datetime.strptime(self.updated_at, ISO_DATE_FORMAT)
        self.closed_at = self.closed_at and datetime.strptime(self.closed_at, ISO_DATE_FORMAT)


class Pull(Ticket):

    """Pull request."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.merged_at = self.merged_at and datetime.strptime(self.merged_at, ISO_DATE_FORMAT)


class Issue(Ticket):

    """Project issue."""


class Api():

    """Common API bindings.

    Attributes:
        auth (str): 'Authorization' header.
        base_url (str): URL of Github API host.
    """

    base_url = 'https://api.github.com'
    auth = 'Basic ' + base64.b64encode(open('auth.txt', 'rb').read()).decode('utf-8')

    def get(self, path: str, **kwargs):
        """Get response to request sent to given URL path.

        Args:
            path (str): Path to resource to get.
            **kwargs: URL parameters.

        Returns:
            list or dict: Parsed response.
        """
        url = f'{self.base_url}{path}?' + urlencode([*filter(lambda x: x[1], kwargs.items())])
        rq = request.Request(url)
        rq.add_header('Authorization', self.auth)
        response = request.urlopen(rq)
        return json.loads(response.read())

    def get_all_pages(self, path: str, **kwargs) -> list:
        """Get all items from paginated response.

        Args:
            path (str): Path to resource to get.
            **kwargs: URL parameters.

        Returns:
            list: Items from all pages.
        """
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

    """Repository API bindings.

    Attributes:
        path (str): Path to repository at Github API host.
    """

    def __init__(self, url=None, owner=None, name=None):
        """Init Repo object.

        May be initiated in two ways:
            Repo('eIGato/github-repo-analyzer')
            Repo(owner='eIGato', name='github-repo-analyzer')

        Args:
            url (str, optional): Full or short URL of Github repo.
            owner (str, optional): Repo owner.
            name (str, optional): Repo name.

        Raises:
            TypeError: If not enough args given.
        """
        if not (url or (owner and name)):
            raise TypeError('Repo object needs url or owner and name')
        if not (owner and name):
            if 'github.com/' in url:
                url = url.split('github.com/', 1)[1]
            path = url.split('/')
            owner, name = path[:2]
        self.path = f'/repos/{owner}/{name}'

    def get_commits(self, sha=None, since=None, until=None) -> list:
        """Get commits from the repo.

        Method gets commits starting from given HEAD (default: master).
        You may specify start and end date-time of analysys in ISO format.
        Like '2018-08-08' or '2018-08-09T12:00:00Z'.

        Args:
            sha (str, optional): HEAD commit or target branch name.
            since (str, optional): Start of the analysys.
            until (str, optional): End of the analysys.

        Returns:
            list: Commits.
        """
        since = since and since.isoformat(timespec='seconds')
        until = until and until.isoformat(timespec='seconds')
        return [Commit(**d) for d in api.get_all_pages(self.path + '/commits', sha=sha, since=since, until=until)]

    def get_pulls(self, state='open') -> list:
        """Get pull requests from the repo.

        Args:
            state (str, optional): PR state to filter: 'open', 'closed', 'all'.

        Returns:
            list: Pull requests.
        """
        return [Pull(**d) for d in api.get_all_pages(self.path + '/pulls', state=state)]

    def get_issues(self, state='open') -> list:
        """Get issues from the repo.

        Args:
            state (str, optional): Issue state to filter: 'open', 'closed', 'all'.

        Returns:
            list: Issues.
        """
        return [Issue(**d) for d in api.get_all_pages(self.path + '/issues', state=state)]

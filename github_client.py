import urllib3
import json
import re

from model import Issue


class GithubIssuesClient:

    def __init__(self, repo_url, username, token):
        urllib3.disable_warnings()
        headers = urllib3.util.make_headers(basic_auth=f'{username}:{token}')
        self.http = urllib3.PoolManager(headers={'user-agent': 'curl/7.64.1'})
        self.http.headers.update(headers)
        self.repo_url = repo_url
        self.api_url = 'https://api.github.com/repos/%s/%s/issues' % tuple(repo_url.rsplit('/', 2)[-2:])
        self.url_pattern = re.compile(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)')

    def _get(self, url: str) -> (bool, dict, dict):
        req = self.http.request('GET', url)
        resp = json.loads(req.data.decode('utf-8'))
        return (req.status == 200, req.headers, resp)

    def _url_search(self, text: str) -> bool:
        return self.url_pattern.search(text) is not None

    @property
    def issue_list(self) -> list:
        page = 1
        issue_list = []
        while True:
            page_url = f'{self.api_url}?page={page}'
            status, headers, issues = self._get(page_url)
            if status:
                if not issues:
                    return issue_list
                issue_list.extend(issues)
                page += 1
            else:
                raise Exception(f'[Error] {issues["message"]}')

    def inspect_issue(self, issue: dict) -> bool:
        # GitHub's REST API v3 compatible fix
        if 'pull_request' in issue:
            return False
        if self._url_search(issue['body']):
            return True
        if issue['comments'] > 0:
            return self.inspect_comments(issue['comments_url'])
        return False

    def inspect_comments(self, comments_api) -> bool:
        status, headers, comments = self._get(comments_api)
        if status:
            for comment in comments:
                if self._url_search(comment['body']):
                    return True
            return False
        else:
            raise Exception(f'[Error] {comments["message"]}')

    def parse_issue(self, issue: dict) -> Issue:
        labels = [label['name'] for label in issue['labels']]
        return Issue(
            id=issue['number'],
            title=issue['title'],
            url=issue['html_url'],
            date=issue['created_at'],
            labels=labels)

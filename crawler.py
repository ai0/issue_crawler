import os
import asyncio
import pathlib
import csv
from argparse import ArgumentParser

from utils import async_retry
from github_client import GithubIssuesClient

OUTPUT_DIR = pathlib.Path(os.path.abspath(__file__)).parent / 'output'


@async_retry(tries=2)
async def check(issue: dict, client: GithubIssuesClient, csv_writer) -> None:
    if client.inspect_issue(issue):
        issue_data = client.parse_issue(issue)
        issue_labels = ','.join(issue_data.labels)
        csv_writer.writerow([issue_data.id, issue_data.title, issue_data.url, issue_data.date, issue_labels])


async def fetch(url: str, output: str, username: str, token: str) -> None:
    client = GithubIssuesClient(url, username, token)
    issues = client.issue_list
    output_path = OUTPUT_DIR / output
    with open(output_path, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=' ')
        writer.writerow(['issue_id', 'title', 'url', 'date', 'labels'])
        await asyncio.gather(*(
            check(issue, client, writer)
            for issue in issues))

if __name__ == "__main__":
    parser = ArgumentParser(description='GitHub Issue Crawler')
    parser.add_argument('-u', '--url', dest='url', type=str, help='the url of target GitHub repo', required=True)
    parser.add_argument('-o', '--output', dest='output', type=str, help='the output file name', required=True)
    parser.add_argument('-gu', '--username', dest='username', type=str, help='GitHub username for API Rate Limit', required=True)
    parser.add_argument('-gt', '--token', dest='token', type=str, help='GitHub token for API Rate Limit (see https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line)', required=True)
    args = parser.parse_args()
    asyncio.run(fetch(args.url, args.output, args.username, args.token))

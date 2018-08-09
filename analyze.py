#!/usr/bin/env python3
"""Script to analyze given repository."""
from argparse import ArgumentParser
from datetime import datetime
from datetime import timedelta

from github import Repo


def parse_args():
    """Parse command-line args.

    Returns:
        object: Parsed args.
    """
    arg_parser = ArgumentParser(description='Program analyzes given Github repository.')
    arg_parser.add_argument('url', help='URL of target repository.')
    arg_parser.add_argument('--branch', help='Target branch (default: master).', default='master')
    arg_parser.add_argument('--since', help='Date to start analysys from.', default=None)
    arg_parser.add_argument('--until', help='Date to stop analysys at.', default=None)
    return arg_parser.parse_args()


def is_stale(date_iso: str, days: int) -> bool:
    """Determine if item created at gived date is stale.

    Args:
        date_iso (str): Creation date-time of the item in ISO format.
        days (int): Shelf life of the item.

    Returns:
        bool: True if stale, False otherwise.
    """
    date = datetime.strptime(date_iso, '%Y-%m-%dT%H:%M:%SZ')
    return datetime.now() - date > timedelta(days=days)


def main():
    """Script function."""
    args = parse_args()
    repo = Repo(args.url)

    # Analyze commits.
    commits = repo.get_commits(sha=args.branch, since=args.since, until=args.until)
    top_committers = {}
    for commit in commits:
        author_login = commit['author']['login']
        top_committers.setdefault(author_login, 0)
        top_committers[author_login] += 1
    top_committers = [(v, k) for k, v in top_committers.items()]
    top_committers.sort(reverse=True)
    top_committers = top_committers[:30]
    longest_login = 0
    for _, login in top_committers:
        longest_login = max(longest_login, len(login))
    for commit_count, login in top_committers:
        print(f'{login}{" " * (longest_login - len(login))} {commit_count}')

    # Analyze pull requests.
    open_pulls = repo.get_pulls(state='open')
    closed_pulls = repo.get_pulls(state='closed')
    stale_pulls = [*filter(lambda x: is_stale(x['created_at'], 30), open_pulls)]
    print(f'Pull requests: {len(open_pulls)} open, {len(closed_pulls)} closed, {len(stale_pulls)} stale.')

    # Analyze issues.
    open_issues = repo.get_issues(state='open')
    closed_issues = repo.get_issues(state='closed')
    stale_issues = [*filter(lambda x: is_stale(x['created_at'], 14), open_issues)]
    print(f'Issues: {len(open_issues)} open, {len(closed_issues)} closed, {len(stale_issues)} stale.')


if __name__ == '__main__':
    main()

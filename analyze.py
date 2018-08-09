#!/usr/bin/env python3
from argparse import ArgumentParser

from github import Repo


def parse_args():
    arg_parser = ArgumentParser(description='Program analyzes given Github repository.')
    arg_parser.add_argument('url', help='URL of target repository.')
    arg_parser.add_argument('--branch', help='Target branch (default: master).', default='master')
    arg_parser.add_argument('--since', help='Date to start analysys from.', default=None)
    arg_parser.add_argument('--until', help='Date to stop analysys at.', default=None)
    return arg_parser.parse_args()


def main():
    args = parse_args()
    repo = Repo(args.url)
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


if __name__ == '__main__':
    main()

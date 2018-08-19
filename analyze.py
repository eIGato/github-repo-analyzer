#!/usr/bin/env python3
"""Script to analyze given repository.

Attributes:
    SIMPLE_DATE_FORMAT (str): Date format to specify only date.
"""
from argparse import ArgumentParser
from datetime import datetime
from datetime import timedelta

from github import Repo
from github import ISO_DATE_FORMAT


SIMPLE_DATE_FORMAT = '%Y-%m-%d'


def parse_date(date_iso: str) -> datetime:
    """Parse date-time arg.

    Args:
        date_iso (str): Date or date-time in ISO format.

    Returns:
        datetime: Parsed date.
    """
    try:
        return datetime.strptime(date_iso, ISO_DATE_FORMAT)
    except ValueError:
        return datetime.strptime(date_iso, SIMPLE_DATE_FORMAT)


def parse_args():
    """Parse command-line args.

    Returns:
        object: Parsed args.
    """
    arg_parser = ArgumentParser(description='Program analyzes given Github repository.')
    arg_parser.add_argument('url', help='URL of target repository.')
    arg_parser.add_argument('--branch', help='Target branch (default: master).', default='master')
    arg_parser.add_argument('--since', help='Date to start analysys from.', type=parse_date, default=None)
    arg_parser.add_argument('--until', help='Date to stop analysys at.', type=parse_date, default=None)
    return arg_parser.parse_args()


def analyze_tickets(repo: Repo, ticket_type: str, since: datetime, until: datetime, shelf_life: timedelta):
    """Analyze issue-like ticket API.

    Args:
        repo (Repo): Repo to get tickets from.
        ticket_type (str): 'pulls' or 'issues'.
        since (datetime): Analysis start date.
        until (datetime): Analysis end date.
        shelf_life (timedelta): Time to become stale.
    """
    since = since or datetime.min
    until = until or datetime.max
    tickets = repo.get_pulls(state='all') if ticket_type == 'pulls' else repo.get_issues(state='all')
    opened_tickets = set(filter(
        lambda x: since <= x.created_at < until,
        tickets
    ))
    closed_tickets = set(filter(
        lambda x: x.state == 'closed' and since <= x.closed_at < until,
        tickets
    ))
    opened_and_closed_tickets = opened_tickets & closed_tickets
    still_open_tickets = set(filter(
        lambda x: x.state == 'open',
        opened_tickets
    ))
    stale_tickets = set(filter(
        lambda x: since <= x.created_at + shelf_life < until and (
            x.state == 'open' or x.closed_at >= until
        ),
        tickets
    ))
    closed_later_count = len(opened_tickets) - len(opened_and_closed_tickets) - len(still_open_tickets)
    print(f'{len(opened_tickets)} {ticket_type} had been opened.')
    print(f'    {len(opened_and_closed_tickets)} of them had been closed in the same period.')
    print(f'    {closed_later_count} of them had been closed later.')
    print(f'    {len(still_open_tickets)} of them are still open.')
    print(f'{len(closed_tickets)} {ticket_type} had been closed.')
    print(f'    {len(opened_and_closed_tickets)} of them had been opened in the same period.')
    print(f'    {len(closed_tickets) - len(opened_and_closed_tickets)} of them had been opened earlier.')
    print(f'{len(stale_tickets)} {ticket_type} had become stale.')
    print()


def main():
    """Script function."""
    args = parse_args()
    repo = Repo(args.url)

    # Analyze commits.
    commits = repo.get_commits(sha=args.branch, since=args.since, until=args.until)
    top_committers = {}
    for commit in commits:
        author_login = commit.author.login
        top_committers.setdefault(author_login, 0)
        top_committers[author_login] += 1
    top_committers = [(v, k) for k, v in top_committers.items()]
    top_committers.sort(reverse=True)
    top_committers = top_committers[:30]
    longest_login = len('Login')
    for _, login in top_committers:
        longest_login = max(longest_login, len(login))
    print('Most active committers:')
    print(f'Login{" " * (longest_login - len("Login"))} Commits')
    for commit_count, login in top_committers:
        print(f'{login}{" " * (longest_login - len(login))} {commit_count}')
    print()

    # Analyze pull requests.
    analyze_tickets(repo, 'pulls', since=args.since, until=args.until, shelf_life=timedelta(days=30))

    # Analyze issues.
    analyze_tickets(repo, 'issues', since=args.since, until=args.until, shelf_life=timedelta(days=14))


if __name__ == '__main__':
    main()

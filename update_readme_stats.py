#!/usr/bin/env python3
"""
Reads game_stats.json and updates LEADERBOARD, GAME_STATS, PARTICIPANTS
sections in README.md directly (without triggering a game action).
"""
import re
import json
from pathlib import Path
from github import Github
import os

def render_leaderboard(stats):
    top = sorted(
        stats['players'].items(),
        key=lambda x: x[1]['total'],
        reverse=True
    )[:10]
    if not top:
        return '*No players yet. Be the first!*'
    md  = '| Rank | Player | Total | Tic-Tac-Toe | Reversi | Number Guess |\n'
    md += '|:----:|--------|:-----:|:-----------:|:-------:|:------------:|\n'
    for i, (player, s) in enumerate(top, 1):
        rank = ['1st', '2nd', '3rd'][i-1] if i <= 3 else f'{i}th'
        md += f'| {rank} | [@{player}](https://github.com/{player}) | {s["total"]} | {s["tictactoe"]} | {s["reversi"]} | {s["guess"]} |\n'
    return md

def render_game_stats(stats):
    g = stats.get('games', {})
    ttt_total   = g.get('tictactoe', 0)
    rev_total   = g.get('reversi', 0)
    guess_total = g.get('guess', 0)
    grand_total = ttt_total + rev_total + guess_total

    if grand_total == 0:
        return '*No moves played yet.*'

    games = [
        ('Tic-Tac-Toe', ttt_total),
        ('Reversi / Othello', rev_total),
        ('Number Guessing', guess_total),
    ]
    games_sorted = sorted(games, key=lambda x: x[1], reverse=True)

    md  = f'**Total moves played: {grand_total}**\n\n'
    md += '| Rank | Game | Moves |\n'
    md += '|:----:|------|:-----:|\n'
    for i, (name, count) in enumerate(games_sorted, 1):
        rank = ['1st', '2nd', '3rd'][i-1] if i <= 3 else f'{i}th'
        bar_len = int((count / max(grand_total, 1)) * 20)
        bar = '#' * bar_len + '-' * (20 - bar_len)
        pct = round(count / grand_total * 100) if grand_total else 0
        md += f'| {rank} | {name} | {count} ({pct}%) `{bar}` |\n'
    return md

def render_participants(stats):
    if not stats['participants']:
        return '*No participants yet.*'
    total = len(stats['participants'])
    md = f'**Total participants: {total}**\n\n'
    for p in stats['participants']:
        n = stats['players'].get(p, {}).get('total', 0)
        md += f'[![@{p}](https://img.shields.io/badge/@{p}-{n}_moves-blue)](https://github.com/{p}) '
    return md

def replace_section(content, name, new_body):
    return re.sub(
        rf'<!-- {name}_START -->.*?<!-- {name}_END -->',
        f'<!-- {name}_START -->\n{new_body}\n<!-- {name}_END -->',
        content, flags=re.DOTALL
    )

def main():
    stats_path = Path('game_stats.json')
    with open(stats_path) as f:
        stats = json.load(f)

    token = os.environ['GITHUB_TOKEN']
    repo_name = os.environ['REPO']
    g = Github(token)
    repo = g.get_repo(repo_name)

    readme_obj = repo.get_contents('README.md')
    content = readme_obj.decoded_content.decode('utf-8')

    content = replace_section(content, 'LEADERBOARD',  render_leaderboard(stats))
    content = replace_section(content, 'GAME_STATS',   render_game_stats(stats))
    content = replace_section(content, 'PARTICIPANTS', render_participants(stats))

    repo.update_file(
        'README.md',
        'Update leaderboard and game stats from migration',
        content,
        readme_obj.sha,
        branch='main'
    )
    print('README.md updated.')

if __name__ == '__main__':
    main()

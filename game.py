#!/usr/bin/env python3
import os
import re
import sys
from github import Github
from games.tictactoe import TicTacToe
from games.reversi import Reversi
from games.guess import NumberGuess

TTT_PAT   = re.compile(r'^Tic-Tac-Toe:\s*(?:Put|Move)\s+[A-Ca-c][1-3]\s*$')
REV_PAT   = re.compile(r'^Reversi:\s*Put\s+[A-Ha-h][1-8]\s*$')
GUESS_PAT = re.compile(r'^Number\s+Guess:\s*\d+\s*$', re.I)


class GameManager:
    def __init__(self):
        self.g           = Github(os.environ['GITHUB_TOKEN'])
        self.repo        = self.g.get_repo(os.environ['REPO'])
        self.issue_num   = int(os.environ['ISSUE_NUMBER'])
        self.issue       = self.repo.get_issue(self.issue_num)
        self.actor       = os.environ['ACTOR']
        self.issue_title = os.environ.get('ISSUE_TITLE', '').strip()
        self.admin_user  = 'tadanobutubutu'
        self.owner, self.repo_name = os.environ['REPO'].split('/')

        self.ttt   = TicTacToe()
        self.rev   = Reversi()
        self.guess = NumberGuess()

    # ------------------------------------------------------------------ #
    #  有効手のみ issues から集計                                          #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _title_to_type(title):
        """TTT_PAT / REV_PAT / GUESS_PAT にマッチした時だけ有効。リセット系・不明は None。"""
        if TTT_PAT.match(title):   return 'tictactoe'
        if REV_PAT.match(title):   return 'reversi'
        if GUESS_PAT.match(title): return 'guess'
        return None

    @staticmethod
    def _add_count(players, games, login, gtype):
        if login not in players:
            players[login] = {'total': 0, 'tictactoe': 0, 'reversi': 0, 'guess': 0}
        players[login]['total'] += 1
        players[login][gtype]   += 1
        games[gtype]            += 1

    def _compute_stats(self, include_current=False):
        """
        閉じた全 issues を走査して有効手のみ集計する。
        include_current=True の時だけ、現在処理中の issue を先行カウントする。
        """
        players = {}
        games   = {'tictactoe': 0, 'reversi': 0, 'guess': 0}

        # 現在処理中の issue はまだ closed になっていないので、
        # 有効手の場合のみ先行カウントする
        if include_current:
            gtype = self._title_to_type(self.issue_title)
            if gtype:
                self._add_count(players, games, self.actor, gtype)

        for issue in self.repo.get_issues(state='closed'):
            if issue.number == self.issue_num:
                continue
            gtype = self._title_to_type(issue.title.strip())
            if gtype is None:
                continue
            self._add_count(players, games, issue.user.login, gtype)

        participants = sorted(players.keys(),
                              key=lambda p: players[p]['total'], reverse=True)
        return {'players': players, 'participants': participants, 'games': games}

    # ------------------------------------------------------------------ #
    #  レンダリング                                                         #
    # ------------------------------------------------------------------ #
    def _render_leaderboard(self, stats):
        top = sorted(stats['players'].items(),
                     key=lambda x: x[1]['total'], reverse=True)[:10]
        if not top:
            return '*No players yet. Be the first!*'
        md  = '| Rank | Player | Total | Tic-Tac-Toe | Reversi | Number Guess |\n'
        md += '|:----:|--------|:-----:|:-----------:|:-------:|:------------:|\n'
        for i, (player, s) in enumerate(top, 1):
            rank = ['1st', '2nd', '3rd'][i-1] if i <= 3 else f'{i}th'
            md += (f'| {rank} | [@{player}](https://github.com/{player}) '
                   f'| {s["total"]} | {s["tictactoe"]} | {s["reversi"]} | {s["guess"]} |\n')
        return md

    def _render_game_stats(self, stats):
        g = stats['games']
        ttt_total   = g.get('tictactoe', 0)
        rev_total   = g.get('reversi', 0)
        guess_total = g.get('guess', 0)
        grand_total = ttt_total + rev_total + guess_total
        if grand_total == 0:
            return '*No moves played yet.*'
        games_sorted = sorted([
            ('Tic-Tac-Toe',       ttt_total),
            ('Reversi / Othello', rev_total),
            ('Number Guessing',   guess_total),
        ], key=lambda x: x[1], reverse=True)
        md  = f'**Total moves played: {grand_total}**\n\n'
        md += '| Rank | Game | Moves |\n'
        md += '|:----:|------|:-----:|\n'
        for i, (name, count) in enumerate(games_sorted, 1):
            rank = ['1st', '2nd', '3rd'][i-1] if i <= 3 else f'{i}th'
            bar_len = int(count / grand_total * 20)
            bar = '#' * bar_len + '-' * (20 - bar_len)
            pct = round(count / grand_total * 100)
            md += f'| {rank} | {name} | {count} ({pct}%) `{bar}` |\n'
        return md

    def _render_participants(self, stats):
        if not stats['participants']:
            return '*No participants yet.*'
        total = len(stats['participants'])
        md = f'**Total participants: {total}**\n\n'
        for p in stats['participants']:
            n = stats['players'][p]['total']
            md += f'[![@{p}](https://img.shields.io/badge/@{p}-{n}_moves-blue)](https://github.com/{p}) '
        return md

    # ------------------------------------------------------------------ #
    #  ユーティリティ                                                       #
    # ------------------------------------------------------------------ #
    def parse(self):
        t = self.issue_title
        if self.actor == self.admin_user:
            if re.search(r'reset.*(ox|tictactoe|tic)', t, re.I):  return 'ttt_reset',   None
            if re.search(r'reset.*(reversi|othello)',  t, re.I):  return 'rev_reset',   None
            if re.search(r'reset.*(guess)',            t, re.I):  return 'guess_reset', None
        m = re.match(r'Tic-Tac-Toe:\s*Put\s+([A-Ca-c][1-3])\s*$', t)
        if m: return 'ttt', m.group(1).upper()
        m = re.match(r'Reversi:\s*Put\s+([A-Ha-h][1-8])\s*$', t)
        if m: return 'rev', m.group(1).upper()
        m = re.match(r'Number\s+Guess:\s*(\d+)\s*$', t, re.I)
        if m: return 'guess', int(m.group(1))
        return None, None

    def _get_readme(self):
        obj = self.repo.get_contents('README.md')
        return obj, obj.decoded_content.decode('utf-8')

    def _section(self, content, name):
        m = re.search(rf'<!-- {name}_START -->(.*?)<!-- {name}_END -->', content, re.DOTALL)
        return m.group(1) if m else ''

    def _replace_section(self, content, name, new_body):
        return re.sub(
            rf'<!-- {name}_START -->.*?<!-- {name}_END -->',
            f'<!-- {name}_START -->\n{new_body}\n<!-- {name}_END -->',
            content, flags=re.DOTALL
        )

    def _update_readme(self, content, readme_obj):
        self.repo.update_file(
            'README.md',
            f'Update game by @{self.actor}',
            content, readme_obj.sha, branch='main'
        )

    def _apply_stats(self, content, include_current=False):
        """stats を集計して README の 3 セクションを差し替える。"""
        stats   = self._compute_stats(include_current=include_current)
        content = self._replace_section(content, 'LEADERBOARD',  self._render_leaderboard(stats))
        content = self._replace_section(content, 'GAME_STATS',   self._render_game_stats(stats))
        content = self._replace_section(content, 'PARTICIPANTS', self._render_participants(stats))
        return content

    # ------------------------------------------------------------------ #
    #  メイン処理                                                           #
    # ------------------------------------------------------------------ #
    def run(self):
        action, value = self.parse()

        if action is None:
            self.issue.create_comment(
                f'Unknown command: `{self.issue_title}`\n\n'
                'Expected formats:\n'
                '- `Tic-Tac-Toe: Put A1` (A1-C3)\n'
                '- `Reversi: Put D4` (A1-H8)\n'
                '- `Number Guess: 50` (1-100)'
            )
            self.issue.edit(state='closed')
            sys.exit(0)

        readme_obj, content = self._get_readme()
        result = None

        # --- リセット系（現在 issue は有効手でないので include_current=False）---
        if action == 'ttt_reset':
            state   = {'board': self.ttt._empty_board(), 'turn': self.ttt.X, 'log': []}
            content = self._replace_section(content, 'TICTACTOE', self.ttt.render(state, self.owner, self.repo_name))
            content = self._apply_stats(content, include_current=False)
            self._update_readme(content, readme_obj)
            self.issue.create_comment(f'Tic-Tac-Toe reset by @{self.actor}')
            self.issue.edit(state='closed')
            sys.exit(0)

        if action == 'rev_reset':
            state   = {'board': self.rev._empty_board(), 'turn': self.rev.BLACK, 'log': []}
            content = self._replace_section(content, 'REVERSI', self.rev.render(state, self.owner, self.repo_name))
            content = self._apply_stats(content, include_current=False)
            self._update_readme(content, readme_obj)
            self.issue.create_comment(f'Reversi reset by @{self.actor}')
            self.issue.edit(state='closed')
            sys.exit(0)

        if action == 'guess_reset':
            state   = {'number': None, 'attempts': [], 'solved': False}
            content = self._replace_section(content, 'GUESS', self.guess.render(state, self.owner, self.repo_name))
            content = self._apply_stats(content, include_current=False)
            self._update_readme(content, readme_obj)
            self.issue.create_comment(f'Number Guess reset by @{self.actor}')
            self.issue.edit(state='closed')
            sys.exit(0)

        # --- 有効手 ---
        if action == 'ttt':
            section = self._section(content, 'TICTACTOE')
            state   = self.ttt.parse_state(section)
            result  = self.ttt.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                sys.exit(0)
            content = self._replace_section(content, 'TICTACTOE', self.ttt.render(state, self.owner, self.repo_name))

        elif action == 'rev':
            section = self._section(content, 'REVERSI')
            state   = self.rev.parse_state(section)
            result  = self.rev.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                sys.exit(0)
            content = self._replace_section(content, 'REVERSI', self.rev.render(state, self.owner, self.repo_name))

        elif action == 'guess':
            section = self._section(content, 'GUESS')
            state   = self.guess.parse_state(section)
            result  = self.guess.place(state, value, self.actor)
            if not result['success']:
                self.issue.create_comment(result['message'])
                self.issue.edit(state='closed')
                sys.exit(0)
            content = self._replace_section(content, 'GUESS', self.guess.render(state, self.owner, self.repo_name))

        # 有効手の場合のみ include_current=True
        content = self._apply_stats(content, include_current=True)
        self._update_readme(content, readme_obj)
        self.issue.create_comment(result['message'])
        self.issue.edit(state='closed')
        sys.exit(0)


if __name__ == '__main__':
    GameManager().run()

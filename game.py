#!/usr/bin/env python3
import os
import re
import sys
import json
import urllib.request
from games.tictactoe import TicTacToe
from games.reversi import Reversi
from games.guess import NumberGuess

TTT_PAT   = re.compile(r'^Tic-Tac-Toe:\s*(?:Put|Move)\s+[A-Ca-c][1-3]\s*$')
REV_PAT   = re.compile(r'^Reversi:\s*Put\s+[A-Ha-h][1-8]\s*$')
GUESS_PAT = re.compile(r'^Number\s+Guess:\s*\d+\s*$', re.I)

# issue comment に含まれる勝利パターン
TTT_WIN_X   = re.compile(r'\u274c wins!')
TTT_WIN_O   = re.compile(r'\u2b55 wins!')
REV_WIN_B   = re.compile(r'Game over!.*\u26ab.*wins')
REV_WIN_W   = re.compile(r'Game over!.*\u26aa.*wins')

GRAPHQL_URL = 'https://api.github.com/graphql'


class GameManager:
    def __init__(self):
        self.token       = os.environ['GITHUB_TOKEN']
        self.repo_full   = os.environ['REPO']           # owner/repo
        self.issue_num   = int(os.environ['ISSUE_NUMBER'])
        self.actor       = os.environ['ACTOR']
        self.issue_title = os.environ.get('ISSUE_TITLE', '').strip()
        self.admin_user  = 'tadanobutubutu'
        self.owner, self.repo_name = self.repo_full.split('/')
        self._current_result_message = ''

        # PyGithub は REST 操作のみに使用
        from github import Github
        self._gh   = Github(self.token)
        self._repo = self._gh.get_repo(self.repo_full)
        self._issue = self._repo.get_issue(self.issue_num)

        self.ttt   = TicTacToe()
        self.rev   = Reversi()
        self.guess = NumberGuess()

    # ------------------------------------------------------------------ #
    #  GraphQL ヘルパー                                                    #
    # ------------------------------------------------------------------ #
    def _graphql(self, query, variables=None):
        payload = json.dumps({'query': query, 'variables': variables or {}}).encode()
        req = urllib.request.Request(
            GRAPHQL_URL,
            data=payload,
            headers={
                'Authorization': f'bearer {self.token}',
                'Content-Type': 'application/json',
            }
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    # ------------------------------------------------------------------ #
    #  GraphQL で closed issues を一括取得（タイトル + 作成者 + コメント） #
    # ------------------------------------------------------------------ #
    def _fetch_closed_issues(self):
        """
        全ての closed issue の (number, title, login, comments[body]) を返す。
        GraphQL でページネーションしながら一括取得。
        """
        query = """
        query($owner:String!, $repo:String!, $after:String) {
          repository(owner:$owner, name:$repo) {
            issues(states:CLOSED, first:100, after:$after,
                   orderBy:{field:CREATED_AT, direction:ASC}) {
              pageInfo { hasNextPage endCursor }
              nodes {
                number
                title
                author { login }
                comments(first:5) {
                  nodes { body }
                }
              }
            }
          }
        }
        """
        issues = []
        cursor = None
        while True:
            data = self._graphql(query, {
                'owner': self.owner,
                'repo':  self.repo_name,
                'after': cursor
            })
            conn = data['data']['repository']['issues']
            issues.extend(conn['nodes'])
            if not conn['pageInfo']['hasNextPage']:
                break
            cursor = conn['pageInfo']['endCursor']
        return issues

    # ------------------------------------------------------------------ #
    #  勝利パターン判定                                                    #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _detect_win(comments):
        """コメントのリストから (winner_key or None) を返す"""
        for c in comments:
            body = c.get('body', '')
            if TTT_WIN_X.search(body):  return 'ttt_x'
            if TTT_WIN_O.search(body):  return 'ttt_o'
            if REV_WIN_B.search(body):  return 'rev_black'
            if REV_WIN_W.search(body):  return 'rev_white'
        return None

    @staticmethod
    def _detect_win_from_message(message):
        """result['message'] 文字列から直接勝利キーを返す"""
        if TTT_WIN_X.search(message):  return 'ttt_x'
        if TTT_WIN_O.search(message):  return 'ttt_o'
        if REV_WIN_B.search(message):  return 'rev_black'
        if REV_WIN_W.search(message):  return 'rev_white'
        return None

    # ------------------------------------------------------------------ #
    #  集計（GraphQL データから）                                        #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _title_to_type(title):
        if TTT_PAT.match(title):   return 'tictactoe'
        if REV_PAT.match(title):   return 'reversi'
        if GUESS_PAT.match(title): return 'guess'
        return None

    @staticmethod
    def _add_count(players, games, login, gtype):
        if login not in players:
            players[login] = {
                'total': 0, 'tictactoe': 0, 'reversi': 0, 'guess': 0,
                'ttt_wins_x': 0, 'ttt_wins_o': 0,
                'rev_wins_black': 0, 'rev_wins_white': 0,
            }
        players[login]['total'] += 1
        players[login][gtype]   += 1
        games[gtype]            += 1

    def _compute_stats(self, include_current=False):
        players = {}
        games   = {'tictactoe': 0, 'reversi': 0, 'guess': 0}
        wins    = {'ttt_x': 0, 'ttt_o': 0, 'rev_black': 0, 'rev_white': 0}

        # 現在処理中 issue の先行カウント（有効手の場合のみ）
        if include_current:
            gtype = self._title_to_type(self.issue_title)
            if gtype:
                self._add_count(players, games, self.actor, gtype)

        closed = self._fetch_closed_issues()
        for issue in closed:
            if issue['number'] == self.issue_num:
                continue
            title  = (issue.get('title') or '').strip()
            login  = (issue.get('author') or {}).get('login') or 'ghost'
            comments = [c for c in (issue.get('comments') or {}).get('nodes', [])]

            gtype = self._title_to_type(title)
            if gtype:
                self._add_count(players, games, login, gtype)

            # 勝利記録：コメントから検出
            win = self._detect_win(comments)
            if win:
                wins[win] += 1
                # 最後に手を打ったプレイヤーに勝利を記録
                if gtype and login in players:
                    key_map = {
                        'ttt_x':     'ttt_wins_x',
                        'ttt_o':     'ttt_wins_o',
                        'rev_black': 'rev_wins_black',
                        'rev_white': 'rev_wins_white',
                    }
                    players[login][key_map[win]] += 1

        # 現在 issue の勝利も先行反映（include_current時）
        # result['message'] を使って直接判定する
        if include_current and self._current_result_message:
            win = self._detect_win_from_message(self._current_result_message)
            if win:
                wins[win] += 1
                key_map = {
                    'ttt_x':     'ttt_wins_x',
                    'ttt_o':     'ttt_wins_o',
                    'rev_black': 'rev_wins_black',
                    'rev_white': 'rev_wins_white',
                }
                if self.actor in players:
                    players[self.actor][key_map[win]] += 1

        participants = sorted(players.keys(),
                              key=lambda p: players[p]['total'], reverse=True)
        return {'players': players, 'participants': participants,
                'games': games, 'wins': wins}

    # ------------------------------------------------------------------ #
    #  レンダリング                                                         #
    # ------------------------------------------------------------------ #
    def _render_leaderboard(self, stats):
        top = sorted(stats['players'].items(),
                     key=lambda x: x[1]['total'], reverse=True)[:10]
        if not top:
            return '*No players yet. Be the first!*'
        md  = '| Rank | Player | Total | TTT | Reversi | Guess | ❌W | ⭕W | ⚫W | ⚪W |\n'
        md += '|:----:|--------|:-----:|:---:|:-------:|:-----:|:---:|:---:|:---:|:---:|\n'
        for i, (player, s) in enumerate(top, 1):
            rank = ['1st', '2nd', '3rd'][i-1] if i <= 3 else f'{i}th'
            md += (f'| {rank} | [@{player}](https://github.com/{player}) '
                   f'| {s["total"]} | {s["tictactoe"]} | {s["reversi"]} | {s["guess"]} '
                   f'| {s["ttt_wins_x"]} | {s["ttt_wins_o"]} '
                   f'| {s["rev_wins_black"]} | {s["rev_wins_white"]} |\n')
        # 右下に総勝利数
        w = stats['wins']
        md += f'\n**Game wins — ❌: {w["ttt_x"]} ⭕: {w["ttt_o"]} ⚫: {w["rev_black"]} ⚪: {w["rev_white"]}**\n'
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
        obj = self._repo.get_contents('README.md')
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
        self._repo.update_file(
            'README.md',
            f'Update game by @{self.actor}',
            content, readme_obj.sha, branch='main'
        )

    def _apply_stats(self, content, include_current=False):
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
            self._issue.create_comment(
                f'Unknown command: `{self.issue_title}`\n\n'
                'Expected formats:\n'
                '- `Tic-Tac-Toe: Put A1` (A1-C3)\n'
                '- `Reversi: Put D4` (A1-H8)\n'
                '- `Number Guess: 50` (1-100)'
            )
            self._issue.edit(state='closed')
            sys.exit(0)

        readme_obj, content = self._get_readme()
        result = None

        if action == 'ttt_reset':
            state   = {'board': self.ttt._empty_board(), 'turn': self.ttt.X, 'log': []}
            content = self._replace_section(content, 'TICTACTOE', self.ttt.render(state, self.owner, self.repo_name))
            content = self._apply_stats(content, include_current=False)
            self._update_readme(content, readme_obj)
            self._issue.create_comment(f'Tic-Tac-Toe reset by @{self.actor}')
            self._issue.edit(state='closed')
            sys.exit(0)

        if action == 'rev_reset':
            state   = {'board': self.rev._empty_board(), 'turn': self.rev.BLACK, 'log': []}
            content = self._replace_section(content, 'REVERSI', self.rev.render(state, self.owner, self.repo_name))
            content = self._apply_stats(content, include_current=False)
            self._update_readme(content, readme_obj)
            self._issue.create_comment(f'Reversi reset by @{self.actor}')
            self._issue.edit(state='closed')
            sys.exit(0)

        if action == 'guess_reset':
            state   = {'number': None, 'attempts': [], 'solved': False}
            content = self._replace_section(content, 'GUESS', self.guess.render(state, self.owner, self.repo_name))
            content = self._apply_stats(content, include_current=False)
            self._update_readme(content, readme_obj)
            self._issue.create_comment(f'Number Guess reset by @{self.actor}')
            self._issue.edit(state='closed')
            sys.exit(0)

        if action == 'ttt':
            section = self._section(content, 'TICTACTOE')
            state   = self.ttt.parse_state(section)
            result  = self.ttt.place(state, value, self.actor)
            if not result['success']:
                self._issue.create_comment(result['message'])
                self._issue.edit(state='closed')
                sys.exit(0)
            content = self._replace_section(content, 'TICTACTOE', self.ttt.render(state, self.owner, self.repo_name))

        elif action == 'rev':
            section = self._section(content, 'REVERSI')
            state   = self.rev.parse_state(section)
            result  = self.rev.place(state, value, self.actor)
            if not result['success']:
                self._issue.create_comment(result['message'])
                self._issue.edit(state='closed')
                sys.exit(0)
            content = self._replace_section(content, 'REVERSI', self.rev.render(state, self.owner, self.repo_name))

        elif action == 'guess':
            section = self._section(content, 'GUESS')
            state   = self.guess.parse_state(section)
            result  = self.guess.place(state, value, self.actor)
            if not result['success']:
                self._issue.create_comment(result['message'])
                self._issue.edit(state='closed')
                sys.exit(0)
            content = self._replace_section(content, 'GUESS', self.guess.render(state, self.owner, self.repo_name))

        # result['message'] を保存してから stats に反映
        self._current_result_message = result['message']
        content = self._apply_stats(content, include_current=True)
        self._update_readme(content, readme_obj)
        self._issue.create_comment(result['message'])
        self._issue.edit(state='closed')
        sys.exit(0)


if __name__ == '__main__':
    GameManager().run()

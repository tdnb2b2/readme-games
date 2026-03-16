class TicTacToe:
    def __init__(self):
        self.size = 3
        self.symbols = {'X': '❌', 'O': '⭕', None: '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'}
        self.img_x = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/274c.svg'
        self.img_o = 'https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/2b55.svg'
        self.issue_number = 1

    def set_issue_number(self, num):
        self.issue_number = num

    def create_board(self):
        return [[None for _ in range(self.size)] for _ in range(self.size)]

    def make_move(self, state, move, player):
        if move == 'start':
            state['board'] = self.create_board()
            state['turn'] = 'X'
            state['moves'] = []
            return {'success': True, 'message': f'🎮 New Tic-Tac-Toe game started by @{player}! {self.symbols["X"]} goes first.'}

        if not state['board']:
            state['board'] = self.create_board()
            state['turn'] = 'X'
            state['moves'] = []

        if len(move) != 2:
            return {'success': False, 'message': 'Invalid format. Use A1-C3 (e.g., B2)'}

        col = ord(move[0]) - ord('A')
        row = int(move[1]) - 1

        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return {'success': False, 'message': 'Position out of bounds'}

        if state['board'][row][col] is not None:
            return {'success': False, 'message': f'❌ Position {move} is already taken! Choose an empty square.'}

        # コマを配置
        state['board'][row][col] = state['turn']
        state['moves'].append({'player': player, 'move': move, 'symbol': state['turn']})

        # 勝利判定
        winner = self.check_winner(state['board'])
        if winner:
            msg = f'🏆 **{self.symbols[winner]} WINS!** Game over.\n'
            msg += f'Winning move: {move} by @{player}\n'
            msg += f'Click any square to start a new game!'
            state['board'] = None
            state['turn'] = 'X'
            state['moves'] = []
            return {'success': True, 'message': msg}

        # 引き分け判定
        if self.is_full(state['board']):
            msg = f'🤝 **DRAW!** The board is full.\n'
            msg += f'Last move: {move} by @{player}\n'
            msg += f'Click any square to start a new game!'
            state['board'] = None
            state['turn'] = 'X'
            state['moves'] = []
            return {'success': True, 'message': msg}

        # 次のターンに切り替え
        state['turn'] = 'O' if state['turn'] == 'X' else 'X'
        return {'success': True, 'message': f'✅ {self.symbols[state["turn"]]} placed at {move} by @{player}.\nNext turn: {self.symbols[state["turn"]]}'}

    def check_winner(self, board):
        # 横のラインをチェック
        for i in range(self.size):
            if board[i][0] and board[i][0] == board[i][1] == board[i][2]:
                return board[i][0]
        
        # 縦のラインをチェック
        for i in range(self.size):
            if board[0][i] and board[0][i] == board[1][i] == board[2][i]:
                return board[0][i]
        
        # 左上から右下の斜めライン
        if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
            return board[0][0]
        
        # 右上から左下の斜めライン
        if board[0][2] and board[0][2] == board[1][1] == board[2][0]:
            return board[0][2]
        
        return None

    def is_full(self, board):
        return all(cell is not None for row in board for cell in row)

    def render(self, state, owner='tdnb2b2', repo='readme-games'):
        board = state['board'] if state['board'] else self.create_board()
        is_active = state['board'] is not None

        if is_active:
            md = f"\n**Current turn:** {self.symbols[state['turn']]}\n\n"
        else:
            md = "\n"

        md += "|   | **A** | **B** | **C** |   |\n"
        md += "|---|:-----:|:-----:|:-----:|:-:|\n"

        for i in range(self.size):
            md += f"| **{i+1}** | "
            for j in range(self.size):
                cell = board[i][j]
                position = f"{chr(65+j)}{i+1}"
                
                if cell is None:
                    # 空のマスはリンクを表示
                    title = f"Tic-Tac-Toe:+Move+{position}"
                    body = "Please+do+not+change+the+title.+Just+click+%22Submit+new+issue%22.+You+don%27t+need+to+do+anything+else+:D"
                    link = f"https://github.com/{owner}/{repo}/issues/new?title={title}&body={body}"
                    md += f"[{self.symbols[None]}]({link})"
                elif cell == 'X':
                    # Xのコマは画像を表示（リンクなし）
                    md += f"<img src=\"{self.img_x}\" width=40px>"
                else:
                    # Oのコマは画像を表示（リンクなし）
                    md += f"<img src=\"{self.img_o}\" width=40px>"
                md += " | "
            md += f"**{i+1}** |\n"

        md += "|   | **A** | **B** | **C** |   |\n"

        if not is_active:
            md += "\nClick any square to start!\n"
        else:
            # 空いているマスだけをリンク表示
            empty = []
            for i in range(self.size):
                for j in range(self.size):
                    if board[i][j] is None:
                        pos = f"{chr(65+j)}{i+1}"
                        title = f"Tic-Tac-Toe:+Move+{pos}"
                        body = "Please+do+not+change+the+title.+Just+click+%22Submit+new+issue%22.+You+don%27t+need+to+do+anything+else+:D"
                        link = f"https://github.com/{owner}/{repo}/issues/new?title={title}&body={link}"
                        empty.append(f"[{pos}]({link})")
            
            if empty:
                md += "\n**Available moves:** " + " · ".join(empty) + "\n"

            if state['moves']:
                md += "\n<details>\n  <summary>Move history</summary>\n\n"
                md += "| Move | Symbol | Player |\n| :--: | :----: | :----- |\n"
                for m in state['moves']:
                    md += f"| `{m['move']}` | {self.symbols[m['symbol']]} | [@{m['player']}](https://github.com/{m['player']}) |\n"
                md += "\n</details>\n"

        return md

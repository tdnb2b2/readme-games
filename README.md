# 🎮 README Games Arena

> Play multiple simple games directly in this README! Powered by GitHub Actions for instant response.
> **📱 Fully mobile-friendly** - works perfectly on GitHub Mobile app!

[![Game Action](https://github.com/tdnb2b2/readme-games/actions/workflows/game-action.yml/badge.svg)](https://github.com/tdnb2b2/readme-games/actions/workflows/game-action.yml)

## 🚀 Quick Start

### 🖥️ Desktop: Click on the board!
1. **Choose a game** below
2. **Click any empty square** on the game board
3. **Press "Comment"** button
4. **Done!** GitHub Actions updates everything instantly

### 📱 Mobile: Works in GitHub app!
1. **Open this README** in GitHub Mobile
2. **Tap any empty square** on the game board
3. **Comment form opens** (stays in GitHub app - no browser redirect!)
4. **Tap "Comment"** and you're done!

**🎉 When you play your first move:**
- ✅ Your name appears in the **participants list**
- ✅ You're added to the **leaderboard**
- ✅ You're **invited as a read-only collaborator** (automatically!)
- ✅ This repo appears in **your GitHub profile**

---

## 🎯 Available Games

### ❌⭕ Tic-Tac-Toe (3x3)

<!-- TICTACTOE_START -->
*No active game. Start with: `start ttt` or `start tictactoe`*
<!-- TICTACTOE_END -->

**🎮 Game Arena:** [Issue #1 - Tic-Tac-Toe](https://github.com/tdnb2b2/readme-games/issues/1) | [Start New Game](https://github.com/tdnb2b2/readme-games/issues/1/comments/new?body=start%20ttt)

---

### ⚫⚪ Reversi / Othello (8x8)

<!-- REVERSI_START -->
*No active game. Start with: `start reversi`*
<!-- REVERSI_END -->

**🎮 Game Arena:** [Issue #2 - Reversi](https://github.com/tdnb2b2/readme-games/issues/2) | [Start New Game](https://github.com/tdnb2b2/readme-games/issues/2/comments/new?body=start%20reversi)

---

### 🔢 Number Guessing Game (1-100)

<!-- GUESS_START -->
*No active game. Start with: `start guess` or `start number`*
<!-- GUESS_END -->

**🎮 Game Arena:** [Issue #3 - Number Guess](https://github.com/tdnb2b2/readme-games/issues/3) | [Start New Game](https://github.com/tdnb2b2/readme-games/issues/3/comments/new?body=start%20guess)

---

## 🏆 Leaderboard - Top 10 Players

<!-- LEADERBOARD_START -->
*まだプレイヤーがいません。最初のプレイヤーになろう！*
<!-- LEADERBOARD_END -->

---

## 👥 Game Participants

このゲームに参加してくれた全てのプレイヤー:

<!-- PARTICIPANTS_START -->
*まだ参加者がいません。最初の参加者になろう！*
<!-- PARTICIPANTS_END -->

---

## 🔑 Read-Only Collaborator System

**🎉 初回プレイ時に自動でCollaborator招待！**

ゲームを初めてプレイすると、自動的に以下が実行されます：

✅ **Read-Only権限で招待** - `pull` permission (読み取り専用)
✅ **プロフィールに表示** - あなたのGitHubプロフィールにこのリポジトリが表示される
✅ **安全** - 書き込み権限なし、読み取りのみ
✅ **自動** - 手動操作不要

**権限詳細:**
- ✅ リポジトリの閲覧
- ✅ Issueへのコメント
- ✅ フォーク作成
- ❌ コードの編集・プッシュは不可
- ❌ 設定変更は不可

**招待の確認方法:**
1. GitHubのプロフィールを開く
2. **Organizations** または **Repositories** タブを確認
3. `tdnb2b2/readme-games` が表示される

---

## 📱 Mobile-Friendly Design

**GitHub Mobileで完全に動作！**

✅ **アプリ内で完結** - 外部ブラウザに飛ばない！
✅ **ワンタップでプレイ** - ボードをタップするだけ
✅ **自動入力** - コメントが自動で入力される
✅ **超高速** - 10-15秒で反応

**marcizhuのチェスゲームと違い:**
- ⛔ marcizhu: リンククリック→Chromeにリダイレクト (モバイルで不便)
- ✅ README Games: GitHubアプリ内で完結！(モバイル完全対応)

---

## 📖 How It Works

1. **ボードをクリック** - 空いているマスを選ぶ
2. **GitHub Actionsが発動** - 自動的にワークフロー実行
3. **ゲームロジック処理** - 移動を検証・実行
4. **Collaborator招待** - 初回プレイ時にRead-Onlyで招待
5. **README更新** - ゲーム状態とリーダーボードが更新
6. **参加者リスト追加** - あなたの名前が追加される

### Performance Optimizations ⚡

- **Minimal dependencies**: Only PyGithub for API calls
- **Efficient state management**: Single JSON file for all game data
- **Pip caching**: Dependencies cached for faster workflow runs
- **Optimized Python**: No unnecessary imports or computations
- **Direct README updates**: No external rendering services
- **Lightweight games**: Simple logic, maximum speed
- **Clickable boards**: HTML tables with direct comment links
- **Smart invitations**: Only invites first-time players

## 🎮 Game Commands

| Game | Start Command | Move Format | Example | Game Arena |
|------|---------------|-------------|----------|------------|
| Tic-Tac-Toe | `start ttt` | `[A-C][1-3]` | `B2`, `A1`, `C3` | [Issue #1](https://github.com/tdnb2b2/readme-games/issues/1) |
| Reversi | `start reversi` | `[A-H][1-8]` | `D3`, `E6`, `F5` | [Issue #2](https://github.com/tdnb2b2/readme-games/issues/2) |
| Number Guess | `start guess` | `[1-100]` | `50`, `75`, `42` | [Issue #3](https://github.com/tdnb2b2/readme-games/issues/3) |

**📝 Direct Comment:** 直接Issueにコメントすることもできます！

## 🔧 Technical Stack

- **Trigger**: GitHub Actions (on issue comments)
- **Runtime**: Python 3.11 (fastest Python version)
- **API**: PyGithub (official GitHub API wrapper)
- **Storage**: Single JSON file (ultra-fast read/write)
- **UI**: HTML tables with direct comment links (mobile-optimized)
- **Permissions**: Automatic read-only collaborator invitations
- **Deployment**: Instant (no build step)

## 🤝 Contributing

Play any game to become a participant! Want to add more games?

1. Fork this repository
2. Add your game in `games/yourgame.py`
3. Update `game.py` to register it
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📜 Inspiration

Inspired by [@marcizhu's amazing chess README game](https://github.com/marcizhu/marcizhu) and the GitHub Actions community.

**Improvements over marcizhu's chess:**
- ✅ Mobile-friendly (stays in GitHub app)
- ✅ Multiple games support
- ✅ Leaderboard & participants tracking
- ✅ Automatic read-only collaborator invitations
- ✅ Organization-based (better permission management)

## 📄 License

MIT License - Feel free to fork and create your own game!

---

**Made with ❤️ using GitHub Actions** | [View Workflow](https://github.com/tdnb2b2/readme-games/blob/main/.github/workflows/game-action.yml) | [Source Code](https://github.com/tdnb2b2/readme-games)

# 🎮 README Games Arena

> Play multiple simple games directly in this README! Powered by GitHub Actions for instant response.

[![Game Action](https://github.com/tadanobutubutu/readme-games/actions/workflows/game-action.yml/badge.svg)](https://github.com/tadanobutubutu/readme-games/actions/workflows/game-action.yml)

## 🚀 Quick Start

1. **Choose a game** below
2. **Click "New Issue"** or comment on existing game issue
3. **Make your move** by commenting the position/number
4. **Your name appears in the participants list!**

## 🎯 Available Games

### ❌⭕ Tic-Tac-Toe (3x3)

<!-- TICTACTOE_START -->
*No active game. Start with: `start ttt` or `start tictactoe`*
<!-- TICTACTOE_END -->

**Start new game:** [Click here to start Tic-Tac-Toe](https://github.com/tadanobutubutu/readme-games/issues/new?title=Tic-Tac-Toe&body=start%20ttt)

---

### ⚫⚪ Reversi / Othello (8x8)

<!-- REVERSI_START -->
*No active game. Start with: `start reversi`*
<!-- REVERSI_END -->

**Start new game:** [Click here to start Reversi](https://github.com/tadanobutubutu/readme-games/issues/new?title=Reversi&body=start%20reversi)

---

### 🔢 Number Guessing Game (1-100)

<!-- GUESS_START -->
*No active game. Start with: `start guess` or `start number`*
<!-- GUESS_END -->

**Start new game:** [Click here to start Number Guess](https://github.com/tadanobutubutu/readme-games/issues/new?title=Number%20Guess&body=start%20guess)

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

## 📖 How It Works

1. When you **comment on an issue** with a move (e.g., `A1`, `D3`, `50`)
2. **GitHub Actions is triggered** instantly
3. The system **validates and executes** your move
4. **README is updated** with the new game state
5. Your **name is added to the participants list**

### Performance Optimizations ⚡

- **Minimal dependencies**: Only PyGithub for API calls
- **Efficient state management**: Single JSON file for all game data
- **Pip caching**: Dependencies cached for faster workflow runs
- **Optimized Python**: No unnecessary imports or computations
- **Direct README updates**: No external rendering services
- **Lightweight games**: Simple logic, maximum speed

## 🎮 Game Commands

| Game | Start Command | Move Format | Example |
|------|---------------|-------------|----------|
| Tic-Tac-Toe | `start ttt` | `[A-C][1-3]` | `B2`, `A1`, `C3` |
| Reversi | `start reversi` | `[A-H][1-8]` | `D3`, `E6`, `F5` |
| Number Guess | `start guess` | `[1-100]` | `50`, `75`, `guess 42` |

## 🔧 Technical Stack

- **Trigger**: GitHub Actions (on issue comments)
- **Runtime**: Python 3.11 (fastest Python version)
- **API**: PyGithub (official GitHub API wrapper)
- **Storage**: Single JSON file (ultra-fast read/write)
- **Deployment**: Instant (no build step)

## 🤝 Contributing

Play any game to become a participant! Want to add more games?

1. Fork this repository
2. Add your game in `games/yourgame.py`
3. Update `game.py` to register it
4. Submit a pull request

## 📜 Inspiration

Inspired by [@marcizhu's amazing chess README game](https://github.com/marcizhu) and the GitHub Actions community.

## 📄 License

MIT License - Feel free to fork and create your own game!

---

**Made with ❤️ using GitHub Actions** | [View Workflow](https://github.com/tadanobutubutu/readme-games/blob/main/.github/workflows/game-action.yml) | [Source Code](https://github.com/tadanobutubutu/readme-games)

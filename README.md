# 🤖 Gemini Discord Search Bot

Gemini 2.0 Flash を使用したWEB検索専用のDiscord botです。チャンネル内の会話を監視し、自動的にWEB検索を実行して回答を提供します。

## 🌟 機能

- **自動WEB検索**: 指定されたチャンネルでのメッセージを監視し、自動的に関連する検索を実行
- **会話メモリ**: 過去の会話を記憶し、文脈を考慮した回答を提供
- **手動検索**: コマンドを使用した手動検索
- **ログ取得**: 日付指定でのチャット履歴取得
- **チャンネル監視管理**: 特定チャンネルでの自動検索のオン/オフ切り替え

## 📋 コマンド

### 基本コマンド
- `!search <検索クエリ>` - 手動でWEB検索を実行
- `!help` - ヘルプメッセージを表示

### ログ取得コマンド
- `!logs` - 今日のログを取得
- `!logs yesterday` - 昨日のログを取得
- `!logs 2024-01-15` - 指定日のログを取得 (YYYY-MM-DD形式)
- `!logs 7days` - 過去7日間のログを取得

### 管理コマンド (チャンネル管理権限必要)
- `!monitor status` - 現在のチャンネルの監視状態を確認
- `!monitor on` - 現在のチャンネルで自動検索を有効化
- `!monitor off` - 現在のチャンネルで自動検索を無効化

## 🚀 セットアップ

### 1. 必要な環境
- Python 3.8以上
- Discord Bot Token
- Google Gemini API Key

### 2. インストール

```bash
# リポジトリをクローン
git clone <your-repo-url>
cd gemini-discord-search-bot

# 依存関係をインストール
pip install -r requirements.txt
```

### 3. 環境設定

`.env` ファイルを作成し、以下の情報を設定：

```env
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
CHANNEL_ID=your_default_channel_id_here
```

### 4. Discord Bot の作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 新しいアプリケーションを作成
3. Bot セクションでbot tokenを取得
4. OAuth2 > URL Generator で以下の権限を選択：
   - `bot`
   - `Send Messages`
   - `Read Message History`
   - `Use Slash Commands`
   - `Embed Links`

### 5. Gemini API Key の取得

1. [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
2. API Keyを作成・取得

### 6. 実行

```bash
python discord_bot.py
```

## 🛠️ ファイル構成

```
gemini-discord-search-bot/
├── discord_bot.py          # メインのDiscord botファイル
├── gemini_search.py        # Gemini API統合とWEB検索機能
├── conversation_memory.py  # 会話履歴管理
├── requirements.txt        # Python依存関係
├── .env.example           # 環境変数テンプレート
└── README.md              # このファイル
```

## 💡 使用方法

### 自動検索
指定されたチャンネルで10文字以上のメッセージを投稿すると、自動的にWEB検索が実行され、関連する情報を含む回答が返されます。

### 手動検索
```
!search Pythonの最新バージョン
```

### ログ取得例
```
!logs                    # 今日のログ
!logs yesterday          # 昨日のログ
!logs 2024-01-15        # 2024年1月15日のログ
!logs 30days            # 過去30日間のログ
```

## 🔧 カスタマイズ

### 検索動作の調整
`gemini_search.py` の以下のパラメータを調整できます：
- `temperature`: 応答の創造性 (0.0-1.0)
- `max_output_tokens`: 最大出力トークン数
- 文脈保持期間 (デフォルト: 24時間)

### データベース管理
会話履歴は SQLite データベース (`conversation_memory.db`) に保存されます。
古い履歴は自動的にクリーンアップされます (デフォルト: 30日)。

## ⚠️ 注意事項

- Gemini API の使用量制限に注意してください
- Discord API の rate limit に注意してください
- 機密情報を含む会話は記録されるため、プライベートチャンネルでの使用を推奨します

## 🐛 トラブルシューティング

### よくある問題

1. **Bot が応答しない**
   - Discord Token が正しく設定されているか確認
   - Bot に必要な権限が付与されているか確認

2. **検索が動作しない**
   - Gemini API Key が正しく設定されているか確認
   - API 使用量制限に達していないか確認

3. **ログが取得できない**
   - データベースファイルのアクセス権限を確認
   - 指定した日付形式が正しいか確認

## 📄 ライセンス

MIT License

## 🤝 貢献

バグ報告や機能要求は GitHub Issues でお願いします。
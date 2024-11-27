# Web Scraping

このプロジェクトは、SUUMO の賃貸物件と中古マンションのサイトから情報をスクレイピングして取得するものです。主に以下の情報を収集します：

- **建物名** (title)
- **住所** (address)
- **アクセス** (access)
- **築年数** (age)
- **階数** (floor)
- **家賃** (fee)
- **管理費** (management_fee)
- **敷金** (deposit)
- **礼金** (gratuity)
- **間取り** (madori)
- **面積** (menseki)
- **構造** (structure)
- **総階数** (floors)
- **築年数** (year)
- **総戸数** (numbers)

## スクリプト

1. **`scraping-chintai.py`** - 賃貸物件のスクレイピング
2. **`scraping-used-apartment.py`** - 中古マンションのスクレイピング

### 機能

- 賃貸物件と中古マンションのサイトに掲載されている物件情報を取得します。
- 家賃、築年数といった基本的な情報を抽出し、各物件の詳細リンクにアクセスします。
- 詳細リンク先で、総戸数などの追加の詳細情報を取得します。

## 使用方法

1. 必要なライブラリをインストールします。

   ```bash
   pip install requests beautifulsoup4 pandas

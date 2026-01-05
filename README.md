# Stripe Payment Element を用いた書籍購入アプリケーション（Take-Home Project）

## 概要

本リポジトリは、Stripe の Take-Home 課題として提供されたシンプルな書籍購入アプリケーションに対し、**Stripe Payment Element を用いた決済機能を統合**した実装です。

ユーザーは以下の操作を行うことができます。

- 購入する書籍を選択
- メールアドレスを入力
- Stripe Payment Element を用いて支払い
- 購入完了画面で以下を確認
  - 請求総額（通貨フォーマット済み）
  - Stripe Payment Intent ID（`pi_` で始まる）

本実装では **Stripe Checkout は使用せず**、Stripe が推奨する **Payment Intent + Payment Element** による構成を採用しています。

---

## デモの決済フロー（全体像）

Stripe Payment Elementを用いた決済機能の全体フローは以下となります。

1. PaymentIntent 作成
2. Payment Element 表示
3. confirmPayment
4. 完了画面

決済フローの詳細手順は「アーキテクチャと設計方針」に記載しています。

---

## 技術スタック

- Python 3
- Flask
- Stripe Python SDK
- Stripe.js v3
- Stripe Payment Element
- Vanilla JavaScript
- HTML / CSS

---

## セットアップ方法

### 1. リポジトリの取得

```bash
git clone https://github.com/kenakaga/sa-takehome-project-stripe.git
cd sa-takehome-project-stripe
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. Stripeアカウントの作成
Stripeのアカウントを以下URLから作成します。

- Create your Stripe account
https://dashboard.stripe.com/register

### 4. 環境変数の設定
`.env` ファイルを作成し、Stripe の API キーを設定します。
```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```
※ Secret Key はサーバー側のみで使用し、クライアントには Publishable Key のみを渡しています。

StripeのAPIキーはStripe Dashboardより確認します。
![api key](/image/api_key.jpg)
*(例) Stripe DashboardのAPI Keys*

※ 本デモではSandboxアカウントのAPIキーを使用します。

### 5. アプリケーション起動
以下コマンドによりFlaskのアプリケーションを起動します。
```bash
flask run -p 4242
```
ブラウザで以下にアクセスします。
```bash
http://localhost:4242
```
以上、セットアップは完了です。

## アーキテクチャと設計方針

### 決済フローの詳細

![transaction flow](/image/transaction_flow.jpg)
*決済フロー図　※引用元 (https://docs.stripe.com/payments/accept-a-payment?platform=web&ui=elements#web-create-intent)*

**決済フローの詳細手順**
1. ユーザーが書籍を選択
2. サーバー側（Flask）で商品 ID を元に金額を確定
3. `/create-payment-intent` にて PaymentIntent を作成
    - 金額は **必ずサーバー側で計算**
4. クライアントに `client_secret` を返却
5. Stripe Payment Element を表示
    - ユーザーはemailアドレスを入力
6. `stripe.confirmPayment()` により支払い確定
7. 完了画面にリダイレクト(`return_url`)
8. 完了画面で PaymentIntent を取得し、結果を表示

※ 本デモでは決済後のサーバーのその他の処理は不要な前提のため未実装

### 使用している Stripe API / 機能
- `stripe.PaymentIntent.create`
- `stripe.PaymentIntent.retrieve`
- `stripe.confirmPayment`
- Stripe Payment Element
- Link Authentication Element

### 問題へのアプローチと設計判断
#### 元リポジトリを極力変更しない方針
- 既存の UI / 商品選択ロジックは尊重
- 決済に必要な最小限のコードのみを追加
- 既存の `/checkout` バリデーションを活用

#### セキュリティを考慮した設計
- 金額はクライアントから受け取らず、サーバーで確定
- `.env` はサーバー側のみで使用
- Publishable Key のみを HTML 経由でクライアントに渡す
- Secret Key はクライアントに露出させない

#### 金額と通貨の扱い
- Stripe の `amount` は 最小通貨単位で返却されるため、
通貨に応じて表示ロジックを分ける仕組みを追加
    - USD / EUR など：`amount / 100` → `$23.00`
    - JPY（ゼロディシマル通貨）：そのまま表示 → `¥2,300`
- 通貨記号は USD($) / JPY(¥) / EUR(€) に対応

### 参照したドキュメント
- Stripe DOCS – Accept a payment (Advanced integration)
https://docs.stripe.com/payments/accept-a-payment?platform=web&ui=elements

- Stripe DOCS – Payment Element Quickstart
https://docs.stripe.com/payments/quickstart

- Stripe DOCS – Link Authentication Element
https://docs.stripe.com/payments/elements/link-authentication-element

- Stripe DOCS - Compare features and availability
https://docs.stripe.com/payments/online-payments#compare-features-and-availability

- Stripe API - Payment Intents
https://docs.stripe.com/api/payment_intents

### 今後の拡張案（より堅牢な構成にする場合）
- Webhook の追加
    - `payment_intent.succeeded` を受信し、注文確定を非同期で処理
    - 完了画面は UX、Webhook を正の情報源にする
- Stripe Customer の永続化
    - email と支払い履歴を顧客単位で管理
- 複数商品（カート）対応
- Apple Pay / Google Pay の有効化
- 通貨の
- 本番環境向けのエラーハンドリング・ロギング強化

### まとめ
本アプリケーションは、
Stripe が推奨する Payment Intent + Payment Element を用いた**シンプルかつ安全な決済フロー**を実装しています。

既存コードを尊重しながら、実運用を見据えた拡張が可能な構成を意識しました。
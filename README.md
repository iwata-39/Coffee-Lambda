# Coffee-Lambda
コーヒーショップのオンラインサイトから新商品の発売をLINEに通知するスクリプトです。  
Onibus Coffee / Rec Coffee / Leaves Coffeeの3つのショップに対応しています。  
LINE通知は、毎週月曜と木曜のいずれかで新商品が発売された場合に実行されます。

## スクリプトの概要
普段から行っている複数サイトのチェックを効率的にしたいという想いから作成いたしました。
<br>現在は上記3つのショップの通知のみですが、より多くのショップに対応できる形を目指しています。

## 使用技術
- AWS
  - Lambda
  - Eventbridge
- GCP
  - Google Sheets API
  - Workload Identity Federation
- Line Messaging API
- Python 3.12
- IaC(取り組み中)
  - Terraform

## インフラ構成図
![構成図](C:\Users\iwata\OneDrive\ドキュメント\Coffee_Lambda構成図.drawio.svg)

## 実装上の工夫
- サイトごとに関数を分けて、一つのサイトがサーバーダウンしていても他サイトの処理が継続できる形を実現しています。
- 認証ではWorkload Identity Federationを採用して、認証情報の漏洩リスクや管理コストを低減しています。
- 通知ではLine Messaging APIを採用して、使用率の高いLINEから簡単に新商品を確認できる仕組みを構築しています。

## 今後の展望
- Shopify / BASE / STORESなどネットショップのプラットフォームで処理をまとめて、対象となるサイトが追加しやすい形を実現する。
- 通知内容を見直し、新商品の詳細についてより分かりやすい形にブラッシュアップする。
- Terraformで現構成のIaC化を実現させ、構成管理を効率化する。


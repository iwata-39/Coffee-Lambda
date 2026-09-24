import json
import requests
from bs4 import BeautifulSoup
from credentials_import import get_credentials
import gspread
import os

def get_onibus_product():
    # Onibus Coffeeの商品情報を取得
    # Shoptifyストアは、/products.jsonエンドポイントを通じて製品データを提供する
    # エンドポイントではproduct_informationの値を返す

    url_onibus = 'https://onibuscoffee.com/collections/all'

    # Shoptifyサイトからデータをスクレイピングする
    json_url = f"{url_onibus}/products.json"  # ストアのURLに'/products.json'を追加する
    products = []
    try:
        response = requests.get(json_url)
        response.raise_for_status() # requestsのエラー判定
        data = response.json() # JSON形式のレスポンスをJavascriptで扱う形に変換
        for product in data["products"]:  # 各商品を反復処理する
            product_info = {
                "title": product["title"],
                "id": product["id"],
                "variants": product["variants"][0]["price"],
                "images": product["images"],
                "options": product["options"]
            }
            products.append(product_info)

    except requests.RequestException as e: # ネットワーク関連のエラーを表示
        print(f"Error: {e}")
    except json.JSONDecodeError: # デコード時のエラーを表示
        print("Error parsing the JSON response.")
    return products # 商品情報を返す

def get_rec_product():
    # Rec Coffeeの商品情報を取得
    # Onibus同様、Shoptifyストアからのスクレイピング
    
    url_rec = 'https://rec-coffee.com/collections/all'

    # Shoptifyサイトからデータをスクレイピングする
    json_url = f"{url_rec}/products.json"  # ストアのURLに'/products.json'を追加する
    products = []
    try:
        response = requests.get(json_url)
        response.raise_for_status() # requestsのエラー判定
        data = response.json() # JSON形式のレスポンスをJavascriptで扱う形に変換
        for product in data["products"]:  # 各商品を反復処理する
            product_info = {
                "title": product["title"],
                "id": product["id"],
                "variants": product["variants"][0]["price"],
                "images": product["images"],
                "options": product["options"]
            }
            products.append(product_info)

    except requests.RequestException as e: # ネットワーク関連のエラーを表示
        print(f"Error: {e}")
    except json.JSONDecodeError: # デコード時のエラーを表示
        print("Error parsing the JSON response.")
    return products # 商品情報を返す

def get_lvs_product():
    # Leaves Coffeeの商品情報を取得
    # Leavesは、通常のShoptifyストアではないため、別途実装が必要
    # ソースコードを解析し、商品名と価格を取得する

    url_lvs = 'https://leavescoffee.jp/shop/coffee'
    
    # Shoptifyサイトからデータをスクレイピングする
    products = []
    try:
        response = requests.get(url_lvs)
        response.raise_for_status() # requestsのエラー判定
        soup = BeautifulSoup(response.text, 'html.parser') # ライブラリであるBeautiful Soupを使って、取得したWebページのHTML文字列を解析
        obj = soup.select('div.product-item') # divタグのうち、product-item というクラスを持つすべての要素を取得
        
        for e in obj:
            text = e.text.strip() # 文字列の前後の空白を削除
            if text:
            # ￥マークが含まれていたら、品名と価格に分ける
                if '￥' in text:
                    parts = text.split('￥', 1) # 最初に出てくる￥で前後に分割
                    title = parts[0].strip()
                    price = parts[1].replace("New","").strip() # leavesは"New"の文字列が混入する場合があるため除去
                    product_info = {"title": title,"price": price} # Shoptifyデータと辞書で管理
                  
                    products.append(product_info)
            else:
                # ￥が見つからない場合はそのまま追加
                products.append({"title": text,"price": ""})

        # もし1件も取れなかった場合
        if not products:
            products.append({"title": "指定した値が見つかりませんでした"})
            print("指定した値が見つかりませんでした")
        
    except requests.RequestException as e: # ネットワーク関連のエラーを表示
        print(f"Error: {e}")
    return products # 商品情報を返す

def check_and_update_sheets():

    # 1.Google Cloudの認証情報を取得
    credentials = get_credentials()
    client = gspread.authorize(credentials)
    ss = client.open_by_url(os.environ.get("GSPREAD_URL"))
    print("スプレッドシートに接続しました")

    # 2.スプレッドシートを開く
    ws_oni = ss.worksheet("onibus")
    ws_rec = ss.worksheet("rec")
    ws_lvs = ss.worksheet("leaves")
    print("シートを開きました")

    # 3.各サイトの最新データを取得
    onibus_products = get_onibus_product()
    print(f"Onibus: {len(onibus_products)}件取得")

    rec_products = get_rec_product()
    print(f"Rec: {len(rec_products)}件取得")

    leaves_products = get_lvs_product()
    print(f"Leaves: {len(leaves_products)}件取得")

    # 4.スプレッドシートから最新データを取得
    existing_names_oni = set(ws_oni.col_values(1))
    print(existing_names_oni)

    existing_names_rec = set(ws_rec.col_values(1))
    print(existing_names_rec)

    existing_names_lvs = set(ws_lvs.col_values(1))
    print(existing_names_lvs)

    # 5.各サイトのデータから名前を抽出
    new_titles_oni = set(item["title"] for item in onibus_products)
    new_titles_rec = set(item["title"] for item in rec_products)
    new_titles_lvs = set(item["title"] for item in leaves_products)

    # 6.差分をチェック
    diff_oni = new_titles_oni - existing_names_oni
    diff_rec = new_titles_rec - existing_names_rec
    diff_lvs = new_titles_lvs - existing_names_lvs

    # 7.価格を追加
    items_oni = []
    for item in onibus_products:
        if item["title"] in diff_oni:
            items_oni.append({"item": item["title"], "price": item["variants"]})
    print(f"Onibus新商品: {len(items_oni)}件")
    
    items_rec = []
    for item in rec_products:
        if item["title"] in diff_rec:
            items_rec.append({"item": item["title"], "price": item["variants"]})
    print(f"Rec新商品: {len(items_rec)}件")

    items_lvs = []
    for item in leaves_products:
        if item["title"] in diff_lvs:
            items_lvs.append({"item": item["title"], "price": item["price"]})
    print(f"Leaves新商品: {len(items_lvs)}件")

    # 8.結果を辞書にして返す
    new_name = {
        "Onibus Coffee": items_oni,
        "Rec Coffee": items_rec,
        "Leaves Coffee": items_lvs
        }

    print(new_name)

    # 9.スプレッドシートに追加

    # スプレッドシートに存在しない商品情報をappend_rowsで一括出力
    new_oni = [[item["title"], item["id"], item["variants"]] for item in onibus_products if item["title"] not in existing_names_oni]
    if new_oni:
        ws_oni.append_rows(new_oni)
        print("Onibus Coffeeに新商品を追加しました。")
        print(new_oni)

    new_rec = [[item["title"], item["id"], item["variants"]] for item in rec_products if item["title"] not in existing_names_rec]
    if new_rec:
        ws_rec.append_rows(new_rec)
        print("Rec Coffeeに新商品を追加しました。")
        print(new_rec)
    
    new_lvs = [[item["title"], item["price"]] for item in leaves_products if item["title"] not in existing_names_lvs]
    if new_lvs:
        ws_lvs.append_rows(new_lvs)
        print("Leaves Coffeeに新商品を追加しました。")
        print(new_lvs)
    
    return new_name # 差分を返す

def line_notify():
    new_name = check_and_update_sheets()
    print("新商品チェック完了、LINE通知処理開始")
    
    # LINEへの送信
    try:
        LINE_ACCESS_TOKEN = os.environ['LINE_ACCESS_TOKEN']
        LINE_USER_ID = os.environ['LINE_USER_ID']
    except KeyError as e: #環境変数が設定されていない場合のエラーを表示
        return {
            'statusCode': 500,
            'body': json.dumps(f'環境変数が設定されていません: {str(e)}')
        }
    
    url = "https://api.line.me/v2/bot/message/push"
    
    # HTTPリクエストのヘッダーを設定
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    
    message_text = "コーヒー豆 新入荷商品のご案内になります！\n"

    # 新規商品があるかを判定
    has_product= any(new_name.values())

    # 新商品がない場合
    if not has_product:
        return {
            'statusCode': 200,
            'body': json.dumps('新入荷商品はありませんでした。')
        }

    # 新商品がある場合
    for shop_name, products in new_name.items():
        if not products:
            continue
        
        # メッセージに商品情報を追加
        message_text += f"━━━━━━━━━━━━━━━\n"
        message_text += f"\n{shop_name}\n\n"
        for product in products:
            message_text += f'- {product["item"]} (¥{product["price"]})\n'
    print(f"送信メッセージ:\n{message_text}")

    # 送信するメッセージの形式を設定
    body = {
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message_text
            }
        ]
    }
    print(body)

    try:
        response = requests.post(url, headers=headers, json=body) # LINEにJSON形式でPOSTリクエストを送信
        
        if response.status_code != 200:
             print(f"LINE Error Status Code: {response.status_code}")
             print(f"LINE Error: {response.text}")
             return {
                'statusCode': response.status_code,
                'body': json.dumps(f'LINE送信失敗: {response.text}')
            }

        return {
            'statusCode': 200,
            'body': json.dumps('LINE通知完了！')
        }
    except Exception as e:
        print(f"System Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'システムエラー: {str(e)}')
        }

def lambda_handler(event, context):
    try:
        response = line_notify()
        print(response)
        return response

    except Exception as e: # 関数呼び出し時のエラーを表示
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

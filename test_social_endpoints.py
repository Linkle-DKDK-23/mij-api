#!/usr/bin/env python3
"""
ソーシャル機能のAPIエンドポイントをテストするスクリプト
実際のサーバーに対してHTTPリクエストを送信して動作確認を行う
"""

import requests
import json
from uuid import uuid4
import sys

# APIベースURL
BASE_URL = "http://localhost:8000"

def test_api_endpoint(method, endpoint, data=None, headers=None, description=""):
    """APIエンドポイントをテスト"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"✓ {method} {endpoint} - {description}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code < 400:
            try:
                response_data = response.json()
                print(f"  Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"  Response: {response.text[:200]}...")
        else:
            print(f"  Error: {response.text}")
            
        print("-" * 50)
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"✗ {method} {endpoint} - 接続エラー (サーバーが起動していない可能性があります)")
        print("-" * 50)
        return None
    except Exception as e:
        print(f"✗ {method} {endpoint} - エラー: {str(e)}")
        print("-" * 50)
        return None

def main():
    print("=== ソーシャル機能API疎通テスト ===")
    print("注意: このテストを実行する前にバックエンドサーバーを起動してください")
    print("コマンド: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    
    # サンプルUUID (実際のテストではダミーデータ)
    dummy_user_id = str(uuid4())
    dummy_post_id = str(uuid4())
    dummy_comment_id = str(uuid4())
    
    # 認証ヘッダー (実際のテストでは認証が必要)
    headers = {
        "Content-Type": "application/json"
    }
    
    print("1. フォロー機能のテスト")
    test_api_endpoint("POST", f"/social/follow/{dummy_user_id}", 
                     description="フォロー切り替え")
    test_api_endpoint("GET", f"/social/follow/status/{dummy_user_id}",
                     description="フォロー状態確認")
    test_api_endpoint("GET", f"/social/followers/{dummy_user_id}",
                     description="フォロワー一覧取得")
    test_api_endpoint("GET", f"/social/following/{dummy_user_id}",
                     description="フォロー中一覧取得")
    
    print("\n2. いいね機能のテスト")
    test_api_endpoint("POST", f"/social/like/{dummy_post_id}",
                     description="いいね切り替え")
    test_api_endpoint("GET", f"/social/like/status/{dummy_post_id}",
                     description="いいね状態確認")
    test_api_endpoint("GET", "/social/liked-posts",
                     description="いいねした投稿一覧取得")
    
    print("\n3. コメント機能のテスト")
    test_api_endpoint("POST", f"/social/comments/{dummy_post_id}",
                     data={"body": "テストコメントです", "parent_comment_id": None},
                     description="コメント投稿")
    test_api_endpoint("GET", f"/social/comments/{dummy_post_id}",
                     description="コメント一覧取得")
    
    print("\n4. ブックマーク機能のテスト")
    test_api_endpoint("POST", f"/social/bookmark/{dummy_post_id}",
                     description="ブックマーク切り替え")
    test_api_endpoint("GET", f"/social/bookmark/status/{dummy_post_id}",
                     description="ブックマーク状態確認")
    test_api_endpoint("GET", "/social/bookmarks",
                     description="ブックマーク一覧取得")
    
    print("\n=== API疎通テスト完了 ===")
    print("注意: 認証が必要なエンドポイントは401エラーが想定されます")
    print("実際の動作確認にはログインしたユーザーでのテストが必要です")

if __name__ == "__main__":
    main()
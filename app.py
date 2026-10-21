"""
仕様書 → 加工指示書 変換デモ（Webアプリ版）
製造業向けAI活用デモンストレーション
"""

import streamlit as st
import anthropic
from datetime import date

SYSTEM_PROMPT = """あなたは30年以上の経験を持つベテラン生産技術エンジニアです。
製品仕様書を読み込み、マシニングセンタ・旋盤等を使った実際の加工現場で
即座に使える「加工指示書」を作成してください。

加工指示書には以下を必ず含めてください：
1. 工程番号と工程名（例：工程10 フライス加工）
2. 使用機械・工具
3. 加工手順（番号付きステップ）
4. 重要寸法と公差（要注意箇所は★で強調）
5. 品質チェックポイント
6. 注意事項・禁止事項

出力は現場の作業者がそのまま使えるよう、具体的かつ簡潔に。
専門用語は正確に使い、曖昧な表現は避けること。"""


def convert_spec(spec_text: str) -> str:
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"以下の製品仕様書を読んで、加工指示書を作成してください。\n\n{spec_text}",
            }
        ],
    )
    return message.content[0].text


# --- ページ設定 ---
st.set_page_config(
    page_title="仕様書→加工指示書 AI変換デモ",
    layout="centered",
)

st.title("仕様書 → 加工指示書 AI変換デモ")
st.caption("製造業向けAI活用デモンストレーション")

st.markdown(
    """
    製品仕様書を貼り付けるか、テキストファイルをアップロードするだけで、
    現場ですぐ使える**加工指示書**を自動生成します。
    """
)

st.divider()

# --- 入力 ---
st.subheader("仕様書の入力")

input_method = st.radio("入力方法", ["テキストを直接入力", "ファイルをアップロード"], horizontal=True)

spec_text = ""

if input_method == "テキストを直接入力":
    spec_text = st.text_area(
        "仕様書の内容を貼り付けてください",
        height=300,
        placeholder="品名、材質、寸法、公差、表面処理、検査項目などを含む仕様書を貼り付けてください",
    )
else:
    uploaded_file = st.file_uploader("テキストファイル（.txt）をアップロード", type=["txt"])
    if uploaded_file:
        spec_text = uploaded_file.read().decode("utf-8")
        st.success(f"読み込み完了: {uploaded_file.name}")
        with st.expander("読み込んだ内容を確認"):
            st.text(spec_text)

st.divider()

# --- 変換実行 ---
col1, col2 = st.columns([1, 3])
with col1:
    run = st.button("加工指示書を生成", type="primary", disabled=not spec_text.strip())

if run and spec_text.strip():
    with st.spinner("生成中...（10〜20秒ほどかかります）"):
        try:
            result = convert_spec(spec_text)
            today = date.today().strftime("%Y-%m-%d")

            st.divider()
            st.subheader("生成された加工指示書")
            st.text(result)

            # ダウンロード
            download_content = f"生成日: {today}\n{'=' * 60}\n{result}"
            st.download_button(
                label="テキストファイルとしてダウンロード",
                data=download_content.encode("utf-8"),
                file_name=f"加工指示書_{today}.txt",
                mime="text/plain",
            )

        except anthropic.AuthenticationError:
            st.error("APIキーが正しく設定されていません。管理者にご連絡ください。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

st.divider()
st.caption("※ このデモはAIが仕様書から自動生成したものです。最終確認は担当技術者が行ってください。")

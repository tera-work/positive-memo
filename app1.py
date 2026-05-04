# pip install streamlit,python -m pip install groq を最初にターミナルに入力
# 実行時にターミナルに streamlit run app1.py を入力

from groq import Groq
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from datetime import datetime

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("ポジティブメモ")

st.divider()

st.subheader("自己肯定感を育て、毎日を前向きに過ごすためのメモアプリ")

st.divider()

st.write("日々の「頑張ったこと」「嬉しかったこと」を記録し、自分の成長や小さな幸せに気づけるアプリです。気持ちが落ち込んだときは、過去のメモを振り返ることで、自分の積み重ねを実感し、気持ちを整えることができます。")

if 'memo_df' not in st.session_state:
    st.session_state.memo_df = pd.DataFrame(columns=["日時", "カテゴリ", "内容"])

memo_count = len(st.session_state.memo_df)
st.write(f"現在のメモ数: {memo_count} 件")

st.divider()

col1, col2 = st.columns(2)

if "button_pressed" not in st.session_state:
    st.session_state.button_pressed = None

with col1:
    if st.button("メモを記入"):
        st.session_state.button_pressed = "記入"

with col2:
    if st.button("振り返る"):
        st.session_state.button_pressed = "振り返る"

# 保存用のデータフレーム
if "memo_df" not in st.session_state:
    st.session_state.memo_df = pd.DataFrame(columns=["日時", "カテゴリ", "内容"])

# -----------------------------
#  記入画面
# -----------------------------
if st.session_state.button_pressed == "記入":
    st.write("今日頑張ったこと、楽しかったことは？")

    kinds = st.selectbox(
        'カテゴリ',
        ['勉強', '仕事', '人間関係', '苦手克服', '人助け', '趣味', 'その他']
    )

    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i in range(1):
        st.write('')

    content = st.text_input('記載欄', max_chars=500)

    for i in range(1):
        st.write('')

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("確定"):
            if content.strip() != "":
                
                new_row = pd.DataFrame({
                    "日時": [date_time],
                    "カテゴリ": [kinds],
                    "内容": [content]
                })
                st.session_state.memo_df = pd.concat(
                    [st.session_state.memo_df, new_row],
                    ignore_index=True
                )
                st.success("メモを追加しました")

                status_area = st.empty()
                stream = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"「{content}」を50文字程度で褒めて"}],
                    model="llama-3.3-70b-versatile",
                    stream=True,
                )

                full_response = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        status_area.info(f"{full_response}")
            
            else:
                st.warning("内容を入力してください")


# -----------------------------
#  振り返り画面（削除機能付き）
# -----------------------------
elif st.session_state.button_pressed == "振り返る":
    if len(st.session_state.memo_df) == 0:
        st.header("まだメモがありません。")
    else:
        st.header("メモ一覧")
        sort = st.selectbox(
            '並び替え',
            ['新しい順', '古い順']
        )
        narrow_down = st.selectbox(
            '絞り込み',
            ['なし', '勉強', '仕事', '人間関係', '苦手克服', '人助け', '趣味', 'お出かけ', 'その他']
        )

        # ---- ソート処理 ----
        if sort == "新しい順":
            st.session_state.memo_df = st.session_state.memo_df.sort_values(
                by="日時", ascending=False
            ).reset_index(drop=True)
        else:
            st.session_state.memo_df = st.session_state.memo_df.sort_values(
                by="日時", ascending=True
            ).reset_index(drop=True)

        # ---- 絞り込み ----
        if narrow_down == "なし":
            filtered_df = st.session_state.memo_df
        else:
            filtered_df = st.session_state.memo_df[
                st.session_state.memo_df["カテゴリ"] == narrow_down
            ].reset_index(drop=True)

        # ======================================================
        #   各行に削除ボタンを配置
        # ======================================================
        for i, row in filtered_df.iterrows():
            with st.expander(f"{row['日時']} / {row['カテゴリ']}"):
                st.write(row["内容"])

                # 削除処理
                if st.button("このメモを削除", key=f"delete_{i}"):
                    # 元の DataFrame のインデックスを取得して削除
                    orig_idx = st.session_state.memo_df[
                        (st.session_state.memo_df["日時"] == row["日時"]) &
                        (st.session_state.memo_df["内容"] == row["内容"])
                    ].index

                    st.session_state.memo_df = st.session_state.memo_df.drop(orig_idx).reset_index(drop=True)

                    st.success("削除しました")
                    st.rerun()
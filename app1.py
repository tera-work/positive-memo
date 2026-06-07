# pip install streamlit groq python-dotenv pandas
# pip install supabase
# 実行時にターミナルに streamlit run app1.py を入力

from groq import Groq
from supabase import create_client
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

st.title("ポジティブメモ")

st.divider()

st.subheader("自己肯定感を育て、毎日を前向きに過ごすためのメモアプリ")

st.divider()

st.write("日々の「頑張ったこと」「嬉しかったこと」を記録し、自分の成長や小さな幸せに気づけるアプリです。気持ちが落ち込んだときは、過去のメモを振り返ることで、自分の積み重ねを実感し、気持ちを整えることができます。")

result = supabase.table("memo").select("*").execute()
memo_df = pd.DataFrame(result.data)

memo_count = len(memo_df)

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

# -----------------------------
#  記入画面
# -----------------------------
if st.session_state.button_pressed == "記入":
    st.write("今日頑張ったこと、楽しかったことは？")

    kinds = st.selectbox(
        'カテゴリ',
        ['勉強', '仕事', '人間関係', '苦手克服', '人助け', '運動', '趣味', 'お出かけ', 'その他']
    )

    for i in range(1):
        st.write('')

    content = st.text_input('記載欄', max_chars=500)

    for i in range(1):
        st.write('')

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("確定"):
            if content.strip() != "":
                
                supabase.table("memo").insert({
                    "category": kinds,
                    "content": content
                }).execute()
                st.success("メモを追加しました")

                status_area = st.empty()
                try:
                    stream = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"「{content}」を50文字程度で褒めて"}],
                        model="llama-3.3-70b-versatile",
                        stream=True,
                    )

                    full_response = ""

                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            status_area.info(full_response)

                except Exception as e:
                    st.error(f"AI応答エラー: {e}")

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

    result = (
        supabase
        .table("memo")
        .select("*")
        .execute()
    )

    memo_df = pd.DataFrame(result.data)

    if len(memo_df) == 0:
        st.header("まだメモがありません。")

    else:
        st.header("メモ一覧")
        sort = st.selectbox(
            '並び替え',
            ['新しい順', '古い順']
        )
        narrow_down = st.selectbox(
            '絞り込み',
            ['なし', '勉強', '仕事', '人間関係', '苦手克服', '人助け', '運動', '趣味', 'お出かけ', 'その他']
        )

        # ---- ソート処理 ----
        display_df = memo_df.copy()

        if sort == "新しい順":
            display_df = display_df.sort_values(
                by="created_at", ascending=False
            ).reset_index(drop=True)
        else:
            display_df = display_df.sort_values(
                by="created_at", ascending=True
            ).reset_index(drop=True)

        # ---- 絞り込み ----
        if narrow_down == "なし":
            filtered_df = display_df
        else:
            filtered_df = display_df[
                display_df["category"] == narrow_down
            ].reset_index(drop=True)

        # ======================================================
        #   各行に削除ボタンを配置
        # ======================================================
        for i, row in filtered_df.iterrows():
            with st.expander(
                f"{row['created_at']} / {row['category']}"
            ):
                st.write(row["content"])

                # 削除処理
                if st.button("このメモを削除",key=f"delete_{row['id']}"):
                    
                    supabase.table("memo") \
                        .delete() \
                        .eq("id", row["id"]) \
                        .execute()

                    st.success("削除しました")
                    st.rerun()
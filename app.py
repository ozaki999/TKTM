import streamlit as st
import numpy as np
import random

# --- 連立方程式の問題生成ロジック ---

def generate_equation_system():
    """
    一意の整数解を持つ連立一次方程式 (ax + by = c, dx + ey = f) を生成する。
    ただし、常に整数解が保証されるわけではないため、試行回数を設ける。
    """
    max_iter = 100 # 問題生成の最大試行回数
    for _ in range(max_iter):
        # 係数をランダムに生成 (-5 から 5 の間の0を含まない整数)
        a, b, d, e = [random.randint(-5, 5) for _ in range(4)]
        
        # 0になるのを避ける（少なくとも1つは非ゼロ）
        while a == 0 and b == 0: a = random.randint(-5, 5)
        while d == 0 and e == 0: e = random.randint(-5, 5)

        # 解 (x, y) をランダムに生成 (-10 から 10 の間の整数)
        x_sol = random.randint(-10, 10)
        y_sol = random.randint(-10, 10)

        # 定数項 c, f を計算
        c = a * x_sol + b * y_sol
        f = d * x_sol + e * y_sol

        # 行列式 (ad - bd) を計算して、一意解があるか確認
        # 行列式が0の場合、解がないか無限の解がある
        determinant = a * e - b * d

        if determinant != 0:
            # 念のため、生成された解が整数であることを確認
            # Cramerの公式を使って解を計算し、それが整数であることを確認する
            # num_x = c * e - b * f
            # num_y = a * f - c * d
            # if num_x % determinant == 0 and num_y % determinant == 0:
            #     # 実際には、x_sol, y_sol から逆算しているので、これらは整数になるはず
            return {
                "eq1_coeffs": (a, b),
                "eq1_const": c,
                "eq2_coeffs": (d, e),
                "eq2_const": f,
                "solution_x": x_sol,
                "solution_y": y_sol
            }
    
    # 規定回数試行しても適切な問題が生成できなかった場合
    st.warning("適切な連立方程式の生成に失敗しました。新しい問題を試してみてください。")
    return None

# --- Streamlit UI ---

st.set_page_config(layout="centered", page_title="連立方程式アプリ")
st.title("🔢 連立方程式 問題アプリ")

st.markdown("""
このアプリは、2変数の連立一次方程式をランダムに生成します。
$x$と$y$の値を入力して、解答が正しいか確認してみましょう！
""")

# --- セッション状態の初期化 ---
# アプリの状態を維持するために st.session_state を使用します
if 'problem' not in st.session_state or st.session_state.problem is None:
    st.session_state.problem = generate_equation_system()
    st.session_state.result = None
    st.session_state.user_x = ""
    st.session_state.user_y = ""

# --- 問題表示 ---
if st.session_state.problem:
    prob = st.session_state.problem
    st.subheader("問題")
    # LaTeX記法で数式をきれいに表示
    st.latex(f"\\begin{{cases}}\
                {prob['eq1_coeffs'][0]}x + {prob['eq1_coeffs'][1]}y = {prob['eq1_const']} \\\\\
                {prob['eq2_coeffs'][0]}x + {prob['eq2_coeffs'][1]}y = {prob['eq2_const']} \\\\\
                \\end{{cases}}")
else:
    st.error("問題が正しく生成されていません。「新しい問題」ボタンを押してください。")

# --- 解答入力 ---
st.subheader("解答を入力してください")
col1, col2 = st.columns(2) # 入力ボックスを横並びにする
with col1:
    user_x_input = st.text_input("x の値:", value=st.session_state.user_x, key="user_x_input")
with col2:
    user_y_input = st.text_input("y の値:", value=st.session_state.user_y, key="user_y_input")

# --- 判定ボタンと新しい問題ボタン ---
col_buttons = st.columns(2) # ボタンを横並びにする
with col_buttons[0]:
    if st.button("解答を判定"):
        try:
            # 入力が空でないことを確認
            if not user_x_input or not user_y_input:
                st.session_state.result = {"type": "warning", "message": "x と y の両方を入力してください。"}
            else:
                user_x = float(user_x_input)
                user_y = float(user_y_input)

                # floatでの比較は誤差が怖いので、整数解を仮定して厳密に比較
                if abs(user_x - prob['solution_x']) < 1e-9 and abs(user_y - prob['solution_y']) < 1e-9:
                    st.session_state.result = {"type": "success", "message": f"正解です！ (x={int(prob['solution_x'])}, y={int(prob['solution_y'])})"}
                else:
                    st.session_state.result = {"type": "error", "message": f"不正解です。もう一度考えてみましょう。"}
        except ValueError: # 数字以外の入力があった場合
            st.session_state.result = {"type": "error", "message": "数字を正しく入力してください。"}
        
        # ユーザーの入力値をセッション状態に保存 (再実行時に保持するため)
        st.session_state.user_x = user_x_input
        st.session_state.user_y = user_y_input

with col_buttons[1]:
    if st.button("新しい問題"):
        # セッション状態をリセットして新しい問題を生成
        st.session_state.problem = generate_equation_system()
        st.session_state.result = None
        st.session_state.user_x = ""
        st.session_state.user_y = ""
        st.rerun() # アプリを再実行し、UIを更新

# --- 結果表示 ---
if st.session_state.result:
    if st.session_state.result["type"] == "success":
        st.success(st.session_state.result["message"])
    elif st.session_state.result["type"] == "error":
        st.error(st.session_state.result["message"])
    elif st.session_state.result["type"] == "warning":
        st.warning(st.session_state.result["message"])

st.markdown("---")
st.write("Developed with Streamlit by Google Gemini")

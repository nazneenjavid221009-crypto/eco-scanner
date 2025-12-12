import streamlit as st
import math
import random

st.set_page_config(page_title="EcoScanner", page_icon="🌿", layout="centered")

st.markdown("<h1 style='text-align:center'>🌿 EcoScanner 9000</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;margin-top:-12px;color:gray'>Mobile-friendly inspector for quick eco-estimates</p>", unsafe_allow_html=True)
st.write("---")

with st.form(key='input_form'):
    product_name = st.text_input("Product name (optional)", placeholder="e.g. 'Polyester T-shirt' or 'Biodegradable dish soap'")
    product_desc = st.text_area("Short description (tell the scanner about materials/packaging)", placeholder="e.g. 'Made of 100% cotton, shipped plastic-free'", height=110)
    guess = st.slider("How eco-friendly do you think this product is? (0 worst — 100 best)", 0, 100, 50)
    submitted = st.form_submit_button("Save inputs")

if submitted:
    st.session_state['product_name'] = product_name
    st.session_state['product_desc'] = product_desc
    st.session_state['guess'] = guess

product_name = st.session_state.get('product_name', product_name)
product_desc = st.session_state.get('product_desc', product_desc)
guess = st.session_state.get('guess', guess)

POS_KEYWORDS = {
    'recycled': 12, 'recyclable': 10, 'biodegradable': 14, 'organic': 10,
    'compostable': 12, 'certified organic': 15, 'fair trade': 8,
    'no plastic': 8, 'plastic-free': 10, 'low-energy': 9, 'solar': 10,
    'natural': 6, 'glass': 6, 'bamboo': 8
}

NEG_KEYWORDS = {
    'plastic': 12, 'polyester': 11, 'disposable': 14, 'single-use': 14,
    'non-recyclable': 16, 'toxic': 15, 'chemical': 10, 'microfiber': 10,
    'nylon': 9, 'packed in plastic': 12, 'petroleum': 13
}

def predict_score(name, desc):
    text = (name + ' ' + desc).lower()
    base = 50
    bonus = 0
    for k, v in POS_KEYWORDS.items():
        if k in text:
            bonus += v
    for k, v in NEG_KEYWORDS.items():
        if k in text:
            bonus -= v
    if len(text) < 10:
        bonus -= 6
    score = max(0, min(100, base + bonus + int((hash(text) % 11) - 5)))
    return score

def explain_score(name, desc, score):
    text = (name + ' ' + desc).lower()
    reasons = []
    for k in POS_KEYWORDS:
        if k in text:
            reasons.append(f"contains '{k}' (+{POS_KEYWORDS[k]})")
    for k in NEG_KEYWORDS:
        if k in text:
            reasons.append(f"mentions '{k}' (-{NEG_KEYWORDS[k]})")
    if not reasons:
        reasons = ["no clear eco-related keywords found — using a generic estimate"]
    reasons = reasons[:3]
    expl = f"Predicted eco-score: {score}/100.\nReasons: " + ", ".join(reasons)
    expl += "\nNote: This is a quick heuristic estimate for demo purposes."
    return expl

col1, col2 = st.columns([1,1])
with col1:
    if st.button("🔎 ANALYZE"):
        s = predict_score(product_name or '', product_desc or '')
        st.session_state['last_score'] = s
        st.session_state['analyzed'] = True
        st.session_state['accuracy_shown'] = False
        st.session_state['explanation_shown'] = False

with col2:
    if st.button("🔄 RESET"):
        for k in ['product_name','product_desc','guess','last_score','analyzed','accuracy_shown','explanation_shown']:
            if k in st.session_state:
                del st.session_state[k]
        st.experimental_rerun()

st.write("---")

if st.session_state.get('analyzed'):
    score = st.session_state.get('last_score', 0)
    st.subheader("Result")
    st.metric("Eco-score", f"{score}/100")

    if score >= 75:
        st.success("This product looks quite eco-friendly.")
    elif score >= 45:
        st.info("This product has a mix of eco and non-eco signals.")
    else:
        st.warning("This product likely has several non-eco characteristics.")

    if st.button("📏 Show accuracy"):
        st.session_state['accuracy_shown'] = True

    if st.session_state.get('accuracy_shown'):
        user_guess = st.session_state.get('guess', guess)
        diff = abs(user_guess - score)

        if diff == 0:
            acc_text = "Perfect! Your guess matched the scanner."
        elif diff <= 5:
            acc_text = f"Very close — within {diff} points."
        elif diff <= 15:
            acc_text = f"Reasonable — off by {diff} points."
        else:
            acc_text = f"Quite different — off by {diff} points."

        st.write(f"**Your guess:** {user_guess}/100  —  **Difference:** {diff}")
        st.info(acc_text)

        if st.button("💬 Show AI explanation"):
            st.session_state['explanation_shown'] = True

    if st.session_state.get('explanation_shown'):
        expl = explain_score(product_name or '', product_desc or '', score)
        st.markdown("**AI explanation:**")
        st.write(expl)

else:
    st.info("Fill product details and press ANALYZE to get a quick eco-score.")

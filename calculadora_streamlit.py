"""
Calculadora Científica PRO — versión web con Streamlit
Ejecutar desde la terminal:
    python -m streamlit run calculadora_streamlit.py

Instalación previa:
    python -m pip install streamlit
"""

import ast
import math
import operator
import streamlit as st


# ---------- Evaluador matemático seguro (sin eval) ----------
BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def evaluate_expression(expression: str, angle_mode: str, ans: float = 0):
    expression = (
        expression.strip()
        .replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("^", "**")
        .replace("π", "pi")
        .replace("√", "sqrt")
    )
    if not expression:
        raise ValueError("Escribe una expresión matemática.")

    def to_rad(x):
        return math.radians(x) if angle_mode == "Grados (DEG)" else x

    def from_rad(x):
        return math.degrees(x) if angle_mode == "Grados (DEG)" else x

    def factorial(x):
        if not float(x).is_integer() or x < 0:
            raise ValueError("El factorial requiere un entero no negativo.")
        if x > 170:
            raise ValueError("El número es demasiado grande para calcular su factorial.")
        return math.factorial(int(x))

    def root(x, n=2):
        if n == 0:
            raise ValueError("El índice de la raíz no puede ser cero.")
        if x < 0:
            if float(n).is_integer() and int(n) % 2:
                return -((-x) ** (1 / n))
            raise ValueError("La raíz real de un número negativo requiere índice impar.")
        return x ** (1 / n)

    def logbase(x, base):
        return math.log(x, base)

    def ncr(n, r):
        return math.comb(int(n), int(r))

    def npr(n, r):
        return math.perm(int(n), int(r))

    def sign(x):
        return (x > 0) - (x < 0)

    def clamp(x, lo, hi):
        return max(lo, min(hi, x))

    env = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "phi": (1 + math.sqrt(5)) / 2,
        "Ans": ans,
        "ans": ans,
        "sin": lambda x: math.sin(to_rad(x)),
        "sen": lambda x: math.sin(to_rad(x)),
        "cos": lambda x: math.cos(to_rad(x)),
        "tan": lambda x: math.tan(to_rad(x)),
        "tg": lambda x: math.tan(to_rad(x)),
        "asin": lambda x: from_rad(math.asin(x)),
        "acos": lambda x: from_rad(math.acos(x)),
        "atan": lambda x: from_rad(math.atan(x)),
        "atan2": lambda y, x: from_rad(math.atan2(y, x)),
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "asinh": math.asinh,
        "acosh": math.acosh,
        "atanh": math.atanh,
        "sqrt": math.sqrt,
        "cbrt": math.cbrt,
        "root": root,
        "abs": abs,
        "ln": math.log,
        "log": math.log10,
        "log10": math.log10,
        "log2": math.log2,
        "logbase": logbase,
        "exp": math.exp,
        "factorial": factorial,
        "gamma": math.gamma,
        "lgamma": math.lgamma,
        "floor": math.floor,
        "ceil": math.ceil,
        "trunc": math.trunc,
        "round": round,
        "degrees": math.degrees,
        "radians": math.radians,
        "hypot": math.hypot,
        "cot": lambda x: 1 / math.tan(to_rad(x)),
        "sec": lambda x: 1 / math.cos(to_rad(x)),
        "csc": lambda x: 1 / math.sin(to_rad(x)),
        "percent": lambda x: x / 100,
        "sign": sign,
        "min": min,
        "max": max,
        "clamp": clamp,
        "comb": ncr,
        "ncr": ncr,
        "perm": npr,
        "npr": npr,
    }

    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in env and not callable(env[node.id]):
                return env[node.id]
            raise ValueError(f"Constante no permitida: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("El exponente es demasiado grande.")
            return BIN_OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](visit(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fn = env.get(node.func.id)
            if not callable(fn):
                raise ValueError(f"Función no permitida: {node.func.id}")
            if node.keywords:
                raise ValueError("No se admiten argumentos con nombre.")
            return fn(*(visit(arg) for arg in node.args))
        raise ValueError("Expresión no válida. Usa números, operadores y funciones disponibles.")

    result = visit(tree.body)
    if isinstance(result, complex):
        if abs(result.imag) < 1e-12:
            result = result.real
        else:
            raise ValueError("El resultado es complejo; esta versión muestra resultados reales.")
    if isinstance(result, float) and not math.isfinite(result):
        raise ValueError("El resultado no es finito.")
    return result


def fmt(value):
    if isinstance(value, int):
        return f"{value:,}".replace(",", " ")
    if isinstance(value, float):
        if value != 0 and (abs(value) >= 1e12 or abs(value) < 1e-8):
            return f"{value:.10e}"
        return f"{value:.12g}"
    return str(value)


# ---------- Interfaz web ----------
st.set_page_config(
    page_title="Calculadora Científica PRO",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #101820 0%, #17252e 100%); color: #f2f6f7; }
    h1, h2, h3, p, label { color: #f2f6f7; }
    div[data-testid="stMetric"] { background: #1b2b34; border: 1px solid #00a6a6; padding: 14px; border-radius: 12px; }
    div.stButton > button { border-radius: 9px; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []
if "ans" not in st.session_state:
    st.session_state.ans = 0.0
if "memory" not in st.session_state:
    st.session_state.memory = 0.0
if "expression" not in st.session_state:
    st.session_state.expression = ""

st.title("🧮 Calculadora Científica PRO")
st.caption("Aplicación web desarrollada en Python con Streamlit · No requiere librerías matemáticas externas.")

with st.sidebar:
    st.header("⚙️ Configuración")
    angle_mode = st.radio("Modo angular", ["Grados (DEG)", "Radianes (RAD)"], index=0)
    st.divider()
    st.subheader("🧠 Memoria")
    st.metric("Valor guardado", fmt(st.session_state.memory))
    m1, m2 = st.columns(2)
    if m1.button("M+ (sumar)", use_container_width=True):
        st.session_state.memory += float(st.session_state.ans)
        st.rerun()
    if m2.button("MC (borrar)", use_container_width=True):
        st.session_state.memory = 0.0
        st.rerun()
    if st.button("MR (insertar memoria)", use_container_width=True):
        st.session_state.expression += fmt(st.session_state.memory)
        st.rerun()
    if st.button("Borrar historial", use_container_width=True):
        st.session_state.history = []
        st.rerun()
    st.divider()
    st.markdown("**Constantes disponibles**")
    st.code("pi   e   tau   phi   Ans", language="text")

left, right = st.columns([1.35, 1], gap="large")

with left:
    st.subheader("Expresión matemática")
    expression = st.text_input(
        "Escribe la operación",
        key="expression",
        placeholder="Ejemplo: sin(30) + sqrt(81) + log(100)",
        help="Usa * para multiplicar, / para dividir y ** para potencias. Las funciones se escriben con paréntesis.",
    )
    button_cols = st.columns(6)
    quick_buttons = [
        ("7", "7"), ("8", "8"), ("9", "9"), ("÷", "/"), ("(", "("), (")", ")"),
        ("4", "4"), ("5", "5"), ("6", "6"), ("×", "*"), ("pi", "pi"), ("e", "e"),
        ("1", "1"), ("2", "2"), ("3", "3"), ("−", "-"), ("**", "**"), ("sqrt(", "sqrt("),
        ("0", "0"), (".", "."), ("Ans", "Ans"), ("+", "+"), ("-", "-"), ("AC", "__CLEAR__"),
    ]
    for idx, (label, value) in enumerate(quick_buttons):
        with button_cols[idx % 6]:
            if st.button(label, key=f"key_{idx}", use_container_width=True):
                if value == "__CLEAR__":
                    st.session_state.expression = ""
                else:
                    st.session_state.expression += value
                st.rerun()

    st.markdown("**Funciones rápidas**")
    function_cols = st.columns(4)
    quick_functions = ["sin(", "cos(", "tan(", "asin(", "acos(", "atan(", "ln(", "log(", "log2(", "factorial(", "cbrt(", "abs("]
    for idx, label in enumerate(quick_functions):
        with function_cols[idx % 4]:
            if st.button(label, key=f"fn_{idx}", use_container_width=True):
                st.session_state.expression += label
                st.rerun()

    calc_col, clear_col = st.columns([2, 1])
    calculate_clicked = calc_col.button("＝ Calcular", type="primary", use_container_width=True)
    clear_clicked = clear_col.button("Limpiar", use_container_width=True)

    if clear_clicked:
        st.session_state.expression = ""
        st.rerun()

    if calculate_clicked:
        try:
            result = evaluate_expression(st.session_state.expression, angle_mode, st.session_state.ans)
            st.session_state.ans = result
            result_text = fmt(result)
            st.session_state.history.insert(
                0,
                {
                    "Expresión": st.session_state.expression,
                    "Resultado": result_text,
                    "Modo": angle_mode,
                },
            )
            st.session_state.last_result_text = result_text
            st.success("Cálculo realizado correctamente.")
        except Exception as exc:
            st.error(f"No se pudo calcular: {exc}")

    if "last_result_text" in st.session_state:
        st.metric("Resultado", st.session_state.last_result_text)

with right:
    st.subheader("📚 Guía de funciones")
    with st.expander("Trigonometría", expanded=True):
        st.code("sin(30)   cos(60)   tan(45)\nasin(0.5)   acos(0.5)   atan(1)", language="text")
        st.caption("Las funciones trigonométricas respetan el modo angular seleccionado.")
    with st.expander("Logaritmos, potencias y raíces"):
        st.code("ln(e)   log(100)   log2(8)\n2**10   sqrt(81)   cbrt(27)\nroot(32,5)   exp(2)", language="text")
    with st.expander("Combinatoria y funciones avanzadas"):
        st.code("factorial(5)   gamma(6)\ncomb(8,3)   perm(8,3)\nlogbase(8,2)   hypot(3,4)\nmin(2,5,1)   max(2,5,1)", language="text")
    with st.expander("Ejemplos para probar"):
        examples = [
            "sin(30) + cos(60)",
            "sqrt(144) + 5**3",
            "logbase(81,3)",
            "comb(10,4)",
            "factorial(6) / factorial(4)",
            "hypot(3,4)",
        ]
        for item in examples:
            st.code(item, language="text")

st.divider()
st.subheader("🕘 Historial de operaciones")
if st.session_state.history:
    st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)
    csv_text = "Expresión,Resultado,Modo\n" + "\n".join(
        '"' + item["Expresión"].replace('"', '""') + '","' + item["Resultado"].replace('"', '""') + '","' + item["Modo"] + '"'
        for item in st.session_state.history
    )
    st.download_button(
        "⬇️ Descargar historial CSV",
        data=csv_text,
        file_name="historial_calculadora.csv",
        mime="text/csv",
    )
else:
    st.info("Tus cálculos aparecerán aquí después de presionar «Calcular».")

st.caption("Consejo: presiona Enter dentro del campo de expresión para confirmar la entrada y luego pulsa «Calcular».")

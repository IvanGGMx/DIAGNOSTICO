import streamlit as st
import random
import os
import json

# =========================
# Usuarios
# =========================
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = {"password": password, "attempts": []}
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    return username in users and users[username]["password"] == password

def save_attempt(username, answers):
    users = load_users()
    if username in users:
        users[username]["attempts"].append(answers)
        save_users(users)

# =========================
# Session state
# =========================
for key, default in [
    ("logged_in", False),
    ("username", None),
    ("page", "login"),
    ("current_question", 0),
    ("answers", {}),
    ("finished", False),
    ("question_order", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# =========================
# Banco de preguntas completo (25)
# =========================
questions = [
    # --- UNIDAD 1 ---
    {"question":"¿Qué define el punto de equivalencia en una valoración?",
     "options":["Cuando cambia el color del indicador",
                "Cuando reaccionan cantidades estequiométricamente equivalentes",
                "Cuando el pH es 7",
                "Cuando termina la reacción visualmente"],
     "answer":"Cuando reaccionan cantidades estequiométricamente equivalentes",
     "explanation":"El punto de equivalencia ocurre cuando las cantidades del analito y titulante reaccionan en proporción estequiométrica."},

    {"question":"Una reacción de precipitación se basa en:",
     "options":["La formación de un gas",
                "La formación de un sólido insoluble",
                "La neutralización ácido-base",
                "La transferencia de electrones"],
     "answer":"La formación de un sólido insoluble",
     "explanation":"Las valoraciones por precipitación implican la formación de un compuesto poco soluble."},

    {"question":"Las reacciones ácido-base implican:",
     "options":["Transferencia de electrones",
                "Transferencia de protones",
                "Formación de complejos",
                "Reacciones redox"],
     "answer":"Transferencia de protones",
     "explanation":"Según Brønsted-Lowry, un ácido dona protones y una base los acepta."},

    {"question":"Las reacciones de óxido-reducción se caracterizan por:",
     "options":["Transferencia de protones",
                "Transferencia de electrones",
                "Formación de precipitados",
                "Disolución de sólidos"],
     "answer":"Transferencia de electrones",
     "explanation":"Las reacciones redox implican intercambio de electrones entre especies."},

    {"question":"Una condición de validez de una valoración es:",
     "options":["La reacción debe ser lenta",
                "La reacción debe ser cuantitativa",
                "Debe formarse un gas",
                "Debe cambiar el pH"],
     "answer":"La reacción debe ser cuantitativa",
     "explanation":"Para que una valoración sea válida, la reacción debe ser rápida y cuantitativa."},

    # --- UNIDAD 2 ---
    {"question":"La ecuación de Nernst se utiliza en:",
     "options":["Conductimetría",
                "Potenciometría",
                "Espectrofotometría",
                "Gravimetría"],
     "answer":"Potenciometría",
     "explanation":"La ecuación de Nernst relaciona el potencial del electrodo con la concentración."},

    {"question":"La Ley de Beer establece que:",
     "options":["La absorbancia es proporcional a la concentración",
                "La conductividad depende del voltaje",
                "El pH depende del volumen",
                "La pendiente es constante"],
     "answer":"La absorbancia es proporcional a la concentración",
     "explanation":"A = εbc, la absorbancia es proporcional a la concentración."},

    {"question":"La conductimetría se basa en:",
     "options":["Medición de absorbancia",
                "Medición de potencial",
                "Medición de conductividad eléctrica",
                "Medición de masa"],
     "answer":"Medición de conductividad eléctrica",
     "explanation":"La conductimetría mide la capacidad de una solución para conducir corriente eléctrica."},

    {"question":"Un electrodo de referencia se caracteriza por:",
     "options":["Tener potencial constante",
                "Ser variable",
                "Depender del pH",
                "Medir absorbancia"],
     "answer":"Tener potencial constante",
     "explanation":"El electrodo de referencia mantiene un potencial conocido y estable durante la medición."},

    {"question":"Una curva de calibración permite:",
     "options":["Determinar concentraciones desconocidas",
                "Calcular pH",
                "Determinar masa molar",
                "Medir temperatura"],
     "answer":"Determinar concentraciones desconocidas",
     "explanation":"Relaciona señal instrumental con concentración del analito."},

    # --- UNIDAD 3 ---
    {"question":"La TVCM significa:",
     "options":["Tabla de Variación de Concentraciones Molares",
                "Titulación Volumétrica de Compuestos Mixtos",
                "Tabla de Valores Constantes Medidos",
                "Técnica Volumétrica de Calibración"],
     "answer":"Tabla de Variación de Concentraciones Molares",
     "explanation":"La TVCM permite seguir el cambio de concentraciones durante la valoración."},

    {"question":"En una valoración ácido-base, la curva se sigue comúnmente mediante:",
     "options":["Conductividad",
                "pH-metría",
                "Absorbancia",
                "Gravimetría"],
     "answer":"pH-metría",
     "explanation":"Se mide el cambio de pH conforme avanza la valoración."},

    {"question":"En complejometría, se forma:",
     "options":["Un precipitado",
                "Un complejo metal-ligando",
                "Un gas",
                "Un ácido fuerte"],
     "answer":"Un complejo metal-ligando",
     "explanation":"Se forma un complejo estable entre un ion metálico y un ligando."},

    {"question":"Un indicador químico sirve para:",
     "options":["Medir temperatura",
                "Detectar el punto final",
                "Medir concentración directa",
                "Determinar masa"],
     "answer":"Detectar el punto final",
     "explanation":"Permite visualizar el final práctico de la valoración."},

    {"question":"Las valoraciones redox pueden seguirse por:",
     "options":["Potenciometría",
                "pH-metría",
                "Gravimetría",
                "Filtración"],
     "answer":"Potenciometría",
     "explanation":"El cambio de potencial permite identificar el punto de equivalencia."},

    # --- UNIDAD 4 ---
    {"question":"Un sistema monoprótico implica:",
     "options":["Un protón intercambiable",
                "Dos protones intercambiables",
                "Tres protones",
                "Ningún protón"],
     "answer":"Un protón intercambiable",
     "explanation":"Un sistema monoprótico dona o acepta un solo protón."},

    {"question":"Un sistema diprótico presenta:",
     "options":["Un equilibrio",
                "Dos etapas de disociación",
                "Un solo punto de equivalencia",
                "Solo precipitación"],
     "answer":"Dos etapas de disociación",
     "explanation":"Un ácido diprótico tiene dos constantes de equilibrio y puede ceder dos protones."},

    {"question":"El modelo de perturbaciones aditivas se usa para:",
     "options":["Resolver sistemas complejos",
                "Medir pH",
                "Calcular pendiente",
                "Medir absorbancia"],
     "answer":"Resolver sistemas complejos",
     "explanation":"Permite analizar sistemas representados por más de una ecuación química."},

    {"question":"En la valoración de mezclas:",
     "options":["Solo hay un punto de equivalencia",
                "Pueden existir múltiples puntos de equivalencia",
                "No ocurre reacción",
                "Siempre hay precipitado"],
     "answer":"Pueden existir múltiples puntos de equivalencia",
     "explanation":"Cada especie puede reaccionar en diferentes etapas."},

    {"question":"La validez de un método volumétrico depende de:",
     "options":["Rapidez y cuantitatividad",
                "Color intenso",
                "Temperatura ambiente",
                "Volumen pequeño"],
     "answer":"Rapidez y cuantitatividad",
     "explanation":"Debe ser rápida y estequiométricamente definida."},

    {"question":"En titulaciones complejas, los errores se minimizan:",
     "options":["Agitando constantemente",
                "Usando indicadores adecuados",
                "Midiendo a ojo",
                "Ignorando el punto de equivalencia"],
     "answer":"Usando indicadores adecuados",
     "explanation":"El uso correcto de indicadores asegura precisión en el punto final."},

    {"question":"El exceso de titulante provoca:",
     "options":["Subestimación de concentración",
                "Sobreestimación de concentración",
                "No altera el resultado",
                "Disolución completa del analito"],
     "answer":"Sobreestimación de concentración",
     "explanation":"Agregar más titulante que lo necesario da una lectura mayor del analito."},

    {"question":"La precisión de una valoración depende de:",
     "options":["Cantidad de analito",
                "Repetición y consistencia de mediciones",
                "Color del recipiente",
                "Tamaño de la pipeta"],
     "answer":"Repetición y consistencia de mediciones",
     "explanation":"Repetir el procedimiento y obtener resultados consistentes aumenta la precisión."},

    {"question":"El indicador ácido-base cambia color según:",
     "options":["pH de la solución",
                "Temperatura",
                "Concentración del titulante",
                "Presión atmosférica"],
     "answer":"pH de la solución",
     "explanation":"El color del indicador depende del pH de la solución durante la valoración."},

    {"question":"En gravimetría, la medición se basa en:",
     "options":["Masa del precipitado",
                "Volumen del líquido",
                "pH de la solución",
                "Temperatura"],
     "answer":"Masa del precipitado",
     "explanation":"Se determina la cantidad de analito por la masa de un precipitado formado."},
]

# =========================
# Aleatorizar preguntas
# =========================
if not st.session_state.question_order:
    st.session_state.question_order = list(range(len(questions)))
    random.shuffle(st.session_state.question_order)

# =========================
# Página Login / Registro diseño
# =========================
if st.session_state.page == "login":
    st.markdown(
        """
        <div style='max-width:500px; margin:auto; padding:30px; border-radius:15px; background-color:#f8f9fa; 
                    box-shadow: 0px 4px 12px rgba(0,0,0,0.15); text-align:center;'>
            <h2 style='color:#4B0082;'>🔐 Curvas & Constantes</h2>
        </div>
        """, unsafe_allow_html=True
    )

    option = st.radio("", ["Login", "Registro"], index=0, horizontal=True)
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    st.markdown("""
        <style>
        .stButton>button {
            background-color:#4B0082;
            color:white;
            height:45px;
            width:100%;
            border-radius:10px;
            font-size:16px;
        }
        </style>
    """, unsafe_allow_html=True)

    if option == "Registro" and st.button("Registrarse"):
        if register_user(username, password):
            st.success("Usuario registrado correctamente")
        else:
            st.error("El usuario ya existe")

    if option == "Login" and st.button("Iniciar sesión"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "diagnostico"
        else:
            st.error("Credenciales incorrectas")

# =========================
# Página Diagnóstico
# =========================
elif st.session_state.page == "diagnostico":
    if not st.session_state.logged_in:
        st.warning("Debes iniciar sesión para acceder al diagnóstico")
        st.stop()

    total = len(st.session_state.question_order)

    if st.session_state.current_question < total:
        idx = st.session_state.question_order[st.session_state.current_question]
        q = questions[idx]

        # Barra de progreso
        progress = (st.session_state.current_question + 1) / total
        st.progress(progress)

        # Tarjeta de pregunta
        st.markdown(
            f"""
            <div style='padding:25px; border-radius:15px; background-color:#e6f2ff; 
                        box-shadow: 0px 4px 12px rgba(0,0,0,0.1); margin-bottom:20px;'>
                <h3 style='color:#4B0082;'>Pregunta {st.session_state.current_question + 1} de {total}</h3>
                <p style='font-size:18px; color:black;'>{q['question']}</p>
            </div>
            """, unsafe_allow_html=True
        )

        # Inicializar estado de respuesta
        if f"answered_{idx}" not in st.session_state:
            st.session_state[f"answered_{idx}"] = False
            st.session_state[f"user_choice_{idx}"] = None

        # Mostrar opciones o feedback
        if not st.session_state[f"answered_{idx}"]:
            choice = st.radio("", q["options"], key=f"radio_{idx}")
            if st.button("Siguiente"):
                if choice is None:
                    st.warning("Selecciona una opción antes de continuar")
                else:
                    st.session_state[f"user_choice_{idx}"] = choice
                    st.session_state[f"answered_{idx}"] = True
                    st.session_state.answers[idx] = choice
        else:
            choice = st.session_state[f"user_choice_{idx}"]
            # Mostrar feedback
            if choice == q["answer"]:
                st.success("✅ Correcto!")
            else:
                st.error(f"❌ Incorrecto! La respuesta correcta es: {q['answer']}")
            st.info(f"💡 Explicación: {q['explanation']}")
            if st.button("Siguiente Pregunta"):
                st.session_state.current_question += 1

    else:
        # Guardar intento del usuario
        save_attempt(st.session_state.username, st.session_state.answers)
        st.session_state.finished = True

    # Resultados finales
    if st.session_state.finished:
        st.markdown(
            """
            <div style='padding:30px; border-radius:15px; background-color:#d1ffd6; 
                        box-shadow: 0px 4px 12px rgba(0,0,0,0.15); margin-top:20px; text-align:center;'>
                <h2 style='color:#008000;'>🏁 Resultados Finales</h2>
            </div>
            """, unsafe_allow_html=True
        )
        correct = sum(1 for i,q in enumerate(questions) if st.session_state.answers.get(i) == q["answer"])
        st.markdown(f"<h3 style='color:white; text-align:center;'>Acertaste <b>{correct}</b> de {len(questions)} preguntas</h3>", unsafe_allow_html=True)

        if st.session_state.username == "admin":
            st.subheader("📊 Intentos de todos los usuarios")
            users = load_users()
            for u, data in users.items():
                st.markdown(f"**{u}**:")
                for attempt in data["attempts"]:
                    score = sum(1 for i,q in enumerate(questions) if attempt.get(i) == q["answer"])
                    st.markdown(f"- {score}/{len(questions)} correctas")

        if st.button("Reiniciar"):
            st.session_state.page = "login"
            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.session_state.finished = False
            st.session_state.question_order = []
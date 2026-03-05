import streamlit as st
import random
import os
import json
from datetime import datetime

# Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# =========================
# Conectar con Google Sheets
# =========================
def connect_sheet():

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        scope
    )

    client = gspread.authorize(creds)

    sheet = client.open("Diagnostico").sheet1

    return sheet


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
# BANCO DE PREGUNTAS
# =========================
questions = [

{"question":"¿Qué define el punto de equivalencia en una valoración?",
"options":["Cuando cambia el color del indicador","Cuando reaccionan cantidades estequiométricamente equivalentes","Cuando el pH es 7","Cuando termina la reacción visualmente"],
"answer":"Cuando reaccionan cantidades estequiométricamente equivalentes",
"explanation":"El punto de equivalencia ocurre cuando las cantidades del analito y titulante reaccionan en proporción estequiométrica."},

{"question":"Una reacción de precipitación se basa en:",
"options":["La formación de un gas","La formación de un sólido insoluble","La neutralización ácido-base","La transferencia de electrones"],
"answer":"La formación de un sólido insoluble",
"explanation":"Las valoraciones por precipitación implican la formación de un compuesto poco soluble."},

{"question":"Las reacciones ácido-base implican:",
"options":["Transferencia de electrones","Transferencia de protones","Formación de complejos","Reacciones redox"],
"answer":"Transferencia de protones",
"explanation":"Según Brønsted-Lowry, un ácido dona protones y una base los acepta."},

{"question":"Las reacciones de óxido-reducción se caracterizan por:",
"options":["Transferencia de protones","Transferencia de electrones","Formación de precipitados","Disolución de sólidos"],
"answer":"Transferencia de electrones",
"explanation":"Las reacciones redox implican intercambio de electrones entre especies."},

{"question":"Una condición de validez de una valoración es:",
"options":["La reacción debe ser lenta","La reacción debe ser cuantitativa","Debe formarse un gas","Debe cambiar el pH"],
"answer":"La reacción debe ser cuantitativa",
"explanation":"Para que una valoración sea válida, la reacción debe ser rápida y cuantitativa."},

{"question":"La ecuación de Nernst se utiliza en:",
"options":["Conductimetría","Potenciometría","Espectrofotometría","Gravimetría"],
"answer":"Potenciometría",
"explanation":"La ecuación de Nernst relaciona el potencial del electrodo con la concentración."},

{"question":"La Ley de Beer establece que:",
"options":["La absorbancia es proporcional a la concentración","La conductividad depende del voltaje","El pH depende del volumen","La pendiente es constante"],
"answer":"La absorbancia es proporcional a la concentración",
"explanation":"A = εbc, la absorbancia es proporcional a la concentración."},

{"question":"La conductimetría se basa en:",
"options":["Medición de absorbancia","Medición de potencial","Medición de conductividad eléctrica","Medición de masa"],
"answer":"Medición de conductividad eléctrica",
"explanation":"La conductimetría mide la capacidad de una solución para conducir corriente eléctrica."},

{"question":"Un electrodo de referencia se caracteriza por:",
"options":["Tener potencial constante","Ser variable","Depender del pH","Medir absorbancia"],
"answer":"Tener potencial constante",
"explanation":"El electrodo de referencia mantiene un potencial conocido y estable."},

{"question":"Una curva de calibración permite:",
"options":["Determinar concentraciones desconocidas","Calcular pH","Determinar masa molar","Medir temperatura"],
"answer":"Determinar concentraciones desconocidas",
"explanation":"Relaciona señal instrumental con concentración del analito."},

{"question":"La TVCM significa:",
"options":["Tabla de Variación de Concentraciones Molares","Titulación Volumétrica de Compuestos Mixtos","Tabla de Valores Constantes Medidos","Técnica Volumétrica de Calibración"],
"answer":"Tabla de Variación de Concentraciones Molares",
"explanation":"Permite seguir el cambio de concentraciones durante la valoración."},

{"question":"En una valoración ácido-base, la curva se sigue mediante:",
"options":["Conductividad","pH-metría","Absorbancia","Gravimetría"],
"answer":"pH-metría",
"explanation":"Se mide el cambio de pH conforme avanza la valoración."},

{"question":"En complejometría se forma:",
"options":["Un precipitado","Un complejo metal-ligando","Un gas","Un ácido fuerte"],
"answer":"Un complejo metal-ligando",
"explanation":"Se forma un complejo estable entre metal y ligando."},

{"question":"Un indicador químico sirve para:",
"options":["Medir temperatura","Detectar el punto final","Medir concentración directa","Determinar masa"],
"answer":"Detectar el punto final",
"explanation":"Permite visualizar el final práctico de la valoración."},

{"question":"Las valoraciones redox pueden seguirse por:",
"options":["Potenciometría","pH-metría","Gravimetría","Filtración"],
"answer":"Potenciometría",
"explanation":"El cambio de potencial permite identificar el punto de equivalencia."},

{"question":"Un sistema monoprótico implica:",
"options":["Un protón intercambiable","Dos protones","Tres protones","Ninguno"],
"answer":"Un protón intercambiable",
"explanation":"Un sistema monoprótico dona o acepta un solo protón."},

{"question":"Un sistema diprótico presenta:",
"options":["Un equilibrio","Dos etapas de disociación","Un punto de equivalencia","Solo precipitación"],
"answer":"Dos etapas de disociación",
"explanation":"Un ácido diprótico puede ceder dos protones."},

{"question":"El modelo de perturbaciones aditivas se usa para:",
"options":["Resolver sistemas complejos","Medir pH","Calcular pendiente","Medir absorbancia"],
"answer":"Resolver sistemas complejos",
"explanation":"Permite analizar sistemas con varias ecuaciones químicas."},

{"question":"En la valoración de mezclas:",
"options":["Hay un punto de equivalencia","Pueden existir múltiples puntos","No ocurre reacción","Siempre precipita"],
"answer":"Pueden existir múltiples puntos",
"explanation":"Cada especie reacciona en etapas diferentes."},

{"question":"La validez de un método volumétrico depende de:",
"options":["Rapidez y cuantitatividad","Color intenso","Temperatura ambiente","Volumen pequeño"],
"answer":"Rapidez y cuantitatividad",
"explanation":"La reacción debe ser rápida y completa."},

{"question":"Los errores en titulaciones complejas se minimizan:",
"options":["Agitando constantemente","Usando indicadores adecuados","Midiendo a ojo","Ignorando equivalencia"],
"answer":"Usando indicadores adecuados",
"explanation":"Indicadores correctos aumentan precisión."},

{"question":"El exceso de titulante provoca:",
"options":["Subestimación","Sobreestimación","No afecta","Disolución completa"],
"answer":"Sobreestimación",
"explanation":"Más titulante del necesario aumenta el resultado."},

{"question":"La precisión depende de:",
"options":["Cantidad de analito","Repetición y consistencia","Color del recipiente","Tamaño de pipeta"],
"answer":"Repetición y consistencia",
"explanation":"Resultados consistentes aumentan precisión."},

{"question":"El indicador ácido-base cambia color según:",
"options":["pH","Temperatura","Concentración","Presión"],
"answer":"pH",
"explanation":"El color depende del pH."},

{"question":"En gravimetría la medición se basa en:",
"options":["Masa del precipitado","Volumen","pH","Temperatura"],
"answer":"Masa del precipitado",
"explanation":"Se determina analito por masa del precipitado."}

]


# =========================
# Aleatorizar preguntas
# =========================
if not st.session_state.question_order:
    st.session_state.question_order = list(range(len(questions)))
    random.shuffle(st.session_state.question_order)


# =========================
# LOGIN
# =========================
if st.session_state.page == "login":

    st.title("🔐 Curvas & Constantes")

    option = st.radio("", ["Login", "Registro"], horizontal=True)

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if option == "Registro":

        if st.button("Registrarse"):

            if register_user(username, password):
                st.success("Usuario registrado")
            else:
                st.error("El usuario ya existe")

    if option == "Login":

        if st.button("Iniciar sesión"):

            if login_user(username, password):

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "diagnostico"
                st.rerun()

            else:

                st.error("Credenciales incorrectas")


# =========================
# DIAGNOSTICO
# =========================
elif st.session_state.page == "diagnostico":

    total = len(st.session_state.question_order)

    if st.session_state.current_question < total:

        idx = st.session_state.question_order[st.session_state.current_question]
        q = questions[idx]

        st.progress((st.session_state.current_question+1)/total)

        st.subheader(f"Pregunta {st.session_state.current_question+1}")

        choice = st.radio(q["question"], q["options"])

        if st.button("Responder"):

            st.session_state.answers[idx] = choice

            if choice == q["answer"]:
                st.success("✅ Correcto")
            else:
                st.error(f"❌ Incorrecto. Correcta: {q['answer']}")

            st.info(q["explanation"])

            st.session_state.current_question += 1
            st.rerun()

    else:

        save_attempt(st.session_state.username, st.session_state.answers)

        correct = sum(
            1 for i,q in enumerate(questions)
            if st.session_state.answers.get(i) == q["answer"]
        )

        try:

            sheet = connect_sheet()

            fila = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                st.session_state.username,
                correct
            ]

            for i,q in enumerate(questions):

                respuesta = st.session_state.answers.get(i,"")

                if respuesta == q["answer"]:
                    estado = "Correcta"
                else:
                    estado = "Incorrecta"

                fila.append(respuesta)
                fila.append(estado)

            sheet.append_row(fila)

        except Exception as e:

            st.error("Error guardando en Google Sheets")
            st.write(e)

        st.success(f"Resultado final: {correct}/{len(questions)}")

        if st.button("Reiniciar"):

            st.session_state.page="login"
            st.session_state.current_question=0
            st.session_state.answers={}
            st.session_state.question_order=[]
            st.rerun()


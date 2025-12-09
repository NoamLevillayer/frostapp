import streamlit as st
import matplotlib.pyplot as plt
from utils.function import *
import base64

import base64

def background_gif(gif_path: str) -> str:
    with open(gif_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    return f"data:image/gif;base64,{encoded}"

def set_dark_theme():
    gif_url = background_gif("snow02.gif")  # local file

    dark_css = f"""
    <style>
    .stApp {{
        background-image: url("{gif_url}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-color: #000000; /* fallback */
        color: #e0e0e0;
    }}

    /* Semi-transparent panel to help readability */
    .block-container {{
        background-color: rgba(0, 0, 0, 0.65);
        padding-top: 2rem;
        padding-bottom: 2rem;
        border-radius: 12px;
    }}
    </style>
    """
    st.markdown(dark_css, unsafe_allow_html=True)


set_dark_theme()


icy_blue = "#7fd3ff"

st.markdown(
    f"""
    <h1 style='text-align: center; color: {icy_blue}; font-weight: 700;'>
       ❄️ Analyse des jours de gel en France ❄️
    </h1>
    """,
    unsafe_allow_html=True
)

commune = st.text_input("Nom de la commune", "Marseille")
code_postal = st.number_input("Code postal (optionnel)", min_value=1000, max_value=95999, value=None, step=1)

if st.button("Analyser"):
    
    with st.spinner('Récupération des données météo...'):
        
     try:
            if code_postal:
                coords = get_coordinates(commune, int(code_postal))
            else:
                coords = get_coordinates(commune)
            
            temp_df = get_temperature_data(coords)
            
            if temp_df is None:
                st.error("Aucune donnée météo disponible.")
                st.stop()
                
     except ValueError as e:
            if "Plusieurs communes" in str(e):
                st.warning(str(e))
                result = df[df['nom_standard'] == commune]
                st.dataframe(result[['nom_standard', 'code_postal', 'dep_code']])
            else:
                st.error(str(e))
            st.stop()
    # Statistiques par année
    frost_stats = display_frost_statistics(temp_df)
    st.dataframe(frost_stats, use_container_width=True)
    
    # Probabilité par jour de l'année
    frost_prob = calculate_frost_probability(temp_df)
    

    plt.style.use("default")
    bg_color = "#0a0a0f"         # background
    line_color = "#7fd3ff"       # icy blue
    fill_color = "#7fd3ff"
    grid_color = "#444a5a"
    text_color = "#e0e0e0"

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")

    x = frost_prob['day_of_year']
    y = frost_prob['frost_probability']

    # --- GLOW: multiple lines with increasing width & transparency ---
    for lw, alpha in [(10, 0.05), (8, 0.08), (6, 0.12)]:
        ax.plot(
            x, y,
            linewidth=lw,
            color=line_color,
            alpha=alpha,
            solid_capstyle="round"
        )

    # --- MAIN LINE ---
    ax.plot(
        x, y,
        linewidth=2.5,
        color=line_color,
        solid_capstyle="round"
    )

    # --- FILLED AREA ---
    ax.fill_between(
        x, y,
        alpha=0.20,
        color=fill_color
    )

    # --- Labels & title ---
    ax.set_xlabel("Jour de l'année", color=text_color, fontsize=12)
    ax.set_ylabel("Probabilité de gel (%)", color=text_color, fontsize=12)
    ax.set_title(
    f"Probabilité de gel à {commune} (2013-2024)",
    color=line_color,      # use the same icy blue
    fontsize=16,
    fontweight="bold",
    pad=12)

    # --- Axes styling ---
    ax.tick_params(colors=text_color, labelsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ["bottom", "left"]:
        ax.spines[spine].set_color(text_color)

    ax.grid(False)

    ax.set_xlim(1, 366)
    ax.set_ylim(0, 100)

    month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    ax.set_xticks(month_starts)
    ax.set_xticklabels(month_names, color=text_color)

    st.pyplot(fig)
    plt.close()

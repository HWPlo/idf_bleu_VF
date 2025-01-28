import plotly.express as px
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pydeck as pdk
import os
###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################

st.set_page_config(page_title="Dashboard Ile-de-France ", page_icon="logoSNCF", layout="centered", initial_sidebar_state="auto", menu_items=None)



@st.cache_data
def load_data():
    # Chemin principal : dossier contenant le script actuel
    pathway = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    # Chargement des fichiers en construisant dynamiquement les chemins
    df1 = pd.read_csv(os.path.join(pathway, "accessibilite-en-gare.csv"), sep=';')
    df2 = pd.read_csv(os.path.join(pathway, "accompagnement-pmr-gares.csv"), sep=';')
    df5 = pd.read_csv(os.path.join(pathway, "gares-equipees-du-wifi.csv"), sep=';')
    df4 = pd.read_csv(os.path.join(pathway, "equipements-accessibilite-en-gares.csv"), sep=';')
    df6 = pd.read_csv(os.path.join(pathway, "liste-des-gares.csv"), sep=';')
    df7 = pd.read_csv(os.path.join(pathway, "parking-velos-ile-de-france-mobilites.csv"), sep=';')
    df3 = pd.read_csv(os.path.join(pathway, "arrets-transporteur.csv"), sep=';')

    # Préparer les coordonnées géographiques de l'accessibilité
    df1[["latitude", "longitude"]] = df1["stop_point_geopoint"].str.split(", ", expand=True).astype(float)

    # Charger et nettoyer le fichier principal
    df = pd.read_csv(os.path.join(pathway, "df_merged6.csv"), sep=',')
    df = df.drop(columns=['Has_Bike_Parking_Within_500m'], errors='ignore')
    df.rename(columns={"Rampe et  fauteuil": "Rampe et fauteuil"}, inplace=True)

    return df1, df2, df3, df4, df5, df6, df7, df

# Appeler la fonction pour charger les données
df1, df2, df3, df4, df5, df6, df7, df = load_data()
@st.cache_data
def load_and_process_data(df):
    # Charger les données
    
    # Valeurs invalides
    invalid_values = ["aucune donnée", "Aucune donnée", "Non", 0, "nan", np.nan]
    
    # Création des nouvelles colonnes
    df["ASSISTANCE_GENERALE"] = df[
        [
            "PRESENCE_PERSONNEL",
            "ASSISTANCE_ACCES_QUAIS",
        ]
    ].apply(lambda row: any(val not in invalid_values for val in row), axis=1)

    df["ASSISTANCE_SONORE"] = df[
        ["INFO_SONORE_GARE", "BOUCLE_INDUCTION_MAGNETIQUE", "ArTAudibleSignals"]
    ].apply(lambda row: any(val not in invalid_values for val in row), axis=1)

    df["ASSISTANCE_VISUEL"] = df[
        ["ECRAN_INFO_GARE", "BANDE_EVEIL_VIGILANCE", "ArTVisualSigns"]
    ].apply(lambda row: any(val not in invalid_values for val in row), axis=1)

    df["ASSISTANCE_MOBILITE"] = df[
        [
            "ACCES_ASCENSEUR_RAMPE",
            "FAUTEUIL_ROULANT_DISPONIBLE",
            "Rampe",
            "Fauteuil",
            "Rampe et fauteuil",
            "ArTAccessibility",
            "access_gare ou arrêt non accessible",
        ]
    ].apply(lambda row: any(val not in invalid_values for val in row), axis=1)

    # Convertir les colonnes en booléens pour plus de clarté
    df[["ASSISTANCE_GENERALE", "ASSISTANCE_SONORE", "ASSISTANCE_VISUEL", "ASSISTANCE_MOBILITE"]] = df[
        ["ASSISTANCE_GENERALE", "ASSISTANCE_SONORE", "ASSISTANCE_VISUEL", "ASSISTANCE_MOBILITE"]
    ].astype(bool)

    return df
df = load_and_process_data(df)    
###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################
###############################################################################################

st.markdown(
    '<h1 style="color:black; text-align: center;"> Accessibilité <span style="color:#7B152A;">Ile-de-France</span> 🚅</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div style="text-align: justify; font-family: 'Arial', sans-serif; line-height: 1.6; font-size: 16px; color: #333; margin: 20px 0;">
    Cette application a été pensée pour offrir aux collectivités locales les outils nécessaires à une prise de décision éclairée sur l’accessibilité des gares et équipements.<br><br>
    Son objectif ? Révolutionner l’expérience des utilisateurs de transports en commun en la rendant plus fluide, pratique et inclusive.<br><br>
    
    </div>
    """, 
    unsafe_allow_html=True
)



# Organisation des filtres dans la barre latérale
st.sidebar.header("Filtres")

# 1. Filtre par département (sidebar)
selected_departement = st.sidebar.selectbox(
    "Département",
    options=["Tous les départements"] + df["DEPARTEMENT"].unique().tolist()
)

# 2. Filtre par commune (sidebar) en fonction du département sélectionné
if selected_departement and selected_departement != "Tous les départements":
    communes_du_departement = df[df["DEPARTEMENT"] == selected_departement]["COMMUNE"].unique().tolist()
    selected_commune = st.sidebar.selectbox(
        "Commune",
        options=["Toutes les communes"] + communes_du_departement
    )
else:
    selected_commune = st.sidebar.selectbox(
        "Commune",
        options=["Toutes les communes"] + df["COMMUNE"].unique().tolist()
    )

# 3. Filtre par gare (sidebar) en fonction de la commune sélectionnée
if selected_commune and selected_commune != "Toutes les communes":
    gares_de_la_commune = df[df["COMMUNE"] == selected_commune]["LIBELLE"].unique().tolist()
    selected_label = st.sidebar.selectbox(
        "Rechercher une gare",
        options=["Toutes les gares"] + gares_de_la_commune
    )
else:
    selected_label = st.sidebar.selectbox(
        "Rechercher une gare",
        options=["Toutes les gares"] + df["LIBELLE"].unique().tolist()
    )

# Filtrage des données en fonction des sélections
filtered_df = df.copy()

if selected_departement and selected_departement != "Tous les départements":
    filtered_df = filtered_df[filtered_df["DEPARTEMENT"] == selected_departement]

if selected_commune and selected_commune != "Toutes les communes":
    filtered_df = filtered_df[filtered_df["COMMUNE"] == selected_commune]

if selected_label and selected_label != "Toutes les gares":
    filtered_df = filtered_df[filtered_df["LIBELLE"] == selected_label]


# Onglets
tab1, tab2, tab3, tab4,tab5 = st.tabs(
    ["Carte d'accessibilité", "Accessibilité PMR", "Assistance", "Equipements","Sources"]
)


with tab1:
    st.markdown(
        '<h3 style="color:black; text-align: center;">Carte des gares d\'<span style="color:#7B152A;">Île-de-France</span> selon <span style="color:#F3A847 ;">l\'accessibilité</span></h3>',
        unsafe_allow_html=True,
    )

    # Définir les couleurs selon le niveau d'accessibilité
    color_scale = {
        1: [255, 0, 0],        # Niveau 1 : Rouge (très mauvais)
        2: [255, 165, 0],      # Niveau 2 : Orange (mauvais)
        3: [255, 255, 0],      # Niveau 3 : Jaune (modéré)
        4: [0, 128, 0],        # Niveau 4 : Vert (bon)
        5: [0, 255, 0],        # Niveau 5 : Vert clair (très bon)
        6: [0, 191, 255],      # Niveau 6 : Bleu clair (excellent)
    }

    # Appliquer la couleur à chaque gare selon son niveau d'accessibilité
    df1["color"] = df1["accessibility_level_id"].map(color_scale)

    # Créer les colonnes
    col1, col2, col3 = st.columns(3)


    # Ajouter un filtre pour les niveaux d'accessibilité (sélection multiple) dans col1
    with col3:
        accessibility_filter = st.multiselect(
            "Filtrer par niveaux d'accessibilité",
            options=["Niveau 1", "Niveau 2", "Niveau 3", "Niveau 4", "Niveau 5", "Niveau 6"],
            default=[]  # Sélection par défaut (vide pour tout afficher)
        )

    # Mapping entre les noms et les IDs
    level_map = {
        "Niveau 1": 1,
        "Niveau 2": 2,
        "Niveau 3": 3,
        "Niveau 4": 4,
        "Niveau 5": 5,
        "Niveau 6": 6
    }

    # Filtrer les données en fonction des niveaux d'accessibilité sélectionnés
    if not accessibility_filter:
        filtered_df = df1
    else:
        selected_levels = [level_map[level] for level in accessibility_filter]
        filtered_df = df1[df1["accessibility_level_id"].isin(selected_levels)]

    # Liste des gares disponibles après filtrage
    gares_de_l_accessibilite = filtered_df["stop_name"].unique().tolist()

    # Ajouter un champ pour rechercher une gare dans col2
    with col3:
        selected_label2 = st.selectbox(
            "Rechercher une gare",
            options=["Toutes les gares"] + gares_de_l_accessibilite
        )

    # Filtrer encore les données en fonction de la gare sélectionnée
    if selected_label2 != "Toutes les gares":
        filtered_df = filtered_df[filtered_df["stop_name"] == selected_label2]

    # KPI : Nombre de gares affichées
    kpi = len(filtered_df)

    # KPI pour les gares avec niveau d'accessibilité 1
    filtered_df1 = df1[df1["accessibility_level_id"] == 1]
    kpi_access_1 = len(filtered_df1)

    # Affichage des KPI dans col1 et col2
    with col1:
        st.markdown(
            f"""
            <div style="background-color:#F7F8FA; padding: 8px 12px; border-radius: 8px; color: black; text-align: center;">
                <h3 style="margin: 0; font-size: 14px; color: #9B1B30;">Nombre de gares affichées</h3>
                <h2 style="margin: 0; font-size: 24px; font-weight: bold; color: #7B152A;">{kpi}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        if accessibility_filter or selected_label2 != "Toutes les gares":
            # Masquer col2 si des filtres sont sélectionnés
            st.empty()
        else:
            st.markdown(
                f"""
                <div style="background-color:#F7F8FA; padding: 8px 12px; border-radius: 8px; color: black; text-align: center;">
                    <h3 style="margin: 0; font-size: 14px; color: #9B1B30;">Gares non accessibles</h3>
                    <h2 style="margin: 0; font-size: 24px; font-weight: bold; color: #7B152A;">{kpi_access_1}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )
    # Sélecteurs de filtres dans col3

    # Pydeck : Création de la carte
    view_state = pdk.ViewState(
        latitude=filtered_df["latitude"].mean(),
        longitude=filtered_df["longitude"].mean(),
        zoom=9,
        pitch=40,
    )

    # Ajouter les points sur la carte
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position="[longitude, latitude]",
        get_color="color",
        get_radius=150,
        pickable=True,
        tooltip=True,
    )

    # Info-bulle avec le niveau d'accessibilité
    tooltip = {
        "html": "<b>Gare :</b> {stop_name} <br><b>Accessibilité :</b> {accessibility_level_name} (Niveau {accessibility_level_id})",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }

    # Créer la carte avec la couche d'info-bulle
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)

    # Afficher la carte
    st.pydeck_chart(r)
    
with tab2:
    # Filtrage des données en fonction des sélections
    filtered_df = df.copy()
    
    if selected_departement and selected_departement != "Tous les départements":
        filtered_df = filtered_df[filtered_df["DEPARTEMENT"] == selected_departement]
    
    if selected_commune and selected_commune != "Toutes les communes":
        filtered_df = filtered_df[filtered_df["COMMUNE"] == selected_commune]
    
    if selected_label and selected_label != "Toutes les gares":
        filtered_df = filtered_df[filtered_df["LIBELLE"] == selected_label]

    # Calculer les KPI
    total_gares = len(filtered_df)
    gares_avec_rampe = len(filtered_df[filtered_df["Rampe"] > 0])
    gares_avec_fauteuil = len(filtered_df[filtered_df["Fauteuil"] > 0])
    gares_avec_assistance2 = len(filtered_df[filtered_df["Assistance simple"] > 0])
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
        f"""
        <div style="background-color:#F7F8FA; padding: 8px 12px; border-radius: 8px; color: black; text-align: center; margin-bottom: 20px;">
            <h3 style="margin: 0; font-size: 14px; color: #9B1B30;">Nombre de gares</h3>
            <h2 style="margin: 0; font-size: 24px; font-weight: bold; color: #7B152A;">{total_gares}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with col2:
        colonnes_assistance = ["Rampe", "Fauteuil", "Assistance simple"]  # Ajoutez d'autres colonnes si nécessaire
        gares_sans_données = filtered_df[colonnes_assistance].isnull().any(axis=1).sum()
        st.markdown(
            f"""
            <div style="background-color:#F7F8FA; padding: 8px 12px; border-radius: 8px; color: black; text-align: center; margin-bottom: 20px;">
                <h3 style="margin: 0; font-size: 14px; color: #9B1B30;">Gares sans données</h3>
                <h2 style="margin: 0; font-size: 24px; font-weight: bold; color: #7B152A;">{gares_sans_données}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div style="background-color:#F7F8FA; padding: 8px 12px; border-radius: 8px; color: black; text-align: center; margin-bottom: 20px;">
                <h3 style="margin: 0; font-size: 14px; color: #9B1B30;">Gares avec rampe</h3>
                <h2 style="margin: 0; font-size: 24px; font-weight: bold; color: #7B152A;">{gares_avec_rampe}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background-color:#F7F8FA; padding: 8px 12px; border-radius: 8px; color: black; text-align: center; margin-bottom: 20px;">
                <h3 style="margin: 0; font-size: 14px; color: #9B1B30;">Gares avec fauteuil</h3>
                <h2 style="margin: 0; font-size: 24px; font-weight: bold; color: #7B152A;">{gares_avec_fauteuil}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
         st.markdown(
             f"""
             <div style="background-color:#F7F8FA; padding: 8px 12px; border-radius: 8px; color: black; text-align: center; margin-bottom: 20px;">
                 <h3 style="margin: 0; font-size: 14px; color: #9B1B30;">Gares avec assistance</h3>
                 <h2 style="margin: 0; font-size: 24px; font-weight: bold; color: #7B152A;">{gares_avec_assistance2}</h2>
             </div>
             """,
             unsafe_allow_html=True
         )

    # Calculer les top gares avec rampes
    top_gares_rampe = (
        filtered_df[filtered_df["Rampe"] > 0]
        .groupby("LIBELLE")["Rampe"]
        .sum()
        .sort_values(ascending=False)
        .head(10)  # Top 10
        .reset_index()
    )
    
    # Calculer les top gares avec fauteuils
    top_gares_fauteuil = (
        filtered_df[filtered_df["Fauteuil"] > 0]
        .groupby("LIBELLE")["Fauteuil"]
        .sum()
        .sort_values(ascending=False)
        .head(10)  # Top 10
        .reset_index()
    )
    
    # Créer les graphiques
    fig_rampe = px.bar(
        top_gares_rampe,
        x="Rampe",
        y="LIBELLE",
        orientation="h",
        title="Top des gares avec rampes",
        labels={"LIBELLE": "", "Rampe": "Rampes"},
        color="Rampe",
        color_continuous_scale="sunsetdark",
    )
    
    fig_fauteuil = px.bar(
        top_gares_fauteuil,
        x="Fauteuil",
        y="LIBELLE",
        orientation="h",
        title="Top des gares avec fauteuils",
        labels={"LIBELLE": "", "Fauteuil": "Fauteuils"},
        color="Fauteuil",
        color_continuous_scale="sunset",
    )
    fig_assistance = px.bar(
        top_gares_fauteuil,
        x="Fauteuil",
        y="LIBELLE",
        orientation="h",
        title="Top des gares avec fauteuils",
        labels={"LIBELLE": "", "Fauteuil": "Fauteuils"},
        color="Fauteuil",
        color_continuous_scale="sunset",
    )
    # Calculer les top gares avec assistance simple
    top_gares_assistance = (
        filtered_df[filtered_df["Assistance simple"] > 0]
        .groupby("LIBELLE")["Assistance simple"]
        .sum()
        .sort_values(ascending=False)
        .head(10)  # Top 10
        .reset_index()
    )

    # Créer le graphique pour "Assistance simple"
    fig_assistance = px.bar(
        top_gares_assistance,
        x="Assistance simple",
        y="LIBELLE",
        orientation="h",
        title="Top des gares avec assistance simple",
        labels={"LIBELLE": "", "Assistance simple": "Assistance"},
        color="Assistance simple",
        color_continuous_scale="peach",
    )
    col1, col2= st.columns(2)
    # Ajout des graphiques dans les colonnes
    with col1:
        st.plotly_chart(fig_rampe, use_container_width=True)
    
    with col2:
        st.plotly_chart(fig_fauteuil, use_container_width=True)
    # Calculer le nombre de lignes avec None dans les colonnes spécifiques

    st.plotly_chart(fig_assistance, use_container_width=True)


   
with tab3:

    filtered_df = df.copy()
    if selected_departement and selected_departement != "Tous les départements":
        filtered_df = filtered_df[filtered_df["DEPARTEMENT"] == selected_departement]
    
    if selected_commune and selected_commune != "Toutes les communes":
        filtered_df = filtered_df[filtered_df["COMMUNE"] == selected_commune]
    
    if selected_label and selected_label != "Toutes les gares":
        filtered_df = filtered_df[filtered_df["LIBELLE"] == selected_label]
    # Filtrage des données en fonction des sélections


    
    # 3. Calcul du pourcentage de "Oui" dans chaque colonne
    columns = ["ASSISTANCE_GENERALE", "ASSISTANCE_SONORE", "ASSISTANCE_VISUEL", "ASSISTANCE_MOBILITE"]
    col1, col2, col3, col4 = st.columns(4)
    # Distribution des KPI sur les colonnes
    for i, column in enumerate(columns):
        # Comptage des valeurs "Oui" et "Non"
        counts = filtered_df[column].value_counts(normalize=True)  # normalize pour obtenir des pourcentages
        percentage_oui = counts.get(True, 0) * 100  # Calculer le pourcentage de "Oui"

        # Construction du style HTML pour chaque KPI
        kpi_html = f"""
        <div style="background-color:#F7F8FA; padding: 8px 12px; border-radius: 8px; color: black; text-align: center; margin-bottom: 20px;">
            <h3 style="margin: 0; font-size: 14px; color: #9B1B30;">{column.replace('_', ' ').title()}</h3>
            <h2 style="margin: 0; font-size: 24px; font-weight: bold; color: #7B152A;">{percentage_oui:.1f}%</h2>
        </div>
        """

        # Distribution des KPI entre les colonnes
        if i == 0:
            with col1:
                st.markdown(kpi_html, unsafe_allow_html=True)
        elif i == 1:
            with col2:
                st.markdown(kpi_html, unsafe_allow_html=True)
        elif i == 2:
            with col3:
                st.markdown(kpi_html, unsafe_allow_html=True)
        else:
            with col4:
                st.markdown(kpi_html, unsafe_allow_html=True)
    # Choisir la colonne à afficher
    col1,col2 = st.columns(2)
    with col1:
        selected_column = st.selectbox(
            "Choisissez une variable à afficher :",
            options=["ASSISTANCE_GENERALE", "ASSISTANCE_SONORE", "ASSISTANCE_VISUEL", "ASSISTANCE_MOBILITE"],
            key="selected_variable"
        )
        
    # Calcul des valeurs "Oui" et "Non" par département pour la colonne sélectionnée
    stacked_data = (
        df.groupby(["DEPARTEMENT", selected_column])
        .size()
        .unstack(fill_value=0)
        .rename(columns={True: "Oui", False: "Non/Aucune donnée"})
    )
    
    # Ajouter une colonne "Total" pour calculer le nombre total de réponses par département
    stacked_data["Total"] = stacked_data["Oui"] + stacked_data["Non/Aucune donnée"]
    
    # Trier les départements par nombre total de réponses (descendant)
    stacked_data = stacked_data.sort_values(by="Total", ascending=False)
    
    # Retirer la colonne "Total" (elle n'est pas nécessaire pour le graphique)
    stacked_data = stacked_data.drop(columns=["Total"])
    
    # Création du graphique de type barre empilée (horizontal)
    fig, ax = plt.subplots(figsize=(8, 6))
    stacked_data.plot(kind="barh", stacked=True, color=["#9B1B30", "#F3A847"], ax=ax)
    
    # Inverser l'axe Y pour afficher les départements avec le plus de réponses en haut
    ax.invert_yaxis()
    
    # Ajout des détails du graphique
    ax.set_title(f"Répartition de l'{selected_column.replace('_', ' ').title()} par département")
    ax.set_xlabel("Nombre de réponses")
    ax.set_ylabel("")
    ax.legend(title="Réponses", loc="lower right")
    plt.xticks(rotation=0)
    
    # Afficher le graphique dans Streamlit
    st.pyplot(fig)

with tab4:  

    # Filtrage des données en fonction des sélections
    filtered_df = df.copy()

    if selected_departement and selected_departement != "Tous les départements":
        filtered_df = filtered_df[filtered_df["DEPARTEMENT"] == selected_departement]

    if selected_commune and selected_commune != "Toutes les communes":
        filtered_df = filtered_df[filtered_df["COMMUNE"] == selected_commune]

    if selected_label and selected_label != "Toutes les gares":
        filtered_df = filtered_df[filtered_df["LIBELLE"] == selected_label]

    # Fonction pour tracer la carte
    def plot_map(filtered_df, service_choice):


        # Extraire la latitude et la longitude à partir de GEO_POINT
        filtered_df[['latitude', 'longitude']] = filtered_df['GEO_POINT'].str.split(',', expand=True)
        filtered_df['latitude'] = filtered_df['latitude'].astype(float)
        filtered_df['longitude'] = filtered_df['longitude'].astype(float)

        # Définir les couleurs selon le service choisi
        def get_color(row):
            if service_choice == "Aucun":
                return [255, 255, 255]  # Blanc pour toutes les gares si aucun service n'est sélectionné
            elif service_choice == "Wifi":
                if row['Service Wifi'] == 'Oui':
                    return [94, 197, 96]  # Vert pour les gares avec Wifi
                else:
                    return [243, 60, 60]  # Rouge pour les gares sans Wifi
            elif service_choice == "Velo":
                if row['Has_Bike_Parking_Within_250m'] == 'Oui':
                    return [94, 197, 96]  # Vert pour les gares avec parking à vélo < 250m
                else:
                    return [243, 60, 60]  # Rouge pour les gares sans parking à vélo
            elif service_choice == "Toilettes":
                if row['TOILETTES'] == 'Oui':
                    return [94, 197, 96]  # Vert pour les gares avec toilettes
                else:
                    return [243, 60, 60]  # Rouge pour les gares sans toilettes
            elif service_choice == "Accès ascenseur/rampe":
                if row['ACCES_ASCENSEUR_RAMPE'] == 'Oui':
                    return [94, 197, 96]  # Vert pour les gares avec ascenseur ou rampe
                else:
                    return [243, 60, 60]  # Rouge pour les gares sans ascenseur ou rampe
            elif service_choice == "Toilettes accessibles":
                if row['TOILETTES_ACCESSIBLE'] == 'Oui':
                    return [94, 197, 96]  # Vert pour les gares avec toilettes accessibles
                else:
                    return [243, 60, 60]  # Rouge pour les gares sans toilettes accessibles
            elif service_choice == "Fauteuil roulant disponible":
                if row['FAUTEUIL_ROULANT_DISPONIBLE'] == 'Oui':
                    return [94, 197, 96]  # Vert pour les gares avec fauteuil roulant disponible
                else:
                    return [243, 60, 60]  # Rouge pour les gares sans fauteuil roulant disponible

        filtered_df['color'] = filtered_df.apply(get_color, axis=1)

        # Créer une carte avec un fond sombre
        view_state = pdk.ViewState(
            latitude=filtered_df["latitude"].mean(),
            longitude=filtered_df["longitude"].mean(),
            zoom=9,
            pitch=40,
        )

        # Ajouter les marqueurs sur la carte
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position="[longitude, latitude]",
            get_color="color",  # Utiliser la colonne 'color' pour définir la couleur des marqueurs
            get_radius=100,
            pickable=True,
            tooltip=True,
        )

        # Créer la carte avec un fond sombre
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
        )

        return r

    # Titre de la carte
    st.markdown(
        '<h3 style="color:black; text-align: center;">Les gares d\'<span style="color:#7B152A;">Île-de-France</span> selon l\'<span style="color:#F3A847;">aménagement</span></h3>',
        unsafe_allow_html=True,
    )

    # Ajouter un selectbox pour choisir entre "Wifi", "Velo", "Toilettes", "Accès ascenseur/rampe", "Toilettes accessibles", ou "Fauteuil roulant disponible"
    col1, col2 = st.columns(2)
    with col1:
        service_choice = st.selectbox(
            "Choisissez un service",
            options=["Aucun", "Wifi", "Velo", "Toilettes", "Accès ascenseur/rampe", "Toilettes accessibles", "Fauteuil roulant disponible", "Présence personnel", "Boucle induction magnétique"]
        )
    
    with col2:
        if service_choice == "Wifi":
            # Filtrer les gares ayant le service Wifi
            wifi_filter = st.radio(
                "Filtrer les gares par Service Wifi",
                options=["Tout", "Avec Wifi", "Sans Wifi"],
            )
        elif service_choice == "Velo":
            # Filtrer les gares par parking à vélo
            parking_filter = st.selectbox(
                "Filtrer les gares par parking à vélo",
                options=["Tout", "Avec parking à vélo", "Sans parking à vélo"],
            )
        elif service_choice == "Toilettes":
            # Filtrer les gares par toilettes
            toilets_filter = st.radio(
                "Filtrer les gares par Toilettes",
                options=["Tout", "Avec toilettes", "Sans toilettes"],
            )
        elif service_choice == "Accès ascenseur/rampe":
            # Filtrer les gares par accès ascenseur ou rampe
            ascenseur_filter = st.radio(
                "Filtrer les gares par accès ascenseur/rampe",
                options=["Tout", "Avec ascenseur ou rampe", "Sans ascenseur ni rampe"],
            )
        elif service_choice == "Toilettes accessibles":
            # Filtrer les gares par toilettes accessibles
            accessible_toilets_filter = st.radio(
                "Filtrer les gares par Toilettes accessibles",
                options=["Tout", "Avec toilettes accessibles", "Sans toilettes accessibles"],
            )
        elif service_choice == "Fauteuil roulant disponible":
            # Filtrer les gares par fauteuil roulant disponible
            wheelchair_filter = st.radio(
                "Filtrer les gares par fauteuil roulant disponible",
                options=["Tout", "Avec fauteuil roulant disponible", "Sans fauteuil roulant disponible"],
            )
        elif service_choice == "Présence personnel":
            # Filtrer les gares par présence de personnel
            personnel_filter = st.radio(
                "Filtrer les gares par présence de personnel",
                options=["Tout", "Avec personnel", "Sans personnel"],
            )
        elif service_choice == "Boucle induction magnétique":
            # Filtrer les gares par boucle d'induction magnétique
            induction_filter = st.radio(
                "Filtrer les gares par Boucle d'induction magnétique",
                options=["Tout", "Avec boucle induction magnétique", "Sans boucle induction magnétique"],
            )
    
    # Appliquer le filtre basé sur le choix de service
    if service_choice == "Wifi":
        if wifi_filter == "Avec Wifi":
            filtered_df = filtered_df[filtered_df['Service Wifi'] == 'Oui']
        elif wifi_filter == "Sans Wifi":
            filtered_df = filtered_df[filtered_df['Service Wifi'] == 'Non']
    elif service_choice == "Velo":
        if parking_filter == "Avec parking à vélo":
            filtered_df = filtered_df[filtered_df['Has_Bike_Parking_Within_250m'] == 'Oui']
        elif parking_filter == "Sans parking à vélo":
            filtered_df = filtered_df[filtered_df['Has_Bike_Parking_Within_250m'] == 'Non']
    elif service_choice == "Toilettes":
        if toilets_filter == "Avec toilettes":
            filtered_df = filtered_df[filtered_df['TOILETTES'] == 'Oui']
        elif toilets_filter == "Sans toilettes":
            filtered_df = filtered_df[filtered_df['TOILETTES'] == 'Non']
    elif service_choice == "Accès ascenseur/rampe":
        if ascenseur_filter == "Avec ascenseur ou rampe":
            filtered_df = filtered_df[filtered_df['ACCES_ASCENSEUR_RAMPE'] == 'Oui']
        elif ascenseur_filter == "Sans ascenseur ni rampe":
            filtered_df = filtered_df[filtered_df['ACCES_ASCENSEUR_RAMPE'] == 'Non']
    elif service_choice == "Toilettes accessibles":
        if accessible_toilets_filter == "Avec toilettes accessibles":
            filtered_df = filtered_df[filtered_df['TOILETTES_ACCESSIBLE'] == 'Oui']
        elif accessible_toilets_filter == "Sans toilettes accessibles":
            filtered_df = filtered_df[filtered_df['TOILETTES_ACCESSIBLE'] == 'Non']
    elif service_choice == "Fauteuil roulant disponible":
        if wheelchair_filter == "Avec fauteuil roulant disponible":
            filtered_df = filtered_df[filtered_df['FAUTEUIL_ROULANT_DISPONIBLE'] == 'Oui']
        elif wheelchair_filter == "Sans fauteuil roulant disponible":
            filtered_df = filtered_df[filtered_df['FAUTEUIL_ROULANT_DISPONIBLE'] == 'Non']
    elif service_choice == "Présence personnel":
        if personnel_filter == "Avec personnel":
            filtered_df = filtered_df[filtered_df['PRESENCE_PERSONNEL'] == 'Oui']
        elif personnel_filter == "Sans personnel":
            filtered_df = filtered_df[filtered_df['PRESENCE_PERSONNEL'] == 'Non']
    elif service_choice == "Boucle induction magnétique":
        if induction_filter == "Avec boucle induction magnétique":
            filtered_df = filtered_df[filtered_df['BOUCLE_INDUCTION_MAGNETIQUE'] == 'Oui']
        elif induction_filter == "Sans boucle induction magnétique":
            filtered_df = filtered_df[filtered_df['BOUCLE_INDUCTION_MAGNETIQUE'] == 'Non']
    
        

    
    # Tracer la carte avec les données filtrées
    map_ = plot_map(filtered_df, service_choice)
    col1,col2 = st.columns(2)
    # Afficher les colonnes pour la carte et le graphique ou uniquement la carte selon le choix
    if service_choice != "Aucun":
        col1, col2 = st.columns(2)
    
        with col1:
            # Afficher la carte avec Streamlit
            st.markdown(
                '<h3 style="color:black; text-align: center;">Carte des gares</h3>',
                unsafe_allow_html=True,
            )
            st.pydeck_chart(map_)
    
        with col2:
     
            # Vérification s'il y a des données après le filtre
            if not filtered_df.empty:
                # Configuration des catégories selon le service sélectionné
                if service_choice == "Wifi":
                    chart_column = 'Service Wifi'
                    title = "Répartition des gares selon le Wifi"
                elif service_choice == "Velo":
                    chart_column = 'Has_Bike_Parking_Within_250m'
                    title = "Répartition des gares selon le parking vélo"
                elif service_choice == "Toilettes":
                    chart_column = 'TOILETTES'
                    title = "Répartition des gares selon les toilettes"
                elif service_choice == "Accès ascenseur/rampe":
                    chart_column = 'ACCES_ASCENSEUR_RAMPE'
                    title = "Répartition des gares selon l'accès ascenseur/rampe"
                elif service_choice == "Toilettes accessibles":
                    chart_column = 'TOILETTES_ACCESSIBLE'
                    title = "Répartition des gares selon les toilettes accessibles"
                elif service_choice == "Fauteuil roulant disponible":
                    chart_column = 'FAUTEUIL_ROULANT_DISPONIBLE'
                    title = "Répartition des gares selon la disponibilité de fauteuils roulants"
                else:
                    st.write("Service non reconnu.")
                    chart_column = None
        
                # Si une colonne valide est définie, afficher le camembert
                if chart_column:
                    pie_chart = px.pie(
                        filtered_df,
                        names=chart_column,  # La colonne utilisée pour les catégories
                        title=title,
                        hole=0.4,  # Donut chart
                        color_discrete_sequence=px.colors.sequential.RdBu,  # Couleurs personnalisées
                    )
                    st.plotly_chart(pie_chart)

        # Graphique en barres par DEPARTEMENT
        if not filtered_df.empty and 'DEPARTEMENT' in filtered_df.columns:
            # Filtrer les données pour ne garder que celles où la variable cible est "Oui"
            filtered_df_oui = filtered_df[filtered_df[chart_column] == 'Oui']
        
            # Vérification si des données existent après le filtrage
            if not filtered_df_oui.empty:
                # Comptage des occurrences par département
                dept_counts = filtered_df_oui['DEPARTEMENT'].value_counts().reset_index()
                dept_counts.columns = ['DEPARTEMENT', 'Nombre']  # Renommage des colonnes pour le graphique
        
                # Graphique en barres
                bar_chart = px.bar(
                    dept_counts,
                    x='DEPARTEMENT',  # Axe des x : les départements
                    y='Nombre',  # Nombre d'occurrences par département
                    title=f"Répartition des gares ayant {service_choice} par départements",
                    text_auto=True,  # Affichage des valeurs au-dessus des barres
                    labels={'DEPARTEMENT': 'Département', 'Nombre': 'Nombre'},
                    color='DEPARTEMENT',  # Ajouter de la couleur par département
                    color_discrete_sequence=px.colors.sequential.RdBu  # Choix de couleurs
                )
                st.plotly_chart(bar_chart)

    else:
        # Si "Aucun" est sélectionné, afficher uniquement la carte
        st.markdown(
            '<h3 style="color:black; text-align: center;">Carte des gares</h3>',
            unsafe_allow_html=True,
        )
        st.pydeck_chart(map_)
# Onglet Logistique
with tab5:
    # Fonction pour convertir un DataFrame en CSV
    def convert_df_to_csv(df):
        # Utilisation de StringIO pour générer un CSV en mémoire
        csv = df.to_csv(index=False)
        return csv
    
    # Télécharger df
    csv_df = convert_df_to_csv(df)
    st.download_button(
        label="Télécharger la base de données utilisée",
        data=csv_df,
        file_name="df1.csv",
        mime="text/csv"
    )
    
     # Télécharger df1
    csv_df1 = convert_df_to_csv(df1)
    st.download_button(
        label="Télécharger accessibilité en gare",
        data=csv_df1,
        file_name="accessibilite-en-gare.csv",
        mime="text/csv"
    )
    
    # Télécharger df2
    csv_df2 = convert_df_to_csv(df2)
    st.download_button(
        label="Télécharger accompagnement PMR",
        data=csv_df2,
        file_name="accompagnement-pmr-gares.csv",
        mime="text/csv"
    )
    
    # Télécharger df3
    csv_df3 = convert_df_to_csv(df3)
    st.download_button(
        label="Télécharger arrêts transporteur",
        data=csv_df3,
        file_name="arrets-transporteur.csv",
        mime="text/csv"
    )
    
    # Télécharger df4
    csv_df4 = convert_df_to_csv(df4)
    st.download_button(
        label="Télécharger équipements accessibilité",
        data=csv_df4,
        file_name="equipements-accessibilite-en-gares.csv",
        mime="text/csv"
    )
    
    # Télécharger df5
    csv_df5 = convert_df_to_csv(df5)
    st.download_button(
        label="Télécharger gares équipées du WiFi",
        data=csv_df5,
        file_name="gares-equipees-du-wifi.csv",
        mime="text/csv"
    )
    
    # Télécharger df6
    csv_df6 = convert_df_to_csv(df6)
    st.download_button(
        label="Télécharger liste des gares",
        data=csv_df6,
        file_name="liste-des-gares.csv",
        mime="text/csv"
    )
    
    # Télécharger df7
    csv_df7 = convert_df_to_csv(df7)
    st.download_button(
        label="Télécharger parking vélos Île-de-France",
        data=csv_df7,
        file_name="parking-velos-ile-de-france-mobilites.csv",
        mime="text/csv"
    )
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 12:40:27 2025

@author: drakoriz
"""

import pandas as pd

# Liste des noms de fichiers CSV

df1 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/accessibilite-en-gare.csv", sep=';')
df2 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/accompagnement-pmr-gares.csv", sep=';')
df3 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/arrets-transporteur.csv", sep=';')
df4 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/equipements-accessibilite-en-gares.csv", sep=';')
df5 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/gares-equipees-du-wifi.csv", sep=';')
df6 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/liste-des-gares.csv", sep=';')
df7 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/parking-velos-ile-de-france-mobilites.csv", sep=';')
df8 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/referentiel-equipements-gares-.csv", sep=';')
df9 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/validations-reseau-ferre-nombre-validations-par-jour-1er-semestre.csv", sep=';')

#1 3 7 8 9 
# Afficher les colonnes et les types de données des DataFrames
for name, df in zip(
    ["df1", "df2", "df3", "df4", "df5", "df6", "df7", "df8", "df9"], 
    [df1, df2, df3, df4, df5, df6, df7, df8, df9]
):
    print(f"Colonnes dans {name}:")
    print(df.columns)
    print("Types des colonnes:")
    print(df.dtypes)
    print("\n")

# Comparer les colonnes entre les DataFrames
common_columns = {}
for name, df in zip(
    ["df1", "df2", "df3", "df4", "df5", "df6", "df7", "df8", "df9"], 
    [df1, df2, df3, df4, df5, df6, df7, df8, df9]
):
    common_columns[name] = df.columns

# Trouver les colonnes communes entre les DataFrames
for name, columns in common_columns.items():
    for other_name, other_columns in common_columns.items():
        if name != other_name:
            common = set(columns).intersection(set(other_columns))
            if common:
                print(f"Colonnes communes entre {name} et {other_name}: {common}")

################################################################################################
import pandas as pd
# Indices des colonnes à supprimer (2ème colonne, 3ème colonne, etc.)
df6 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/liste-des-gares.csv", sep=';')
df4 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/equipements-accessibilite-en-gares.csv", sep=';')
df5 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/gares-equipees-du-wifi.csv", sep=';')
df2 = pd.read_csv("/Users/drakoriz/Documents/SNCF_BLEU/dragon/accompagnement-pmr-gares.csv", sep=';')
# Liste des départements d'Île-de-France en lettres et en majuscule
idf_departements = ['PARIS', 'SEINE-ET-MARNE', 'YVELINES', 'ESSONNE', 'HAUTS-DE-SEINE', 'SEINE-SAINT-DENIS', 'VAL-DE-MARNE', "VAL-D'OISE"]

# Convertir la colonne 'DEPARTEMENT' en majuscule et vérifier si elle est dans la liste des départements d'Île-de-France
df6['DEPARTEMEN'] = df6['DEPARTEMEN'].str.upper()  # Convertir en majuscule
df6 = df6[df6['DEPARTEMEN'].isin(idf_departements)]  # Filtrer les départements

#1 3 7 8 9 

colonnes_a_supprimer = [1, 2, 3, 4, 5, 6, 9, 10,11, 12, 13, 14, 15,17]  # Indices (commencent à 0)
colonnes_a_supprimer2 = [2,3,4]
# Supprimer les colonnes par leurs indices
df6 = df6.drop(df6.columns[colonnes_a_supprimer], axis=1)

df4 = df4.drop(df4.columns[colonnes_a_supprimer2], axis=1)


df4['Accessibilité'] = df4['Accessibilité'].astype(str)
# Extraire les valeurs uniques dans la colonne 'Accessibilité'
types_accessibilite = df4['Accessibilité'].unique().tolist()

# Noms des colonnes pour les types d'accessibilité
noms_colonnes = [
    'ECRAN_INFO_GARE',
    'PRESENCE_PERSONNEL',
    'INFO_SONORE_GARE',
    'BANDE_EVEIL_VIGILANCE',
    'ACCES_ASCENSEUR_RAMPE',
    'TOILETTES',
    'BOUCLE_INDUCTION_MAGNETIQUE',
    'TOILETTES_ACCESSIBLE',
    'ASSISTANCE_ACCES_QUAIS',
    'FAUTEUIL_ROULANT_DISPONIBLE'
]

# Initialiser les nouvelles colonnes avec des valeurs par défaut (0) dans df4
for nom_colonne in noms_colonnes:
    df4[nom_colonne] = 0

# Remplir les colonnes avec 1 si l'accessibilité correspond à l'un des types dans la liste
for i, type_accessibilite in enumerate(types_accessibilite):
    df4[noms_colonnes[i]] = df4['Accessibilité'].apply(lambda x: 1 if type_accessibilite in x else 0)
aa= df6["CODE_UIC"] == 87113001

# Supprimer la deuxième colonne de df4
df4 = df4.drop(df4.columns[2], axis=1)
df4 = df4.groupby('UIC').max().reset_index()

df6 = df6.drop_duplicates(subset=df6.columns[0], keep='first')

df_merged = pd.merge(df4, df6, left_on=df4.columns[0], right_on=df6.columns[0], how='right')
df5['UIC_&_87'] = '87' + df5['UIC'].astype(str)
df5 = df5.drop(df5.columns[0], axis=1)  # Supprimer la première colonne
df5.insert(0, 'UIC_&_87', df5.pop('UIC_&_87'))  # Insérer la colonne 'UIC_&_87' à la première position
df_merged[df_merged.columns[0]] = df_merged[df_merged.columns[0]].astype(str)

df5 = df5.drop(df5.columns[1], axis=1)
df_merged2= pd.merge(df_merged, df5, left_on=df_merged.columns[0], right_on=df5.columns[0], how='left')

# Convertir la première colonne en datetime si ce n'est pas déjà le cas
df2[df2.columns[0]] = pd.to_datetime(df2[df2.columns[0]], format='%Y-%m')

# Trier par la première colonne de manière décroissante pour avoir les dates les plus récentes en premier
df2 = df2.sort_values(by=df2.columns[0], ascending=False)

# Garder uniquement la première occurrence de chaque UIC (colonne 1)
df2 = df2.drop_duplicates(subset=df2.columns[1], keep='first')
df2 = df2.drop(df2.columns[7], axis=1)
df2 = df2.drop(df2.columns[0], axis=1)
df2 = df2.drop(df2.columns[1], axis=1)
df2[df2.columns[0]] = df2[df2.columns[0]].astype(str)
df_merged3= pd.merge(df_merged2, df2, left_on=df_merged.columns[0], right_on=df2.columns[0], how='left')
df_merged3 = df_merged3.drop(columns=['CODE_UIC', 'UIC_&_87', 'Code UIC'])



"""
accented_chars = "áàâäãåāæéèêëēēiíìîïīíıjóòôöõøōœúùûüūūýÿ"
unaccented_chars = "aaaaaaaeeeeeiiiiiijooooooooooouuuuuuuyy"
# Créer un tableau de traduction
trans = str.maketrans(accented_chars, unaccented_chars)

# Appliquer les transformations
df3["ArTName"] = (
    df3["ArTName"]
    .str.lower()                            # Convertir en minuscules
    .str.translate(trans)                    # Supprimer les accents
    .str.replace(r"[-\d]", "", regex=True)   # Supprimer les tirets et les chiffres
    .str.replace(r"\s+", "", regex=True)     # Supprimer les espaces pour tout coller
    .str.replace(r"[^a-z]", "", regex=True)# Supprimer tous les caractères non alphabétiques
    .str.replace(r"tgv", "", regex=True)  
)

# Appliquer les transformations sur la colonne souhaitée de df_merged3 (ici la 3ème colonne)
df_merged3['temp_col'] = (
    df_merged3.iloc[:, 1]                       # Sélectionner la 3ème colonne
    .str.lower()                                # Convertir en minuscules
    .str.translate(trans)                        # Supprimer les accents
    .str.replace(r"[-\d]", "", regex=True)      # Supprimer les tirets et les chiffres
    .str.replace(r"\s+", "", regex=True)        # Supprimer les espaces pour tout coller
    .str.replace(r"[^a-z]", "", regex=True)     # Supprimer les caractères non alphabétiques
    .str.replace(r"tgv", "", regex=True)        # Supprimer le terme 'tgv'
)


# Convertir d'abord en UTC, puis supprimer le fuseau horaire
df3['ArTChanged'] = pd.to_datetime(df3['ArTChanged'], utc=True).dt.tz_localize(None)

# Trier df3 par la colonne 'ArTChanged' (du plus ancien au plus récent)
df3 = df3.sort_values(by='ArTChanged', ascending=True)

df3 = df3.drop_duplicates(subset='ArTName', keep='first')
# Supprimer les colonnes par indices
df3 = df3.drop(df3.columns[[0,1, 2 ,3 ,4, 5, 7, 8 ,9 ,10, 11,  15, 16 ,17 ,18 ,19]], axis=1)
"""



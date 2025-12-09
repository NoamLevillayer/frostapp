from meteostat import Point, Daily
from datetime import datetime
import pandas as pd

path = "communes_france_loca.csv"

df = pd.read_csv(
    path,
    dtype={
        'nom_standard': 'object',
        'code_postal': 'Int64',
        'dep_code': 'object'
    }
)

def get_coordinates(nom_commune, code_postal=None): 
    if code_postal:
        result = df[(df['nom_standard'] == nom_commune) & (df['code_postal'] == code_postal)]
    else:
        result = df[df['nom_standard'] == nom_commune]
    
    if result.empty:
        raise ValueError(f"Commune '{nom_commune}' non trouvée")
    
    if len(result) > 1 and not code_postal:
        raise ValueError(f"Plusieurs communes trouvées pour '{nom_commune}'. Spécifiez le code postal.")

    
    lat = result.iloc[0]['latitude_mairie']
    lon = result.iloc[0]['longitude_mairie']
    
    return (lat, lon)


def get_temperature_data(coordinates, start_year=2013, end_year=2024):

    if coordinates is None:
        print("Coordonnees invalides")
        return None
    
    lat, lon = coordinates
    location = Point(lat, lon)
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)

    data = Daily(location, start, end)
    data = data.fetch()

    if data.empty:
        print("Aucune donnees disponibles pour ces coordonnees")
        return None
    
    temp_df = data.reset_index()

    temp_df['is_freezing'] = temp_df['tmin'] < 0

    temp_df['year'] = temp_df['time'].dt.year
    temp_df['month'] = temp_df['time'].dt.month

    return temp_df[['time', 'tmin', 'is_freezing', 'year', 'month']]

def display_frost_statistics(temp_df):

    if temp_df is None or temp_df.empty:
        print("DataFrame vide ou invalide")
        return 
    
    frost_by_year = temp_df.groupby('year')['is_freezing'].sum()

    return frost_by_year

def calculate_frost_probability(temp_df):
    if temp_df is None or temp_df.empty:
        print("DataFrame vide ou invalide")
        return None
    
    df_copy = temp_df.copy()
    df_copy['day_of_year'] = df_copy['time'].dt.dayofyear

    frost_prob = df_copy.groupby('day_of_year').agg(
        frost_probability=('is_freezing', 'mean'),
        total_years=('is_freezing', 'count')).reset_index()
    
    frost_prob['frost_probability'] = frost_prob['frost_probability'] * 100

    return frost_prob
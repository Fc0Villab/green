import pandas as pd
import streamlit as st

st.title("Ranking Individual de Jugadores")

# Leer archivo Excel
df = pd.read_excel("C:/Users/fcovi/Downloads/resultados_partidos.xlsx")

# Crear columnas con nombres de las parejas
df['Pareja_1'] = df['Pareja 1 Jugador A'] + " / " + df['Pareja 1 Jugador B']
df['Pareja_2'] = df['Pareja 2 Jugador A'] + " / " + df['Pareja 2 Jugador B']

# Determinar ganadores
def get_winner(row):
    if row['Juegos Pareja 1'] > row['Juegos Pareja 2']:
        return row['Pareja_1']
    elif row['Juegos Pareja 1'] < row['Juegos Pareja 2']:
        return row['Pareja_2']
    else:
        return "Empate"

df['Ganador'] = df.apply(get_winner, axis=1)

# Calcular estadísticas por pareja
puntos = {}
for _, row in df.iterrows():
    for pareja, juegos_ganados, juegos_perdidos in [
        (row['Pareja_1'], row['Juegos Pareja 1'], row['Juegos Pareja 2']),
        (row['Pareja_2'], row['Juegos Pareja 2'], row['Juegos Pareja 1']),
    ]:
        if pareja not in puntos:
            puntos[pareja] = {
                'Partidos Ganados': 0,
                'Juegos Ganados': 0,
                'Juegos Perdidos': 0
            }
        puntos[pareja]['Juegos Ganados'] += juegos_ganados
        puntos[pareja]['Juegos Perdidos'] += juegos_perdidos
        if row['Ganador'] == pareja:
            puntos[pareja]['Partidos Ganados'] += 1

df_posiciones = pd.DataFrame([
    {
        'Pareja': pareja,
        'Partidos Ganados': stats['Partidos Ganados'],
        'Juegos Ganados': stats['Juegos Ganados'],
        'Juegos Perdidos': stats['Juegos Perdidos'],
        'Dif de Juegos': stats['Juegos Ganados'] - stats['Juegos Perdidos']
    }
    for pareja, stats in puntos.items()
])

# Ranking por pareja (usado solo para asignar puntaje individual)
df_posiciones = df_posiciones.sort_values(
    by=['Partidos Ganados', 'Dif de Juegos'], ascending=False
).reset_index(drop=True)
df_posiciones['Posición'] = df_posiciones.index + 1

# Puntos por posición
puntos_posicion = {
    1: 50, 2: 30, 3: 20, 4: 10, 5: 5, 6: 3, 7: 1, 8: 0
}

# Ranking individual
jugadores = {}

for _, row in df_posiciones.iterrows():
    pareja = row['Pareja']
    posicion = row['Posición']
    puntos_ganados = puntos_posicion.get(posicion, 0)
    jugador_1, jugador_2 = pareja.split(" / ")

    for jugador in [jugador_1, jugador_2]:
        if jugador not in jugadores:
            jugadores[jugador] = {
                'Puntos': 0,
                'Partidos Jugados': 0,
                'Partidos Ganados': 0,
                'Partidos Perdidos': 0
            }
        jugadores[jugador]['Puntos'] += puntos_ganados

# Contar partidos jugados y ganados/perdidos por jugador
for _, row in df.iterrows():
    pareja_1 = row['Pareja_1']
    pareja_2 = row['Pareja_2']
    ganador = row['Ganador']
    jugadores_1 = pareja_1.split(" / ")
    jugadores_2 = pareja_2.split(" / ")

    for jugador in jugadores_1 + jugadores_2:
        jugadores[jugador]['Partidos Jugados'] += 1

    if ganador == pareja_1:
        for jugador in jugadores_1:
            jugadores[jugador]['Partidos Ganados'] += 1
        for jugador in jugadores_2:
            jugadores[jugador]['Partidos Perdidos'] += 1
    elif ganador == pareja_2:
        for jugador in jugadores_2:
            jugadores[jugador]['Partidos Ganados'] += 1
        for jugador in jugadores_1:
            jugadores[jugador]['Partidos Perdidos'] += 1
    else:  # Empate, se cuentan como jugados pero no como ganados/perdidos
        pass

# Crear DataFrame de ranking individual
df_individual = pd.DataFrame([
    {
        'Jugador': jugador,
        'Puntos': datos['Puntos'],
        'Partidos Jugados': datos['Partidos Jugados'],
        'Partidos Ganados': datos['Partidos Ganados'],
        'Partidos Perdidos': datos['Partidos Perdidos']
    }
    for jugador, datos in jugadores.items()
])

df_individual = df_individual.sort_values(by='Puntos', ascending=False).reset_index(drop=True)
df_individual['Posición'] = df_individual.index + 1

st.subheader("Ranking Individual")
st.dataframe(df_individual)
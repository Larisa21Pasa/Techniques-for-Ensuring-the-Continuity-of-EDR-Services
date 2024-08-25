import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
# Setări pentru afișarea completă a coloanelor și rândurilor
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)  # Lățime variabilă pentru a evita trunchierea coloanelor

def load_data_from_db(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query('''
    SELECT a.id AS agent_id, a.ip, t.start_processing, t.start_publishing, t.start_consumption
    FROM agents a, timestamps t
    WHERE t.agent_id = a.id
    ''', conn)
    conn.close()

    df['start_processing'] = pd.to_datetime(df['start_processing'])
    df['start_publishing'] = pd.to_datetime(df['start_publishing'])
    df['start_consumption'] = pd.to_datetime(df['start_consumption'])

    return df


def calculate_average_queue_time(df):
    # Calculăm timpul de așteptare în coadă
    df['queue_time'] = (df['start_consumption'] - df['start_publishing']).dt.total_seconds()

    # Calculăm timpul mediu de așteptare pentru fiecare agent
    avg_queue_time = df.groupby('agent_id')['queue_time'].mean()

    return avg_queue_time


def calculate_average_queue_time(df):
    # Calculăm timpul de așteptare în coadă
    df['queue_time'] = (df['start_consumption'] - df['start_publishing']).dt.total_seconds()

    # Calculăm timpul mediu de așteptare pentru fiecare agent
    avg_queue_time = df.groupby('agent_id')['queue_time'].mean()

    return avg_queue_time, df


def analyze_data(df):
    # Calculăm timpul mediu dintre publicare și consumare pentru fiecare agent
    df['publish_to_consume'] = (df['start_consumption'] - df['start_publishing']).dt.total_seconds()
    average_publish_to_consume_per_agent = df.groupby('agent_id').apply(
        lambda x: (x['start_consumption'] - x['start_publishing']).dt.total_seconds().mean()
    )
    print('Timpul mediu dintre publicare și consumare per agent:')
    print(average_publish_to_consume_per_agent)

    # Calculăm timpul mediu de procesare al alertelor pentru fiecare agent
    df['process_to_publish'] = (df['start_publishing'] - df['start_processing']).dt.total_seconds()
    average_process_to_publish_per_agent = df.groupby('agent_id').apply(
        lambda x: (x['start_publishing'] - x['start_processing']).dt.total_seconds().mean()
    )
    print('Timpul mediu de procesare al alertelor per agent:')
    print(average_process_to_publish_per_agent)

    # Durata medie de procesare până la publicare în general
    overall_average_process_to_publish = df['process_to_publish'].mean()
    print(f'Durata medie de procesare până la publicare: {overall_average_process_to_publish:.2f} secunde')

    # Numărul total de alerte per agent
    alerts_per_agent = df['agent_id'].value_counts()
    print('Numărul total de alerte per agent:')
    print(alerts_per_agent)

    # Latența în timp pentru fiecare agent
    df['hour'] = df['start_processing'].dt.hour
    alerts_per_hour_per_agent = df.groupby(['agent_id', 'hour']).size().unstack(fill_value=0)
    print('Alerte pe oră per agent:')
    print(alerts_per_hour_per_agent)

    return (average_publish_to_consume_per_agent,
            average_process_to_publish_per_agent,
            overall_average_process_to_publish,
            alerts_per_agent,
            alerts_per_hour_per_agent)


def main():
    db_path = 'c2_server.db'  # Completează cu calea către baza ta de date
    df = load_data_from_db(db_path)
    print(f"DATELE DIN DB: {df}\n")
    results = analyze_data(df)
    print(f"REZULTATE {results}")

if __name__ == '__main__':
    main()

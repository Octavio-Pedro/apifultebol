
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import os

# URL fornecida pelo usuário
DATABASE_URL = "postgresql://neondb_owner:npg_DRPAFgfK9y2M@ep-orange-brook-ai94k6jr-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def migrate():
    print("Iniciando migração para o Neon.tech...")
    
    # Conectar ao SQLite local
    try:
        sqlite_conn = sqlite3.connect('football_data.db')
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT * FROM matches")
        matches = sqlite_cursor.fetchall()
        print(f"Encontradas {len(matches)} partidas no SQLite.")
    except Exception as e:
        print(f"Erro ao ler SQLite: {e}")
        return

    # Conectar ao PostgreSQL remoto
    try:
        pg_conn = psycopg2.connect(DATABASE_URL)
        pg_cursor = pg_conn.cursor()
        
        # Criar tabela se não existir
        pg_cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id VARCHAR(255) PRIMARY KEY,
                league VARCHAR(255),
                season VARCHAR(255),
                date VARCHAR(255),
                home_team VARCHAR(255),
                away_team VARCHAR(255),
                home_score INTEGER,
                away_score INTEGER,
                home_corners INTEGER DEFAULT 0,
                away_corners INTEGER DEFAULT 0,
                home_yellow_cards INTEGER DEFAULT 0,
                away_yellow_cards INTEGER DEFAULT 0,
                home_red_cards INTEGER DEFAULT 0,
                away_red_cards INTEGER DEFAULT 0,
                home_penalties INTEGER DEFAULT 0,
                away_penalties INTEGER DEFAULT 0
            );
        """)
        
        # Inserir dados
        if matches:
            query = """
                INSERT INTO matches (
                    id, league, season, date, home_team, away_team, home_score, away_score,
                    home_corners, away_corners, home_yellow_cards, away_yellow_cards,
                    home_red_cards, away_red_cards, home_penalties, away_penalties
                ) VALUES %s
                ON CONFLICT (id) DO NOTHING
            """
            execute_values(pg_cursor, query, matches)
            print(f"Migração concluída: {len(matches)} registros enviados para o Neon.tech.")
        
        pg_conn.commit()
        pg_cursor.close()
        pg_conn.close()
        sqlite_conn.close()
        
    except Exception as e:
        print(f"Erro na migração para o PostgreSQL: {e}")

if __name__ == "__main__":
    migrate()

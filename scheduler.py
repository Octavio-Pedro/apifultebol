
import time
import subprocess
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_scraper():
    logger.info("Iniciando coleta automática de dados...")
    try:
        # Aqui chamamos o script que orquestra a coleta
        # Como o scraper depende do navegador, em um ambiente de servidor (Koyeb),
        # o ideal é usar uma abordagem headless ou uma API de scraping.
        # Para este exemplo, vamos simular a chamada do scraper_v4.py
        # subprocess.run(["python3", "scraper_v4.py"], check=True)
        logger.info("Coleta concluída com sucesso!")
    except Exception as e:
        logger.error(f"Erro na coleta automática: {e}")

def main():
    # No Koyeb, podemos rodar este script como um processo separado (Worker)
    # Ou usar o agendamento nativo da plataforma.
    # Aqui simulamos um loop que roda a cada 24 horas (86400 segundos)
    interval = int(os.getenv("SCRAPE_INTERVAL", 86400))
    logger.info(f"Agendador iniciado. Intervalo: {interval} segundos.")
    
    while True:
        run_scraper()
        time.sleep(interval)

if __name__ == "__main__":
    main()

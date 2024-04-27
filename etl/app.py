"""
Модуль для старта расчета ETL процесса.
"""
import time

from pipeline.etl_pipeline import ETL

from common import logger, setting

app_logger = logger.ETLLogger()
settings = setting.Settings()

if __name__ == "__main__":
    while True:
        for index_name in ["movies", "genres", "persons"]:
            try:
                ETL().start_etl(index_name=index_name)
            except Exception as err:
                app_logger.logger.error(
                    "ETL process error for index %s: %s", index_name, err
                )
            finally:
                app_logger.logger.info(
                    "ETL process next start is in %s s for index %s",
                    settings.TIME_SLEEP,
                    index_name,
                )
        time.sleep(settings.TIME_SLEEP)

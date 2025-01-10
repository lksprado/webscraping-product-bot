import os
import pandas as pd
from sqlalchemy import create_engine, text
import logging

from dotenv import load_dotenv
load_dotenv()


class PostgresClient:
	# definindo argumentos padrão, se nada for definido, usará default
    def __init__(self):
        self.host = os.getenv("PG_HOST")
        self.port = os.getenv("PG_PORT")
        self.database_name = os.getenv("PG_DATABASE")
        self.user = os.getenv("PG_USER")
        self.password = os.getenv("PG_PASSWORD")
        self.schema = os.getenv("PG_SCHEMA", "public")  # Default apenas para schema
        self._engine = None
        self._connect()
        self.setup_logging()

    def setup_logging(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S',
        )

    def _connect(self):
        try:
            connection_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database_name}"
            self._engine = create_engine(connection_string)
            with self._engine.connect() as conn:
                conn.execute(text(f"SET search_path TO {self.schema}"))
            logging.info(f"Database '{self.database_name}' connected successfully on host '{self.host}'")
        except Exception as e:
            logging.exception("Database connection failed")

    def save_dataframe(self, df, table_name, if_exists='append'):
        """
        Salva um DataFrame em uma tabela do PostgreSQL.
        :param df: DataFrame do pandas.
        :param table_name: Nome da tabela de destino.
        :param if_exists: Comportamento se a tabela já existir ('fail', 'replace', 'append').
        """
        try:
            df.to_sql(table_name, self._engine, schema=self.schema, if_exists=if_exists, index=False)
            logging.info(f"Dataframe data saved succesfully in {table_name}")
        except Exception:
            logging.exception(f"Dataframe failed to save in {table_name}")

    def execute_query(self, query, return_as_df=True):
        """
        Executa uma consulta SQL genérica e retorna os resultados.
        :param query: A consulta SQL a ser executada.
        :param return_as_df: Se True, retorna os resultados como um DataFrame.
        :return: Os resultados da consulta (lista ou DataFrame, dependendo de return_as_df).
        """
        try:
            with self._engine.connect() as conn:
                result = conn.execute(text(query))
                if return_as_df:
                    # Se solicitado, converte o resultado para DataFrame
                    columns = result.keys()
                    result_data = result.fetchall()
                    return pd.DataFrame(result_data, columns=columns)
                else:
                    # Caso contrário, retorna os resultados como lista
                    return result.fetchall()
        except Exception:
            logging.exception(f"Failed to execute query")
            return None

    def close_connection(self):
        try:
            if self._engine:
                self._engine.dispose()
                logging.info('Database connection closed')
        except Exception as e:
            logging.exception("Failed to close database connection")
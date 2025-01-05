import os
import pandas as pd
from sqlalchemy import create_engine, text

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

    def _connect(self):
        try:
            connection_string = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database_name}"
            self._engine = create_engine(connection_string)
            with self._engine.connect() as conn:
                conn.execute(text(f"SET search_path TO {self.schema}"))
            print("Conexão com banco de dados estabelecida com sucesso!")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def save_dataframe(self, df, table_name, if_exists='append'):
        """
        Salva um DataFrame em uma tabela do PostgreSQL.
        :param df: DataFrame do pandas.
        :param table_name: Nome da tabela de destino.
        :param if_exists: Comportamento se a tabela já existir ('fail', 'replace', 'append').
        """
        try:
            df.to_sql(table_name, self._engine, schema=self.schema, if_exists=if_exists, index=False)
            print(f"Dados salvos com sucesso na tabela '{table_name}'.")
        except Exception as e:
            print(f"Erro ao salvar os dados: {e}")

    def close_connection(self):
        if self._engine:
            self._engine.dispose()
            print('Conexão encerrada.')
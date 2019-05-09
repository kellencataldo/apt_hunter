import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import contextlib
import logging
import os


BASE = sqlalchemy.ext.declarative.declarative_base()


class ApartmentEntry(BASE):
    __tablename__ = 'apartment_entries'
    address = sqlalchemy.Column(sqlalchemy.String, primary_key=True, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False)

    def __init__(self, address, price, url, title, description):
        self.address = address
        self.price = price
        self.url = url
        self.title = title
        self.description = description
        self.post_text = None

    def __str__(self):
        return f'{self.url}\n'\
               f'TITLE: {self.title} PRICE: {self.price} ADDRESS: {self.address}\n'\
               f'DESCRIPTION: {self.description}\n'\
               f'{self.post_text}\n'


class ConfigEntry(BASE):
    __tablename__ = 'config_entries'
    config_key = sqlalchemy.Column(sqlalchemy.String, primary_key=True, nullable=False)
    config_val = sqlalchemy.Column(sqlalchemy.String, nullable=False)


POSTGRES_ADDRESS = os.environ['POSTGRES_ADDRESS']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_DB = os.environ['POSTGRES_DB']
POSTGRES_PORT = os.environ['POSTGRES_PORT']

database_url = {'drivername': 'postgresql+psycopg2',
                'username': POSTGRES_USER,
                'password': POSTGRES_PASSWORD,
                'host': POSTGRES_ADDRESS,
                'port': POSTGRES_PORT,
                'database': POSTGRES_DB}


DATABASE_ENGINE = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(**database_url))
DATABASE_ENGINE.connect()
BASE.metadata.create_all(DATABASE_ENGINE)
SESSION_FACTORY = sqlalchemy.orm.sessionmaker(bind=DATABASE_ENGINE, expire_on_commit=False)
SESSION = sqlalchemy.orm.scoped_session(SESSION_FACTORY)


@contextlib.contextmanager
def get_scoped_session():
    """Provide a transactional scope around a series of operations."""
    scoped_session = SESSION()
    try:
        yield scoped_session
        scoped_session.commit()
    except Exception as e:
        scoped_session.rollback()
        logging.error(str(e))
        raise
    finally:
        scoped_session.close()


def get_last_run():
    with get_scoped_session() as db_session:
        query_result = db_session.query(ConfigEntry).filter(ConfigEntry.config_key == 'last_run').one_or_none()
        if query_result is not None:
            return query_result.config_val
        return None


def set_last_run(last_run_str):
    with get_scoped_session() as db_session:
        query_result = db_session.query(ConfigEntry).filter(ConfigEntry.config_key == 'last_run').one_or_none()
        if query_result is None:
            db_session.add(ConfigEntry(config_key='last_run', config_val=last_run_str))
        else:
            query_result.config_val = last_run_str


def apt_in_database(crawled_apt):
    with get_scoped_session() as db_session:
        query_result = db_session.query(ApartmentEntry).filter(ApartmentEntry.address == crawled_apt.address,
                                                               ApartmentEntry.price == crawled_apt.price).\
                                                               one_or_none()
        if query_result is None:
            logging.info(f'Apartment: {crawled_apt.address} not found in database')
            db_session.add(crawled_apt)
            return False
        else:
            logging.info(f'Apartment: {crawled_apt.address} found in database')
            return True

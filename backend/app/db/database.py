"""
Database Configuration and Schema Management for MzansiBuilds
"""

import logging
import os
from contextlib import contextmanager
from typing import Optional

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
load_dotenv()


class DatabaseConfig:
    """Database configuration class to manage MySQL connection and schema."""

    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')

        self.setup_logging()

    def setup_logging(self):
        """Configure logger for database operations."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def connect(self) -> Optional[mysql.connector.MySQLConnection]:
        """Open a new MySQL connection for the current request."""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True,
            )

            if connection.is_connected():
                self.logger.info('Opened new MySQL connection.')
                return connection

            self.logger.warning('MySQL connection object created but not connected.')
            return None

        except Error as error:
            self.logger.error(f'Error connecting to MySQL: {error}')
            return None

    def open_connection(self) -> mysql.connector.MySQLConnection:
        """Create a connection and raise an exception if it cannot be established."""
        connection = self.connect()
        if connection is None:
            raise Exception('Failed to open database connection.')
        return connection

    def close_connection(self, connection: mysql.connector.MySQLConnection) -> None:
        """Close a MySQL connection if it is open."""
        if connection is not None and connection.is_connected():
            connection.close()
            self.logger.info('Closed MySQL connection.')

    def get_cursor(self, connection: Optional[mysql.connector.MySQLConnection] = None):
        """Return a dictionary cursor for the provided connection or a new one."""
        if connection is None:
            connection = self.open_connection()
        return connection.cursor(dictionary=True)

    def execute_query(self, query: str, params: tuple = None) -> Optional[list]:
        """Execute a SELECT query and return all rows."""
        connection = self.open_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()

        except Error as error:
            self.logger.error(f'Error executing query: {error}')
            return None

        finally:
            cursor.close()
            self.close_connection(connection)

    def execute_update(self, query: str, params: tuple = None) -> bool:
        """Execute an INSERT, UPDATE, or DELETE statement. Returns True on success, False on failure."""
        connection = self.open_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())
            return True

        except Error as error:
            self.logger.error(f'Error executing update: {error}')
            return False

        finally:
            cursor.close()
            self.close_connection(connection)

    def execute_insert(self, query: str, params: tuple = None) -> Optional[int]:
        """Execute an INSERT statement and return the last inserted ID."""
        connection = self.open_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())
            # For INSERT statements, get the last insert id from the same cursor
            cursor.execute('SELECT LAST_INSERT_ID() AS last_id')
            result = cursor.fetchone()
            last_id = int(result['last_id']) if result and result['last_id'] is not None else None
            return last_id

        except Error as error:
            self.logger.error(f'Error executing insert: {error}')
            return None

        finally:
            cursor.close()
            self.close_connection(connection)

    def execute_batch(self, query: str, data: list) -> bool:
        """Execute a batch operation using executemany."""
        connection = self.open_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.executemany(query, data)
            return True

        except Error as error:
            self.logger.error(f'Error executing batch: {error}')
            return False

        finally:
            cursor.close()
            self.close_connection(connection)

    def table_exists(self, table_name: str) -> bool:
        """Return True when the requested table exists in the configured database."""
        query = '''
        SELECT COUNT(*) AS count
        FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s
        '''
        result = self.execute_query(query, (self.database, table_name))
        return bool(result and result[0].get('count', 0) > 0)

    def create_database_schema(self, force_recreate: bool = False) -> bool:
        """Create the database and all required tables for the application schema."""
        try:
            temp_connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                autocommit=True,
            )
            cursor = temp_connection.cursor()

            cursor.execute('SHOW DATABASES LIKE %s', (self.database,))
            db_exists = cursor.fetchone() is not None

            if force_recreate and db_exists:
                cursor.execute(f'DROP DATABASE IF EXISTS `{self.database}`')
                self.logger.info(f'Force recreated database {self.database}')
                db_exists = False

            if not db_exists:
                cursor.execute(f'CREATE DATABASE IF NOT EXISTS `{self.database}`')
                self.logger.info(f'Created database {self.database}')

            cursor.execute(f'USE `{self.database}`')

            if not self._all_schema_tables_exist(cursor):
                try:
                    self._create_tables(cursor)
                except Error as table_error:
                    # If table creation fails due to schema issues, drop and retry
                    self.logger.warning(f'Schema creation failed: {table_error}, attempting recovery...')
                    cursor.execute(f'DROP DATABASE IF EXISTS `{self.database}`')
                    cursor.execute(f'CREATE DATABASE `{self.database}`')
                    cursor.execute(f'USE `{self.database}`')
                    self._create_tables(cursor)
            else:
                self.logger.info('All required schema tables already exist.')

            cursor.close()
            temp_connection.close()
            return True

        except Error as error:
            self.logger.error(f'Error creating database schema: {error}')
            return False

    def _all_schema_tables_exist(self, cursor) -> bool:
        """Return True when all required application tables are present."""
        required_tables = [
            'users',
            'projects',
            'updates',
            'comment',
            'collaboration_request',
        ]

        cursor.execute('SHOW TABLES')
        existing_tables = [row[0] for row in cursor.fetchall()]
        missing = [table for table in required_tables if table not in existing_tables]

        if missing:
            self.logger.info(f'Missing tables: {missing}')
            return False

        self.logger.info('All required tables are present.')
        return True

    def _create_tables(self, cursor):
        """Create the schema tables with proper keys and constraints."""
        self.logger.info('Creating database schema tables...')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                bio TEXT,
                is_deleted TINYINT(1) NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                proj_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                stage ENUM('Planning', 'Development', 'Testing', 'Completed') NOT NULL DEFAULT 'Planning',
                support_needed TEXT,
                is_deleted TINYINT(1) NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_project_user_id (user_id),
                CONSTRAINT fk_project_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS updates (
                update_id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                user_id INT NOT NULL,
                content TEXT NOT NULL,
                is_deleted TINYINT(1) NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_updates_project_id (project_id),
                INDEX idx_updates_user_id (user_id),
                CONSTRAINT fk_update_project FOREIGN KEY (project_id) REFERENCES projects(proj_id) ON DELETE RESTRICT ON UPDATE CASCADE,
                CONSTRAINT fk_update_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comment (
                com_id INT AUTO_INCREMENT PRIMARY KEY,
                update_id INT NOT NULL,
                user_id INT NOT NULL,
                content TEXT NOT NULL,
                is_deleted TINYINT(1) NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_comment_update_id (update_id),
                INDEX idx_comment_user_id (user_id),
                CONSTRAINT fk_comment_update FOREIGN KEY (update_id) REFERENCES updates(update_id) ON DELETE RESTRICT ON UPDATE CASCADE,
                CONSTRAINT fk_comment_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collaboration_request (
                collab_id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                user_id INT NOT NULL,
                message TEXT,
                status ENUM('Pending', 'Accepted', 'Rejected') NOT NULL DEFAULT 'Pending',
                is_deleted TINYINT(1) NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_collab_project_id (project_id),
                INDEX idx_collab_user_id (user_id),
                CONSTRAINT fk_collab_project FOREIGN KEY (project_id) REFERENCES projects(proj_id) ON DELETE RESTRICT ON UPDATE CASCADE,
                CONSTRAINT fk_collab_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')

        self.logger.info('Database schema tables created successfully.')


db_config = DatabaseConfig()


def get_db_connection():
    """Yield a fresh database connection for each request.

    Use this helper as a FastAPI dependency with Depends(get_db_connection).
    """
    connection = db_config.open_connection()
    try:
        yield connection
    finally:
        db_config.close_connection(connection)

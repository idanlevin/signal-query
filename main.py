import os
import csv
import json
import logging
import platform
import argparse

from pysqlcipher3 import dbapi2 as sqlite

logging.basicConfig(level=logging.INFO,
                    format='|%(asctime)s|%(levelname)-5s|%(process)d|%(thread)d|%(name)s|%(message)s')

_logger = logging.getLogger('signal-query')

# Default Signal directory based on the operating system
def default_signal_dir_path():
    system = platform.system()
    _logger.info(f'Operating system: {system}')
    if system == 'Windows':
        return os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Signal')
    elif system == 'Darwin':
        return os.path.join(os.environ['HOME'], 'Library', 'Application Support', 'Signal')
    elif system == 'Linux':
        return os.path.join(os.environ['HOME'], '.config', 'Signal')
    else:
        raise Exception('Unsupported operating system.')

# Default paths for the Signal database
def default_db_path():
    default_signal_dir = default_signal_dir_path()
    return os.path.join(default_signal_dir, 'sql', 'db.sqlite')

# Default path for the Signal key file
def default_key_path():
    default_signal_dir = default_signal_dir_path()
    return os.path.join(default_signal_dir, 'config.json')

# Read the key from the key file
def read_key(key_file_path):
    _logger.info(f'Reading key from {key_file_path}')
    with open(key_file_path, "r") as key_file:
        key = json.load(key_file)["key"].strip()
    return key

# Execute a SQL query and save the results to a file or print to console
def execute_query(cursor, query, output_file=None, output_format='csv'):
    # Execute the query
    cursor.execute(query)
    
    # Save the results to a file or print to console
    results = cursor.fetchall()
    if output_file:
        with open(output_file, 'a', newline='') as f:
            if output_format == 'csv':
                headers = [description[0] for description in cursor.description]
                writer = csv.writer(f)
                writer.writerow(headers)  # write the headers
                for row in results:
                    escaped_row = [str(item).replace('\n', '\\n') for item in row]
                    writer.writerow(escaped_row)
            else: # json
                for row in results:
                    r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) ]
                    f.write(json.dumps(r) + '\n')
    else:
        for row in results:
            print(row)

# Interactive shell for executing SQL queries
def interactive_shell(cursor, output_file=None):
    _logger.info("Entering interactive mode. Type your queries, and type 'exit' to quit.")
    while True:
        query = input("sql> ").strip()
        if query.lower() == 'exit':
            break
        try:
            execute_query(cursor, query, output_file)
        except Exception as e:
            print(f"Error: {e}")

# Setup the connection to the encrypted SQLite database
def setup_connection(db_path, key_file_path):
    key = read_key(key_file_path)
    
    # Connect to the encrypted SQLite database
    conn = sqlite.connect(db_path)
    cursor = conn.cursor()
    
    # Decrypt the database using the PRAGMA KEY command
    _logger.info(f"Decrypting database {db_path} using key {key[:10]}...")
    r = cursor.execute(f"PRAGMA KEY = \"x'{key}'\"")
    if not "ok" in str(r.fetchone()):
        raise Exception("Failed to decrypt database.")
    cursor.execute("PRAGMA cipher_page_size = 4096")
    cursor.execute("PRAGMA kdf_iter = 64000")
    cursor.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
    cursor.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")
    
    return conn, cursor

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Execute SQL query on an encrypted SQLite database.')
    parser.add_argument('--query', help='SQL query to execute (optional)')
    parser.add_argument('--db_path', default=default_db_path(), help='Path to the encrypted SQLite database (default: %(default)s)')
    parser.add_argument('--key_file_path', default=default_key_path(), help='Path to the key file (default: %(default)s)')
    parser.add_argument('--output_file', help='Path to the output file (optional)')
    parser.add_argument('--output_format', default='csv', help='Output format file, can be json or csv (default: %(default)s)')

    args = parser.parse_args()
    
    conn, cursor = setup_connection(args.db_path, args.key_file_path)
    
    if args.query:
        execute_query(cursor, args.query, args.output_file, args.output_format)
    else:
        interactive_shell(cursor, args.output_file)
    
    # Close the connection
    conn.close()

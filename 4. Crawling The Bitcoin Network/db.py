import contextlib
import os
import random
import sqlite3
import threading
import time

def execute_statement(statement, args={}, retries=3):
    # try / except is a hack for write conflicts from multiple threads
    try:
        with contextlib.closing(sqlite3.connect("crawler.db")) as conn: # auto-closes
            with conn: # auto-commits
                with contextlib.closing(conn.cursor()) as cursor: # auto-closes
                    return cursor.execute(statement, args).fetchall()
    except Exception as e:
        if retries <= 0:
            print(e)
        else:
            return execute_statement(statement, args, retries=retries-1)

def create_tables(remove=False):
    filename = "crawler.db"
    
    try:
        os.remove(filename)
    except Exception as e:
        print(e)
        pass

    create_observations_table = """
    CREATE TABLE observations (
        ip TEXT,
        port INT,
        services INT,
        timestamp INT,
        receiver_services INT,
        receiver_ip TEXT,
        receiver_port INT,
        sender_services INT,
        sender_ip TEXT,
        sender_port INT,
        nonce TEXT,
        user_agent TEXT,
        latest_block INT,
        relay INT
    )
    """
    execute_statement(create_observations_table)

    create_errors_table = """
    CREATE TABLE errors (
        ip TEXT,
        port INT,
        error INT,
        timestamp INT
    )
    """
    execute_statement(create_errors_table)

            
def observe_node(address, args_dict):
    q = """
    INSERT INTO observations (
        ip,
        port,
        services,
        timestamp,
        receiver_services,
        receiver_ip,
        receiver_port,
        sender_services,
        sender_ip,
        sender_port,
        nonce,
        user_agent,
        latest_block,
        relay
    ) VALUES (
        :ip,
        :port,
        :services,
        :timestamp,
        :receiver_services,
        :receiver_ip,
        :receiver_port,
        :sender_services,
        :sender_ip,
        :sender_port,
        :nonce,
        :user_agent,
        :latest_block,
        :relay
    )
    """
    args_dict["nonce"] = str(args_dict["nonce"]) # HACK
    args_dict["ip"] = address[0]
    args_dict["port"] = address[1]
    execute_statement(q, args_dict)


def observe_error(address, error):
    q = """
    INSERT INTO errors (
        ip, port, error, timestamp
    ) VALUES (
        ?,?,?,?
    )
    """
    ip, port = address
    timestamp = time.time()
    try:
        execute_statement(q, (ip, port, error, timestamp))
    except Exception as e:
        print(e)


def count_observations(filename="crawler.db"):
    with sqlite3.connect("crawler.db") as conn:
        return conn.execute("select count(*) from observations").fetchone()[0]
    
def list_observations():
    with sqlite3.connect("crawler.db") as conn:
        return conn.execute("select * from observations").fetchone()

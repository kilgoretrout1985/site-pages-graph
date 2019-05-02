import csv
import sqlite3


def write_csv(csv_file: str, done_urls: dict) -> None:
    with open(csv_file, mode='w') as csv_fh:
        csv_writer = csv.writer(csv_fh)
        csv_writer.writerow([
            'url',
            'status',
            'clicks from /',
            'internal links to url',
            'url redirects to'
        ])
        for url in done_urls:
            csv_writer.writerow([
                url,
                done_urls[url]['status'],
                done_urls[url]['clicks'],
                done_urls[url]['internal_links'],
                done_urls[url]['redirect_to'],
            ])


def write_sqlite(sqlite_file: str, done_urls: dict) -> None:
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS urls")  # clean from previous run
    cursor.execute("""
        CREATE TABLE urls (
            id integer PRIMARY KEY,
            url text UNIQUE,
            status integer,
            clicks_from_main integer,
            internal_links integer,
            redirect_to text
        )
    """)

    for url in done_urls:
        cursor.execute(
            """
            INSERT INTO 
                urls(url,status,clicks_from_main,internal_links,redirect_to) 
                VALUES (?,?,?,?,?)
            """, 
            (
                url,
                done_urls[url]['status'],
                done_urls[url]['clicks'],
                done_urls[url]['internal_links'],
                done_urls[url]['redirect_to'],
            )
        )

    conn.commit()
    conn.close()

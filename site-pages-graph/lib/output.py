import csv


def write_csv(csv_file: str, done_urls: dict) -> bool:
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
    return True

import argparse
import sys

from kicad_adds_on_spider.crawler.worker import Worker


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="KiCad add-ons mirror crawler")
    parser.add_argument("save_dir", help="Directory to save mirrored files")
    parser.add_argument(
        "--download-url",
        default="",
        help="Base URL that KiCad clients will use to fetch files from this mirror "
             "(e.g. http://localhost:8080/). If empty, URLs in packages.json/repository.json "
             "will keep pointing to the official sources.",
    )
    args = parser.parse_args()

    crawler = Worker(args.save_dir, download_base_url=args.download_url)
    crawler.run()

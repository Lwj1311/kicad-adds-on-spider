import json
import os
import sys

from kicad_adds_on_spider.crawler.crawler_utils import CrawlerUtils
from kicad_adds_on_spider.crawler.kicad_utils import KicadUtils
from kicad_adds_on_spider.models.packages import Package, Packages, Version
from kicad_adds_on_spider.models.repository import Repository


KICAD_OFFICIAL_REPOSITORY_URL = "https://repository.kicad.org/repository.json"


class Worker:
    def __init__(self, home_dir: str, download_base_url: str = ""):
        self._download_base_url = download_base_url
        self._home_dir = home_dir
        self._repository = None
        self._packages = None
        os.makedirs(self._home_dir, exist_ok=True)

    @property
    def resource_fp(self):
        return os.path.join(self._home_dir, "resources.zip")

    @property
    def resource_url(self):
        return self._download_base_url + "resources.zip"

    @property
    def repository_fp(self):
        return os.path.join(self._home_dir, "repository.json")

    @property
    def repository_url(self):
        return self._download_base_url + "repository.json"

    @property
    def packages_fp(self):
        return os.path.join(self._home_dir, "packages.json")

    @property
    def packages_url(self):
        return self._download_base_url + "packages.json"

    def get_library_save_path(self, pkg: Package, version: Version):
        return os.path.join(self._home_dir, KicadUtils.format_zip_name(pkg, version))

    def get_library_download_url(self, pkg: Package, version: Version):
        return KicadUtils.format_zip_url(self._download_base_url, pkg, version)

    def _update_resource(self):
        CrawlerUtils.download_content_and_save(self._repository.resources.url, self.resource_fp)
        self._repository.resources.url = self.resource_url
        self._repository.resources.sha256 = KicadUtils.get_sha256(self.resource_fp)

    def _update_packages(self):
        with open(self.packages_fp, "w") as f:
            f.write(self._packages.model_dump_json())
        self._repository.packages.url = self.packages_url
        self._repository.packages.sha256 = KicadUtils.get_sha256(self.packages_fp)

    def _update_repository(self):
        self._repository.name = "KiCad official repository mirror"
        with open(self.repository_fp, "w") as f:
            f.write(self._repository.model_dump_json())

    def _update_libraries(self):
        total_lib_cnt = 0
        failed_lib_cnt = 0

        for pkg in self._packages.packages:
            for version in pkg.versions:
                total_lib_cnt += 1
                try:
                    CrawlerUtils.download_content_and_save(
                        version.download_url,
                        self.get_library_save_path(pkg, version),
                    )
                    version.download_url = self.get_library_download_url(pkg, version)
                except Exception as e:
                    print(f"[WARN] Download failed: {pkg.name} v{version.version}: {e}", file=sys.stderr)
                    failed_lib_cnt += 1

        print(
            f"Total: {total_lib_cnt}, Success: {total_lib_cnt - failed_lib_cnt}, Failed: {failed_lib_cnt}",
            flush=True,
        )

    def run(self):
        self._repository = Repository(
            **json.loads(CrawlerUtils.download_content_string(KICAD_OFFICIAL_REPOSITORY_URL))
        )
        self._packages = Packages(
            **json.loads(CrawlerUtils.download_content_string(self._repository.packages.url))
        )
        self._update_libraries()
        self._update_resource()
        self._update_packages()
        self._update_repository()
        print("Mirror build completed successfully.", flush=True)

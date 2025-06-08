import time

from src.config import settings
from src.core import Project
from src.log import logger
from src.toast import Toaster


def main():
    start = time.time()
    project = Project()
    project.clean(settings.filepath.root / settings.filepath.tmp)
    project.converter.convert()
    # project.restorer.restore()
    end = time.time()
    return end - start


if __name__ == '__main__':
    last = main()
    logger.info(f"===== Lasting {last or -1:.2f}s =====")

    Toaster(
        title="农场汉化脚本",
        body=(
            "农场汉化脚本运行完啦"
            "\n"
            f"耗时 {last or -1:.2f}s"
        ),
        logo=settings.filepath.resource / "img" / "icon.png"
    ).notify()
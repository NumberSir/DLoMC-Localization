import time

from src.config import settings
from src.core import Converter, Restorer, Tweaker, Project
from src.core.paratranz import Paratranz
from src.log import logger
from src.toast import Toaster


# TODO: WIP
# def pre_process(project: Project):
#     project.check_structure()
#     project.clean(
#         settings.filepath.root / settings.filepath.tmp,
#         settings.filepath.root / settings.filepath.convert,
#         settings.filepath.root / settings.filepath.download,
#         settings.filepath.root / settings.filepath.result,
#     )
#     options = webdriver.EdgeOptions()
#     options.add_experimental_option("prefs", {
#         "download.default_directory": (settings.filepath.root / settings.filepath.tmp).__str__()
#     })
#     with webdriver.Edge(options=options) as driver:
#         star = SubscribeStar(driver=driver)
#         star.login()
#         pinned_post_url = star.get_pinned_post_url()
#         public_post_url = star.get_published_post_url(pinned_post_url)
#         download_link = star.get_download_link(public_post_url)
#         star.download(download_link)


def process(project: Project):
    paratranz = Paratranz()
    paratranz.download()

    Converter().convert()
    Restorer().restore()
    Tweaker().tweak()
    project.package()


def main():
    start = time.time()
    project = Project()
    """TODO: Download original game"""
    # pre_process(project)
    """Pick up texts to translate & replace translated texts"""
    process(project)
    end = time.time()
    return end - start


if __name__ == '__main__':
    last = main()
    logger.info(f"===== Lasting {last or -1:.2f}s =====")

    Toaster(
        title="DLoMC-Localization",
        body=(
            "Running finished"
            "\n"
            f"Cost {last or -1:.2f}s"
        ),
        logo=settings.filepath.resource / "project-img" / "icon.png"
    ).notify()
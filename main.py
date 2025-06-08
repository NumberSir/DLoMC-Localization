from src import Project, settings


def main():
    project = Project()
    project.clean(settings.filepath.root / settings.filepath.tmp)
    project.converter.convert()


if __name__ == '__main__':
    main()
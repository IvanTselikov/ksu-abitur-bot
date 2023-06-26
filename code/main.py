from project_controller import Project
import config
import sys

if __name__ == '__main__':
    try:
        project = Project(config.DEFAULT_BOT_PATH)
        project.run(recompile=True, new_console=False)
    except Exception as e:
        print(e)
        input('Для выхода нажмите любую клавишу...')
        sys.exit(0)

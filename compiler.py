import sys
from project_controller import Project
import config


if __name__ == '__main__':
    project = None

    try:
        args = sys.argv[1:]
        if not args:
            # 'python compiler.py' - запустить проект из папки по умолчанию
            project = Project(config.DEFAULT_BOT_PATH)
            project.run(recompile=False, new_console=False)
        elif args[0] == '-c':
            if len(args) > 1:
                # 'python compiler.py -c path/to/project' - скомпилировать и запустить проект из указанной папки
                path = args[1]
                if not Project.is_project(path):
                    raise Exception('Указанная папка "{}" не содержит проекта.'.format(path))
                else:
                    project = Project(path)
                    project.run(recompile=True, new_console=False)
            else:
                # 'python compiler.py -c' - скомпилировать и запустить проект из папки по умолчанию
                project = Project(config.DEFAULT_BOT_PATH)
                project.run(recompile=True, new_console=False)
        else:
            # 'python compiler.py path/to/project' - запустить проект из указанной папки
            path = args[0]
            if not Project.is_project(path):
                raise Exception('Указанная папка "{}" не содержит проекта.'.format(path))
            else:
                project = Project(path)
                project.run(recompile=False, new_console=False)
    except Exception as e:
        if project and project.is_alive():
            project.stop()
        
        print(e)
        input('Для выхода нажмите любую клавишу...')

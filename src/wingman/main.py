"""
Copyright © 2016-2017, 2020 biqqles.

This file is part of Wingman.

Wingman is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Wingman is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Wingman.  If not, see <http://www.gnu.org/licenses/>.

This file contains the application's entry point - main().
"""
import os
import sys
import subprocess
import time

import flint as fl

from wingman import app, config, IS_WIN  # non-relative imports for the benefit of PyInstaller
from wingman.windows.boxes import configuration, loading


def main():
    """Main application entry point."""
    if not fl.paths.is_probably_freelancer(config.paths['freelancer_dir']):
        configuration.ConfigurePaths(mandatory=True).exec()
    fl.paths.set_install_path(config.paths['freelancer_dir'])
    if sys.platform.startswith('win32'):
        import flair
        flair.set_install_path(config.paths['freelancer_dir'])
    elif sys.platform.startswith('linux'):
        if 'wine_prefix_dir' not in config.paths:
            configuration.ConfigurePaths(mandatory=True).exec()
        import rpyc
        subprocess.Popen(
            ['sudo', 'python3', '-m', 'flair', '-r', '-p', '18861', config.paths['freelancer_dir'], config.paths['wine_prefix_dir']],
        )
        c = None
        while not c:
            try:
                c = rpyc.connect('localhost', 18861)
            except ConnectionRefusedError:
                print('Waiting for flair...')
                time.sleep(1)

        flair = c.root
        print(config.paths['freelancer_dir'])
        flair.set_install_path(config.paths['freelancer_dir'])
        print(flair.get_state().running)

    loading.LoadingFiles().exec()

    from wingman.windows.main.layout import MainWindow
    mainWindow = MainWindow()

    os._exit(app.exec())  # bad! but sys.exit isn't working for some reason (not to do with excepthook)


if __name__ == '__main__':
    main()

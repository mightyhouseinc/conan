import os

from conan.tools.build import build_jobs
from conan.errors import ConanException


def _configuration_dict_to_commandlist(name, config_dict):
    command_list = [f'config:{name}']
    for key, value in config_dict.items():
        if type(value) is bool:
            b = 'true' if value else 'false'
            command_list.append(f'{key}:{b}')
        else:
            command_list.append(f'{key}:{value}')
    return command_list


class Qbs(object):
    def __init__(self, conanfile, project_file=None):
        # hardcoded name, see qbs toolchain
        self.profile = 'conan_toolchain_profile'
        self._conanfile = conanfile
        self._set_project_file(project_file)
        self.jobs = build_jobs(conanfile)
        self._configuration = dict()

    def _set_project_file(self, project_file):
        if not project_file:
            self._project_file = self._conanfile.source_folder
        else:
            self._project_file = project_file

        if not os.path.exists(self._project_file):
            raise ConanException(f'Qbs: could not find project file {self._project_file}')

    def add_configuration(self, name, values):
        self._configuration[name] = values

    def build(self, products=None):
        args = [
            '--no-install',
            '--build-directory', self._conanfile.build_folder,
            '--file', self._project_file,
        ]

        if products := products or []:
            args.extend(['--products', ','.join(products)])

        args.extend(['--jobs', f'{self.jobs}'])

        if self.profile:
            args.append(f'profile:{self.profile}')

        for name in self._configuration:
            config = self._configuration[name]
            args.extend(_configuration_dict_to_commandlist(name, config))

        cmd = f"qbs build {' '.join(args)}"
        self._conanfile.run(cmd)

    def build_all(self):
        args = [
            '--no-install',
            '--build-directory',
            self._conanfile.build_folder,
            '--file',
            self._project_file,
            '--all-products',
            *['--jobs', f'{self.jobs}'],
        ]

        if self.profile:
            args.append(f'profile:{self.profile}')

        for name in self._configuration:
            config = self._configuration[name]
            args.extend(_configuration_dict_to_commandlist(name, config))

        cmd = f"qbs build {' '.join(args)}"
        self._conanfile.run(cmd)

    def install(self):
        args = [
            '--no-build',
            '--install-root', self._conanfile.package_folder,
            '--file', self._project_file
        ]

        args.extend(f'config:{name}' for name in self._configuration)
        cmd = f"qbs install {' '.join(args)}"
        self._conanfile.run(cmd)

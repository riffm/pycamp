# -*- coding: utf-8 -*-

import os
import sys
import errno
import logging
import subprocess
import ConfigParser


logging.basicConfig(format='%(asctime)-15s: %(message)s', 
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def main(args):
    config_path = os.path.abspath('pycamp.cfg')
    if os.path.exists(config_path) and os.path.isfile(config_path):
        for env_name, options in env_descriptions(config_path):
            env = Environ(env_name, options)
            env.execute_runcmd()
    else:
        sys.exit('Please provide `pycamp.cfg`')


def env_descriptions(config_path):
    descriptions = []
    defaults = {
        'base_python': 'python',
        'change-dir': '',
        'deps': [],
        'runcmd': '',
    }
    conf_parser = ConfigParser.RawConfigParser()
    conf_parser.read(config_path)
    base_env_options = prepair_options(conf_parser.items('base'), defaults=defaults)
    for section_name in conf_parser.sections():
        if section_name == 'base':
            continue
        if ':' in section_name:
            env_name = section_name.split(':', 1)[1]
            env_options = prepair_options(conf_parser.items(section_name),
                                          defaults=base_env_options.copy())
            descriptions.append((env_name, env_options))
        else:
            raise ValueError('Section `%s` is not in form `[base:ENV_NAME]`' % section_name)
    return descriptions


def prepair_options(items, defaults=None):
    multi_options = ('deps',)
    options = defaults or {}
    for k, v in items:
        v = v.strip()
        if k in multi_options:
            v = v.split('\n')
        options[k] = v
    return options


class Environ(object):
    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.path = os.path.join('.pycamp', name)
        self.full_path = os.path.abspath(self.path)
        self.pip = os.path.join(self.full_path, 'bin', 'pip')
        self.python = os.path.join(self.full_path, 'bin', 'python')
        self.cwd = None
        if options['change-dir']:
            self.cwd = os.path.abspath(options['change-dir'])
        if not os.path.exists(os.path.join(self.full_path, 'bin', 'python')):
            logger.info('Environment `%s` does not exist' % name)
            self._create()
        self._install_deps()
        self._update_target_package()

    @property
    def namespace(self):
        return {
            'bin-dir': os.path.join(self.full_path, 'bin'),
            'python_executable': os.path.join(self.full_path, 'bin', 'python'),
        }

    def _create(self):
        logger.info('Creating environment `%s`...' % self.name)
        try:
            os.makedirs(self.full_path)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        args = ['virtualenv', '--no-site-packages', '-p', self.options['base_python'], self.full_path]
        logger.info(' '.join(args))
        p = subprocess.Popen(args)
        retcode = p.wait()
        if retcode:
            sys.exit('Virtualenv returned %d' % retcode)

    def _install_deps(self):
        if self.options['deps']:
            logger.info('Updating dependencies for `%s`...' % self.name)
            args = [self.pip, '--log=%s/pip.log' % self.full_path, 'install'] + self.options['deps']
            logger.info(' '.join(args))
            p = subprocess.Popen(args)
            retcode = p.wait()
            if retcode:
                sys.exit('Virtualenv returned %d' % retcode)

    def _update_target_package(self):
        if os.path.exists('setup.py'):
            logger.info('Installing your application')
            args = [self.python, 'setup.py', 'install']
            logger.info(' '.join(args))
            p = subprocess.Popen(args)
            retcode = p.wait()
            if retcode:
                sys.exit('Could not install your package')

    def execute_runcmd(self):
        logger.info('Running your command')
        args = (self.options['runcmd'] % self.namespace).split()
        logger.info(' '.join(args))
        p = subprocess.Popen(args, cwd=self.cwd)
        # NOTE: `runcmd` may be a longrunning process or daemon
        #retcode = p.wait()
        #if retcode:
        #    logger.info('`%s` command failed' % self.name)


if __name__ == '__main__':
    main(sys.argv)

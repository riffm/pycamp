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


def env_descriptions(conf_parser):
    defaults = {
        'python': 'python',
        'deps': [],
        'base': None,
    }
    ready = {}
    defered = {}
    for section_name in conf_parser.sections():
        if not section_name.startswith('cmd:'):
            if conf_parser.has_option(section_name, 'base'):
                base = conf_parser.get(section_name, 'base')
                if base in ready:
                    ready[section_name] = prepair_options(conf_parser.items(section_name),
                                                          defaults=ready[base].copy())
                else:
                    defered[section_name] = base
            else:
                ready[section_name] = prepair_options(conf_parser.items(section_name),
                                                      defaults=defaults.copy())
    if defered and not ready:
        raise ValueError('All your environments has `base` option,'
                         ' so we can not get very first base environment')
    while defered:
        inherited = []
        for env_name, base in defered.items():
            if base in ready:
                inherited.append(env_name)
                ready[env_name] = prepair_options(conf_parser.items(env_name),
                                                  defaults=ready[base].copy())
        if not inherited:
            raise ValueError('Please check your `base` option for'
                             ' environment(s) %s' % ', '.join(defered.keys()))
        map(defered.pop, inherited)
    return ready.items()


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
        args = ['virtualenv', '--no-site-packages', '-p', self.options['python'], self.full_path]
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


def main(args):
    config_path = os.path.abspath('pycamp.cfg')
    if os.path.exists(config_path) and os.path.isfile(config_path):
        conf_parser = ConfigParser.RawConfigParser()
        conf_parser.read(config_path)
        for env_name, options in env_descriptions(conf_parser):
            print env_name, options
            #env = Environ(env_name, options)
            #env.execute_runcmd()
    else:
        sys.exit('Please provide `pycamp.cfg`')


if __name__ == '__main__':
    main(sys.argv)

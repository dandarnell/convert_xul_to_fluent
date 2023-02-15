#!/usr/bin/env python

import os
import glob
import json
import cmd
import re
import convert

class DOM:
    def __init__(self, path, contents):
        self.path = path
        self.contents = contents

ALL_DOMS = []

def print_file_list(paths):
    filenames = []

    for i in range(len(paths)):
        filename = paths[i].split('/')[-1]

        filenames.append(str(i).rjust(4, ' ') + ': ' + filename)

    for filename in filenames:
        if len(filename) > 33:
            filenames[filenames.index(filename)] = filename[:33] + '~'

    cli = cmd.Cmd()
    cli.columnize(filenames, displaywidth=120)

def get_migrated_dtd_paths():
    migration_path  = './comm/python/l10n/tb_fluent_migrations/completed'
    migration_files = os.listdir(migration_path)
    dtd_paths       = []

    # Iterate over existing migrations
    for file in migration_files:
        path = os.path.join(migration_path, file)

        with open(path) as file:
            contents = file.read()

            # Find all DTD files referenced in migration
            matches = re.findall('from_path *= *"[^"]+"', contents)
            paths   = [match.split('"')[1] for match in matches]
            paths   = ['./comm/' + path for path in paths if path.split('.')[-1] == 'dtd']

            if paths:
                dtd_paths.extend(paths)

    # Remove duplicates from DTD file list
    dtd_paths = list(dict.fromkeys(dtd_paths))

    return dtd_paths

def get_unmigrated_dtd_paths():
    #for path in glob.glob('./**/*.dtd', recursive = True):
    #    with open(path) as file:

    migrated_paths = get_migrated_dtd_paths()

    dtd_paths             = glob.glob('./**/*.dtd', recursive = True)
    locale_agnostic_paths = [re.sub('locales/[^/]+/', '', path) for path in dtd_paths]
    dtd_paths             = [path for path in dtd_paths if locale_agnostic_paths[dtd_paths.index(path)] not in migrated_paths]

    return dtd_paths

def get_dom_paths(dtd_path):
    dom_paths = []
    if not ALL_DOMS:
        dom_paths.extend(glob.glob('./**/*.xul', recursive = True))
        dom_paths.extend(glob.glob('./**/*.xhtml', recursive = True))
        dom_paths.extend(glob.glob('./**/*.html', recursive = True))

        dom_paths = [path for path in dom_paths if not re.search("/tests?/", path)]

        for path in dom_paths:
            with open(path) as file:
                contents = file.read()
                ALL_DOMS.append(DOM(path, contents))

    dom_paths = []
    for dom in ALL_DOMS:
        # Find all DOMs referencing DTD file
        if dom.contents.find('/' + dtd_path.split('/')[-1]) != -1:
            dom_paths.append(dom.path)

    return dom_paths

def get_dtds():
    dtd_paths = get_unmigrated_dtd_paths()
    dtds = []

    for path in dtd_paths:
        dtds.append({'dtd_path': path, 'dom_paths': get_dom_paths(path)})

    return dtds

def main():
    cache_path = './dtd-cache.json'

    if os.path.exists(cache_path):
        with open(cache_path) as file:
            dtds = json.load(file)
    else:
        print('No DTD cache found. Generating DTD cache...')

        dtds = get_dtds()
        dtds_json = json.dumps(dtds, indent=4)

        with open(cache_path, 'w') as file:
            file.write(dtds_json)

    print_file_list([dtd['dtd_path'] for dtd in dtds])
    print('The above DTD files have not been migrated.')
    dtd_index = input('Which DTD file would you like to migrate? #')
    dtd = dtds[file_index]

    print_file_list(dtd['dom_paths'])
    print('The above DOM files make use of ' + dtd['dtd_path'].split('/')[-1] + '.')
    dom_index = input('Which DOM file would you like to migrate? #')
    dom_path = dtd['dom_paths'][dom_index]

    args = [
        '--bug_id',
        bug_id,
        '--description',
        "Migrate toolbox options strings from DTD to FTL",
        '--repo',
        'comm/',
        '--dtd',
        dtd['dtd_path'],
        '--dom',
        dom_path,
        '--ftl',
        ''
    ]

    convert.main(args)

if __name__ == '__main__':
    main()

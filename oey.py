#!/usr/bin/env python3

from __future__ import print_function

import sys, getopt

# keyed by package-name, contains the list of package dependencies
pn = {}

# keyed by package-name, contains the list of dependent packages
rev_pn = {}

show_parent_deps = False
depends_file = 'task-depends.dot'

indent_str = '\t'

def parse_pn_depends():
    try:
        fh = open(depends_file)
    except:
        print('File %s not found' % (depends_file))
        print('Generate the file with bitbake -g <recipe>')
        sys.exit()

    try:
        raw_lines = fh.read().splitlines()
    finally:
        fh.close()

    for line in raw_lines:
        line = line.rstrip()
        fields = line.split(' ')

        if len(fields) < 3 or fields[1] != '->' or fields[0][1:-1].split('.do_')[1] != 'prepare_recipe_sysroot' or fields[2][1:-1].split('.do_')[1] != 'populate_sysroot':
            continue

        if len(fields) == 3:
            name = fields[0][1:-1].split('.do_')[0]
            depend = fields[2][1:-1].split('.do_')[0]

            if name not in pn:
                pn[name] = []

            pn[name].append(depend)


def build_reverse_dependencies():
    for key in pn:
        for name in pn[key]:
            if name not in rev_pn:
                rev_pn[name] = []

            rev_pn[name].append(key)


def list_packages():
    for key in sorted(pn):
        print(key)

    print('\n',)


def list_deps_recurse(package, parent_deps, depth, max_depth, not_show_native_deps):
    if depth > max_depth:
        return;

    if package in pn:
        tab_str = indent_str * depth

        for dep in sorted(pn[package]):
            if show_parent_deps or dep not in parent_deps:
                if not not_show_native_deps or (not_show_native_deps and "-native" not in dep):
                    print(tab_str, dep)
                    list_deps_recurse(dep, pn[package], depth + 1, max_depth, not_show_native_deps)


def list_deps(package, max_depth, not_show_native_deps):
    if package in pn:
        print('\nPackage [', package, '] depends on')
        list_deps_recurse(package, (), 1, max_depth, not_show_native_deps)

    elif package in rev_pn:
        print('Package [', package, '] has no dependencies')

    else:
        print('Package [', package, '] not found')

    print('\n',)


def list_reverse_deps_recurse(package, depth, max_depth):
    if depth > max_depth:
        return;

    if package in rev_pn:
        tab_str = indent_str * depth

        for dep in sorted(rev_pn[package]):
            print(tab_str, dep)
            list_reverse_deps_recurse(dep, depth + 1, max_depth)


def list_reverse_deps(package, max_depth):
    if package in rev_pn:
        print('\nPackage [', package, '] is needed by')
        list_reverse_deps_recurse(package, 1, max_depth)
        
    elif package in pn:
        print('No package depends on [', package, ']')
        
    else:
        print('Package [', package, '] not found')

    print('\n',)


def collect_deps_flat(src, d, package, depth, max_depth, not_show_native_deps):
    if depth > max_depth:
        return;

    if package in src:
        for dep in src[package]:
            if dep not in d:
                if not not_show_native_deps or (not_show_native_deps and "-native" not in dep):
                    d.append(dep)
                    collect_deps_flat(src, d, dep, depth + 1, max_depth, not_show_native_deps)


def list_deps_flat(package, max_depth, not_show_native_deps):
    d = []

    if package in pn:
        for dep in pn[package]:
            if dep not in d:
                if not not_show_native_deps or (not_show_native_deps and "-native" not in dep):
                    d.append(dep)
                    collect_deps_flat(pn, d, dep, 2, max_depth, not_show_native_deps)

        print('\nPackage [', package, '] depends on')
        for dep in sorted(d):
            print('\t', dep)

    elif package in rev_pn:
        print('Package [', package, '] has no dependencies')

    else:
        print('Package [', package, '] not found')

    print('\n',)


def list_reverse_deps_flat(package, max_depth):
    d = []

    if package in rev_pn:
        for dep in rev_pn[package]:
            if dep not in d:
                d.append(dep)
                collect_deps_flat(rev_pn, d, dep, 2, max_depth, not_show_native_deps)

        print('\nPackage [', package, '] is needed by')
        for dep in sorted(d):
            print('\t', dep)

    elif package in pn:
        print('No package depends on [', package, ']')

    else:
        print('Package [', package, '] not found')

    print('\n',)


def usage():
    print('\nUsage: %s [options] [package]\n' % (sys.argv[0]))
    print('Displays OE build dependencies for a given package or recipe.')
    print('Uses the task-depends.dot file for raw data.')
    print('Generate the *.dot data files by running bitbake -g <recipe>.\n')
    print('Options:')
    print('-h\tShow this help message and exit')
    print('-v\tShow error messages such as recursive dependencies')

    print('-r\tShow reverse dependencies, i.e. packages dependent on package')
    print('-f\tFlat output instead of default tree output')
    print('-d <depth>\tMaximum depth to follow dependencies, default and max is 10')
    print('-i <input file path>\tInput file path')
    print('-s\tShow child package dependencies that are already listed')
    print('-n\tRemove host(native) dependencies')
    print('\tas direct parent dependencies.')
    print('-n\tRemove host(native) dependencies\n')
    print("Provide the package name to analyze from the generated *.dot file.")
    print('Run the program without a package name to get a list of all')
    print('available package names.\n')


if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hi:vrfd:s:n')

    except getopt.GetoptError:
        print('No options: Please see the help')
        usage()
        sys.exit(2)


    depth = 10
    reverse = False
    flat = False
    not_show_native_deps = False

    for o, a in opts:
        if o in ('-h'):
            usage()
            sys.exit()

        elif o in ('-i'):
            depends_file = a

        elif o in ('-r'):
            reverse = True

        elif o in ('-f'):
            flat = True

        elif o in ('-s'):
            show_parent_deps = True

        elif o in ('-d'):
            try:
                depth = int(a, 10)
            except ValueError:
                print('Bad depth argument: ', a)
                usage()
                sys.exit(1)
        elif o in ('-n'):
            not_show_native_deps = True

        else:
            assert False, 'unhandled option'


    if depth > 10:
        print('Limiting depth to 10 levels')
        depth = 10

    parse_pn_depends()
    build_reverse_dependencies()

    if len(args) > 0:
        if reverse:
            if flat:
                list_reverse_deps_flat(args[0], depth)
            else:
                list_reverse_deps(args[0], depth)
        else:
            if flat:
                list_deps_flat(args[0], depth, not_show_native_deps)
            else:
                list_deps(args[0], depth, not_show_native_deps)

    else:
        list_packages()


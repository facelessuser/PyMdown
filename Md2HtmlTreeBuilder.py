"""
Md2HtmlTreeBuilder

Requirements:
  - pymdown must be found in your path
  - Must have a folder structure with markdown files.
  - Expects to find a pymdown.json in the root folder.
    pydown.json must be configured to so that pymdown
    can find templates etc.
  - index.md are converted to index.html, but if they are not found,
    one will be generated.

Usage:
Md2HtmlTreeBuilder /Some/path/to/folder

Licensed under MIT
Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>
"""
from __future__ import unicode_literals
from __future__ import print_function
from os.path import exists, basename, abspath, isdir, isfile, join, splitext
from os import listdir, chdir
import codecs
import subprocess
import sys
import traceback
import re
PY3 = sys.version_info >= (3, 0)

if PY3:
    from urllib.request import pathname2url
    from shlex import quote
    from os import getcwd
else:
    from urllib import pathname2url
    from pipes import quote
    from os import getcwdu as getcwd

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

DEBUG = False

__version__ = '0.0.1'


CRUMB = '<li class="crumb"><a href="%s">%s</a></li>'
BREAD_CRUMBS = '<ul class="bread-crumbs">%s</ul>'

RE_TEMPLATE_NAV = re.compile(r"(\{*?)\{{2}\s*(nav)\s*\}{2}(\}*)")
RE_TEMPLATE_INDEX = re.compile(r"(\{*?)\{{2}\s*(index)\s*\}{2}(\}*)")

from os.path import getmtime as get_modified_time

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


if _PLATFORM == "osx":
    from ctypes import *

    # http://stackoverflow.com/questions/946967/get-file-creation-time-with-python-on-mac
    class struct_timespec(Structure):
        _fields_ = [('tv_sec', c_long), ('tv_nsec', c_long)]

    class struct_stat64(Structure):
        _fields_ = [
            ('st_dev', c_int32),
            ('st_mode', c_uint16),
            ('st_nlink', c_uint16),
            ('st_ino', c_uint64),
            ('st_uid', c_uint32),
            ('st_gid', c_uint32),
            ('st_rdev', c_int32),
            ('st_atimespec', struct_timespec),
            ('st_mtimespec', struct_timespec),
            ('st_ctimespec', struct_timespec),
            ('st_birthtimespec', struct_timespec),
            ('dont_care', c_uint64 * 8)
        ]

    libc = CDLL('libc.dylib')
    stat64 = libc.stat64
    stat64.argtypes = [c_char_p, POINTER(struct_stat64)]

    def getctime(pth):
        """
        Get the appropriate creation time on OSX
        """

        buf = struct_stat64()
        rv = stat64(pth.encode("utf-8"), pointer(buf))
        if rv != 0:
            raise OSError("Couldn't stat file %r" % pth)
        return buf.st_birthtimespec.tv_sec

else:
    from os.path import getctime as get_creation_time

    def getctime(pth):
        """
        Get the creation time for everyone else
        """

        return get_creation_time(pth)


def getmtime(pth):
    """
    Get modified time for everyone
    """

    return get_modified_time(pth)


def relative_root(pth):
    return '/'.join((['..'] * len(pth.replace('\\', '/').split('/')))) + '/index.html'


class Md2HtmlTreeBuilder(object):
    def __init__(self, settings=None, tab_size=4, force_update=False):
        self.tab_size = 4
        self.clear()
        self.force_update = force_update
        if settings is not None and exists(settings) and isfile(settings):
            self.settings = settings
        else:
            self.settings = None

    def clear(self):
        self.base = '.'
        self.level = -1
        self.processed = 0
        self.folder_depth = -1
        self.levels_deep = 0
        self.total_nodes = 0
        self.is_empty = True
        self.errors = False
        self.updated = False

    def log(self, *args):
        if not self.quiet:
            for arg in args:
                print(' ' * (4 * self.level), arg)

    def get_process(self, cmd):
        """ Get the prepared subprocess object """
        if _PLATFORM == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(
                cmd, startupinfo=startupinfo,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        else:
            p = subprocess.Popen(
                ' '.join([quote(c) for c in cmd]),
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                shell=True, cwd=self.treepath
            )
        return p

    def batch_convert(self, pattern):
        """ Convert file pattern(s) to HTML """
        try:
            cmd = ['pymdown', '-b', '--basepath', '.']
            if DEBUG:
                cmd.append('-d')
            if self.settings is not None:
                cmd += ['-s', self.settings]
            for pat in pattern:
                cmd.append(pat)
            p = self.get_process(cmd)
            results = p.communicate()
            results, errors = results[0].decode("utf-8").split('\n'), results[1].decode("utf-8").split('\n')
            self.log(*(results + errors))
            if p.returncode:
                self.errors = True
        except:
            self.log(traceback.format_exc())
            self.log("ERROR: Either pymdown wasn't found, or there was a problem parsing a file!")

    def stream_convert(self, text, relpath=None, no_template=False):
        """ Convert a text object to HTML """
        results = None
        try:
            cmd = ['pymdown', '-q', '--basepath', '.', '--relpath', relpath]
            if no_template:
                cmd.append('--force-no-template')
            if DEBUG:
                cmd.append('-d')
            if self.settings is not None:
                cmd += ['-s', self.settings]
            p = self.get_process(cmd)
            p.stdin.write(text.encode('utf-8'))
            results = p.communicate()
            results, errors = results[0].decode("utf-8"), results[1].decode("utf-8").split('\n')
            if p.returncode:
                self.log(*errors)
                results = None
                self.errors = True
                self.log("ERROR: Issue occured parsing markdown stream!")
        except:
            trace = str(traceback.format_exc()).split('\n')
            self.log(*trace)
            self.log("ERROR: Either pymdown wasn't found, or there was a problem parsing a file!")
        return results

    def repl_index(self, m, index):
        """ Replace instances of {{ index }} with folder index """
        if m.group(0).startswith('{{{') and m.group(0).endswith('}}}'):
            return m.group(0)[1:-1]
        open = m.group(1) if m.group(1) else ''
        close = m.group(3) if m.group(3) else ''
        return open + index + close

    def convert_markdown(self, items, pth, index_exists, updated):
        # Process markdown files if we found some
        if len(updated):
            self.updated = True
            self.log('***valid node (%s)***\n' % pth)

        if len(items) or len(updated):
            if self.site_map and pth == '.':
                site_map = '%s.md' % self.site_map
                items.append(site_map)
            else:
                site_map = None

            if self.site_map is not None and pth != '.':
                self.site += ' ' * (self.tab_size * self.level) + '- [%s](%s)\n' % (
                    basename(pth),
                    pathname2url('/'.join(self.navbar) + '/index.html')
                )

        # Create markdown content for index file
        if len(updated):
            if not index_exists:
                text = '---\ntitle: %s\n---\n[TOC]\n# Index\n\n' % (basename(abspath(pth)) if pth != '.' else self.root)
            else:
                text = ''

        if len(items):
            for d in sorted(items, key=lambda s: s.lower()):
                if d[:-3] == 'index':
                    continue
                if (site_map is not None and d == site_map) or isfile(join(pth, d)):
                    if len(updated):
                        text += '- [%s](%s)\n' % (d[:-3], pathname2url((d[:-2] + 'html').replace('\\', '/')))
                    if self.site_map is not None:
                        self.site += ' ' * ((self.tab_size * self.level) + self.tab_size) + '- [%s](%s)\n' % (
                            d[:-3],
                            pathname2url('/'.join(self.navbar) + ('/%s' % d[:-2] + 'html'))
                        )
                elif len(updated):
                    text += '- [%s](%s)\n' % (basename(d), pathname2url((join(d, 'index.html')).replace('\\', '/')))

        # Convert the markdown to HTML and write it out
        if len(updated):
            if not index_exists:
                self.log("Generating %s..." % join(pth, 'index.html'))
                text = self.stream_convert(text, relpath=pth)
                if text is not None:
                    with codecs.open(join(pth, 'index.html'), 'w', encoding='utf-8') as f:
                        f.write(text)
            else:
                text = self.stream_convert(text, relpath=pth, no_template=True)

            # Convert all 'md' files.
            if not self.force_update:
                patterns = [join(pth, md) for md in updated if isfile(join(pth, md))]
                if index_exists:
                    patterns.append(join(pth, 'index.md'))
            else:
                patterns = [join(pth, '*.md')]
            if len(patterns):
                self.batch_convert(patterns)

            if index_exists:
                try:
                    with codecs.open(join(pth, 'index.html'), 'r', encoding='utf-8') as f:
                        html_text = f.read()
                    html_text = RE_TEMPLATE_INDEX.sub(
                        lambda m, txt=text: self.repl_index(m, index=txt),
                        html_text
                    )
                    with codecs.open(join(pth, 'index.html'), 'w', encoding='utf-8', errors="xmlcharrefreplace") as f:
                        f.write(html_text)
                except:
                    print(traceback.format_exc())
                    pass

        elif len(items):
            self.log("***node up to date (%s)***\n" % pth)
        else:
            self.log('***empty node (%s)***\n' % pth)

    def repl_nav(self, m, bread_crumbs):
        """ Replace instances of {{ nav }} with breadcrumbs """
        if m.group(0).startswith('{{{') and m.group(0).endswith('}}}'):
            return m.group(0)[1:-1]
        open = m.group(1) if m.group(1) else ''
        close = m.group(3) if m.group(3) else ''
        return open + (BREAD_CRUMBS % '\n'.join(bread_crumbs)) + close

    def add_breadcrumbs(self, pth, parent):
        """
        Add Nav {{ nav }}
        """

        for f in listdir(pth)[:]:
            item = join(pth, f)
            text = ''
            ishtml = isfile(item) and item.lower().endswith('.html')
            issitemap = self.site_map is not None and f == self.site_map + '.html' and pth == '.'
            if issitemap or (ishtml and (exists(item[:-4] + 'md') or f == 'index.html')):
                bread_crumbs = []
                count = 0
                last = len(self.navbar) - 1
                for crumb in reversed(self.navbar):
                    href = ('./' if count == 0 else '../' * count) + 'index.html'
                    name = self.root if count == last else crumb
                    bread_crumbs.insert(0, CRUMB % (href, name))
                    count += 1

                if f != 'index.html':
                    bread_crumbs.append(CRUMB % (pathname2url("./%s" % f), splitext(f)[0]))

                with codecs.open(item, 'r+', encoding='utf-8') as html:
                    text = html.read()
                    html.seek(0)
                    text = RE_TEMPLATE_NAV.sub(
                        lambda m, bc=bread_crumbs: self.repl_nav(m, bread_crumbs=bc),
                        text
                    )
                    html.write(text)
                    html.truncate()

    def build_node(self, pth='.', parent=None):
        """ Recursively build this node """
        self.level += 1
        docs = []
        folders = []
        levels_deep = 1
        nodes = 1
        empty_node = True
        index_exists = False
        updated = []
        self.navbar.append(basename(pth))
        self.log(
            "Processing Node (%s)" % pth,
            "--------------------------------"
        )

        # Crawl tree looking for markdown files
        # Track the markdown files and the folders that contain
        # the Markdown files.  Also, flag if the folder already
        # contains an 'index.md' file.
        if not exists(join(pth, '.md-ignore')):
            for f in sorted(listdir(pth), key=lambda s: s.lower()):
                if f in ('.svn', '.git'):
                    continue
                item = join(pth, f)
                if isdir(item):
                    levels, sub_nodes, is_empty = self.build_node(item, pth)
                    if not is_empty:
                        nodes += sub_nodes
                        folders.append(f)
                        if levels + 1 > levels_deep:
                            levels_deep = levels
                        updated.append(f)
                elif item.lower().endswith('.md'):
                    if not self.force_update:
                        converted = item[:-2] + 'html'
                        if not exists(converted):
                            updated.append(f)
                        else:
                            ts_html = getmtime(converted)
                            ts_md = getmtime(item)
                            if ts_md > ts_html:
                                updated.append(f)
                                self.log("Markdown Found: %s" % f)
                    else:
                        updated.append(f)
                        self.log("Markdown Found: %s" % f)
                    if index_exists is False:
                        index_exists = f == 'index.md'
                    empty_node = False
                    self.processed += 1
                    docs.append(f)

            # Convert Markdown
            self.convert_markdown(folders + docs, pth, index_exists, updated)

            if pth == '.' and self.site_map and len(folders + docs) and self.updated:
                text = self.stream_convert(self.site, relpath=pth)
                self.log('Generating the site map...')
                if text is not None:
                    with codecs.open(join(pth, '%s.html' % self.site_map), 'w', encoding='utf-8') as f:
                        f.write(text)

            # Add bread crumb bar
            self.add_breadcrumbs(pth, parent)
        else:
            self.log('***ignored node***\n')

        # Report how many levels deep the tree is,
        # number of valid nodes, and if this node was empty
        self.navbar.pop(-1)
        self.level -= 1
        return levels_deep, nodes, empty_node

    def run(self, treepath, root='root', site_map=None, quiet=False):
        cwd = getcwd()
        self.quiet = quiet
        self.root = root
        if site_map is not None and not exists(join(treepath, site_map + '.md')):
            self.site_map = site_map
            self.site = '---\ntitle: %s\n---\n[TOC]\n# Index\n\n' % self.site_map
            self.site += '- [%s](./index.html)\n' % self.root
        else:
            self.site_map = None
            self.site = ''
        self.treepath = abspath(treepath)
        self.navbar = []
        chdir(treepath)
        self.log(
            "Building Documents...",
            "================================"
        )
        try:
            self.clear()
            levels_deep, total_nodes, self.is_empty = self.build_node()
            if not self.is_empty:
                self.levels_deep = levels_deep
                self.total_nodes = total_nodes
        except:
            trace = str(traceback.format_exc()).split('\n')
            self.log(*trace)
            self.errors = True
        chdir(cwd)
        return self.errors

if __name__ == "__main__":
    import argparse

    def main():

        parser = argparse.ArgumentParser(prog='Md2HtmlTreeBuilder', description='Build a simple static website from a markdown tree.')
        # Flag arguments
        parser.add_argument('--version', action='version', version="%(prog)s " + __version__)
        parser.add_argument('--debug', action='store_true', default=False, help=argparse.SUPPRESS)
        # Input configuration
        parser.add_argument('--settings', '-s', default=None, help="Specify settings file.")
        parser.add_argument('--root', '-r', default='root', help="Name of root folder.")
        parser.add_argument('--force-update', '-f', action='store_true', default=False, help='Force an update of all files even if the file appears to not need updating.')
        parser.add_argument('--site-map', '-S', default=None, help="Generate a site-map in root with the given name.")
        parser.add_argument('--tab-size', '-t', default=4, type=int, help="Tab size for internal generated markdown. Must match PyMdown settings.")
        parser.add_argument('tree', default=None, help="Tree to build")

        args = parser.parse_args()

        if args.debug:
            global DEBUG
            DEBUG = True

        try:
            tabsize = int(args.tab_size)
            if tabsize <= 0:
                tabsize = 4
        except:
            tabsize = 4

        tree_builder = Md2HtmlTreeBuilder(
            tab_size=tabsize,
            settings=args.settings,
            force_update=args.force_update
        )
        errors = tree_builder.run(
            args.tree, args.root,
            site_map=args.site_map
        )
        print('\n\n============ Results ============')
        print("Documents Found: %d" % tree_builder.processed)
        print("Tree Depth: %d" % tree_builder.levels_deep)
        print("Total Nodes: %d" % tree_builder.total_nodes)
        print('=================================\n')

        if errors:
            print("***Finished with errors.  See output for more info.***")
        else:
            print("***Finished successfully.  See output for more info.***")
        return errors

    sys.exit(main())

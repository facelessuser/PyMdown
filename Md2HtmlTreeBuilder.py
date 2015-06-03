"""
Md2HtmlTreeBuilder.

    Quick and dirty conversion of the tree to a site.

    - If not "force update", update all files whose corresponding HTML file
      is older than the their Markdown source.  Otherwise, update all.
    - If encoutering a folder with just HTML, mark the folder as HTML, it will be
      included in the sitemap, but no further processing is necessary.  All subfolders
      will be excluded.  If the top level HTML folder is missing an 'index' file, one
      will be generated, but none further down.
    - Allow HTML files with no source in Markdown folders.
    - Insert directory list into {{ index }} of HTML index files with no markdown source.
    - Insert navigation elements into {{ nav }} in the template.
    - Title will be obtained from "<title></title>" tags in HTML with no Markdown source.
      Title will be obtained fron "title: " attribute in the frontmatter of Markdown source.
      Title will revert to file name if none of the above can be found.
"""
from __future__ import unicode_literals
from __future__ import print_function
import os
import yaml
import codecs
import re
import subprocess
import traceback
import sys
PY3 = sys.version_info >= (3, 0)

__version__ = '0.0.1'

DEBUG = False

if PY3:
    from urllib.request import pathname2url
    from shlex import quote
    from os import getcwd
else:
    from urllib import pathname2url
    from pipes import quote
    from os import getcwdu as getcwd  # noqa

CRUMB = '<li class="crumb"><a href="%s">%s</a></li>'
BREAD_CRUMBS = '<ul class="bread-crumbs">%s</ul>'

RE_TEMPLATE_NAV = re.compile(r"(\{*?)\{{2}\s*(nav)\s*\}{2}(\}*)")
RE_TEMPLATE_INDEX = re.compile(r"(\{*?)\{{2}\s*(index)\s*\}{2}(\}*)")

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


class Md2HtmlTreeBuilder(object):

    """Build a simple static site using PyMdown."""

    def __init__(self, tab_size=4, settings='pymdown.cfg', force_update=False):
        """Initialize."""

        self.force_update = force_update
        self.quiet = False
        self.level = 0
        self.tab_size = tab_size
        self.settings = settings

    ###########################
    # Logging
    ###########################
    def log(self, *args):
        """Log messages."""

        if not self.quiet:
            for arg in args:
                print(arg)

    ###########################
    # Conversion
    ###########################
    def get_process(self, cmd):
        """Get the prepared subprocess object."""

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
        """Convert file pattern(s) to HTML."""

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
        except Exception:
            self.log(traceback.format_exc())
            self.log("ERROR: Either pymdown wasn't found, or there was a problem parsing a file!")

    def stream_convert(self, text, relpath=None, no_template=False, title='Untitled'):
        """Convert a text object to HTML."""

        results = None
        try:
            cmd = ['pymdown', '-q', '--basepath', '.', '--relpath', relpath, '--title', title]
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
        except Exception:
            trace = str(traceback.format_exc()).split('\n')
            self.log(*trace)
            self.log("ERROR: Either pymdown wasn't found, or there was a problem parsing a file!")
        return results

    def is_archive(self, path):
        """Check if file is the archive/sitemap file."""

        return (
            self.sitemap and
            self.sitemap == os.path.basename(os.path.splitext(path)[0]) and
            os.path.dirname(path) == '.'
        )

    def process_dir(self, folder):
        """Process the directory find updates and preparing a folder map and site map."""

        folder_map = ''
        updates = []
        for name, path, obj in folder['files']:
            folder_map += '- [%s](%s)\n' % (
                name,
                pathname2url(
                    os.path.join(
                        path, 'index.html'
                    ) if 'files' in obj else os.path.join(path)[:-(4 if obj['html'] else 2)] + 'html'
                )
            )
            if 'files' in obj:
                self.archive += ' ' * ((self.tab_size * self.level) + self.tab_size) + '- [%s](%s)\n' % (
                    name,
                    pathname2url(os.path.join(path, 'index.html'))
                )
                self.convert(obj, path)
                continue
            if self.sitemap:
                self.archive += ' ' * ((self.tab_size * self.level) + self.tab_size) + '- [%s](%s)\n' % (
                    name,
                    pathname2url(os.path.join(path)[:-(4 if obj['html'] else 2)] + 'html')
                )
            if self.is_archive(path):
                continue
            if obj['update'] and not obj['html']:
                updates.append(path)
        return updates, folder_map

    def convert(self, folder, folder_path):
        """Initiate convert files in site map."""

        self.level += 1
        self.navbar.append(os.path.basename(folder_path))
        updates, folder_map = self.process_dir(folder)
        update = updates or folder['update']

        self.log("\n==== %s (%s) ====" % (folder_path, 'HTML' if folder['html'] else 'Markdown'))
        self.log(folder_map)
        self.log('--- Updates ---')
        if update:
            self.log(folder_path)
        self.log(*updates)

        if update and not folder['html']:
            if not os.path.exists(os.path.join(folder_path, 'index.md')):
                self.log("Generating %s..." % os.path.join(folder_path, 'index.html'))
                folder_map = self.stream_convert(folder_map, relpath=folder_path, title=folder['index']['name'])
                if folder_map is not None:
                    with codecs.open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as f:
                        f.write(folder_map)
            else:
                folder_map = self.stream_convert(
                    folder_map, relpath=folder_path, no_template=True,
                    title=folder['index']['name']
                )
                updates.append(os.path.join(folder_path, 'index.md'))

            if updates:
                patterns = [os.path.join(folder_path, '*.md')] if self.force_update else updates
                if len(patterns):
                    self.batch_convert(patterns)

            self.add_breadcrumbs(folder_path)

            if os.path.exists(os.path.join(folder_path, 'index.md')):
                try:
                    index_file = os.path.join(folder_path, 'index.html')
                    with codecs.open(index_file, 'r', encoding='utf-8') as f:
                        html_text = f.read()
                    html_text = RE_TEMPLATE_INDEX.sub(
                        lambda m, txt=folder_map: self.repl_index(m, index=txt),
                        html_text
                    )
                    with codecs.open(index_file, 'w', encoding='utf-8', errors="xmlcharrefreplace") as f:
                        f.write(html_text)
                except Exception:
                    print(traceback.format_exc())
                    pass

        self.navbar.pop(-1)
        self.level -= 1

    ###########################
    # Templating
    ###########################
    def add_breadcrumbs(self, path):
        """Add Nav {{ nav }}."""

        for f in os.listdir(path)[:]:
            item = os.path.join(path, f)
            text = ''
            ishtml = os.path.isfile(item) and item.lower().endswith('.html')
            issitemap = self.sitemap is not None and f == self.sitemap + '.html' and path == '.'
            if issitemap or (ishtml and (os.path.exists(item[:-4] + 'md') or f == 'index.html')):
                bread_crumbs = []
                count = 0
                last = len(self.navbar) - 1
                for crumb in reversed(self.navbar):
                    href = ('./' if count == 0 else '../' * count) + 'index.html'
                    name = self.root if count == last else crumb
                    bread_crumbs.insert(0, CRUMB % (href, name))
                    count += 1

                if f != 'index.html':
                    bread_crumbs.append(CRUMB % (pathname2url("./%s" % f), os.path.splitext(f)[0]))

                with codecs.open(item, 'r+', encoding='utf-8') as html:
                    text = html.read()
                    html.seek(0)
                    text = RE_TEMPLATE_NAV.sub(
                        lambda m, bc=bread_crumbs: self.repl_nav(m, bread_crumbs=bc),
                        text
                    )
                    html.write(text)
                    html.truncate()

    def repl_nav(self, m, bread_crumbs):
        """Replace instances of {{ nav }} with breadcrumbs."""

        if m.group(0).startswith('{{{') and m.group(0).endswith('}}}'):
            return m.group(0)[1:-1]
        open = m.group(1) if m.group(1) else ''
        close = m.group(3) if m.group(3) else ''
        return open + (BREAD_CRUMBS % '\n'.join(bread_crumbs)) + close

    def repl_index(self, m, index):
        """Replace instances of {{ index }} with folder index."""

        if m.group(0).startswith('{{{') and m.group(0).endswith('}}}'):
            return m.group(0)[1:-1]
        open = m.group(1) if m.group(1) else ''
        close = m.group(3) if m.group(3) else ''
        return open + index + close

    ###########################
    # Site Crawling
    ###########################
    def needs_update(self, path):
        """Check if HTML file needs to be generated from source."""

        update = self.force_update
        if not update:
            html = path[:-2] + 'html'
            update = not os.path.exists(html)
            if not update:
                ts_html = os.path.getmtime(html)
                ts_md = os.path.getmtime(path)
                update = ts_md > ts_html
        return update

    def handle_folders(self, filename, path):
        """Handle folder crawl."""

        folders = []
        has_md = False
        folder_update = False
        node = {
            "html": False,
            "index": None,
            "update": False,
            "files": []
        }
        folder = os.path.join(path, filename)
        self.crawl(node, folder)
        if node['html'] or len(node['files']) or node['index']:
            if not node['html']:
                has_md = True
            if has_md and node['index'] and not os.path.exists(os.path.join(folder, 'index.md')):
                node['index']['name'] = os.path.basename(folder)
            elif node['index'] is None:
                node['index'] = {"name": os.path.basename(folder), "update": True, "html": False}
            if node['update']:
                folder_update = True
            folders.append([node['index']['name'], folder, node])
        return has_md, folder_update, folders

    def handle_files(self, site, filename, path):
        """Handle process the file."""

        has_md = False
        has_index = False
        files = []
        full_path = os.path.join(path, filename)
        if filename.endswith('.md'):
            if path == '.' and self.sitemap is not None and filename[:-3] == self.sitemap:
                return has_md, has_index, files
            has_md = True
            index = filename == 'index.md'
            needs_update = self.needs_update(full_path)
            if index:
                has_index = True
                site['index'] = {
                    "name": self.get_md_title(
                        full_path, os.path.basename(path)
                    ) if path != '.' else self.root,
                    "update": needs_update,
                    "html": False
                }
            else:
                title = self.get_md_title(full_path, os.path.basename(filename)[:-3])
                files.append([title, full_path, {"name": title, "update": needs_update, "html": False}])
            if needs_update:
                site["update"] = True
        elif filename.endswith('.html'):
            if path == '.' and self.sitemap is not None and filename[:-5] == self.sitemap:
                return has_md, has_index, files
            if not os.path.exists(full_path[:-4] + 'md'):
                index = filename == 'index.html'
                if index:
                    has_index = True
                    site['index'] = {
                        "name": self.get_html_title(full_path, os.path.basename(path)),
                        "update": True,
                        "html": False
                    }
                else:
                    title = self.get_html_title(full_path, os.path.basename(filename)[:-5])
                    files.append([title, full_path, {"name": title, "update": True, "html": True}])
                site["update"] = True
        return has_md, has_index, files

    def crawl(self, site, path='.'):
        """Crawl the directory gathering all relevant files and folders."""

        has_md = False
        has_index = False
        folder_update = False
        folders = []
        files = []
        if not os.path.exists(os.path.join(path, '.md-ignore')):
            for f in sorted(os.listdir(path), key=lambda s: s.lower()):
                if f in ('.svn', '.git') or f.startswith('_'):
                    continue

                if os.path.isfile(os.path.join(path, f)):
                    md_files, is_index, subfile = self.handle_files(site, f, path)
                    has_md = has_md or md_files
                    has_index = has_index or is_index
                    files.extend(subfile)
                else:
                    md_files, subfolder_update, sub_folders = self.handle_folders(f, path)
                    has_md = has_md or md_files
                    folder_update = folder_update or subfolder_update
                    folders.extend(sub_folders)

        html_folder = not has_md and has_index

        if path == '.' and self.sitemap is not None:
            archive = os.path.join(path, self.sitemap + '.html')
            files.append(
                [
                    self.sitemap, archive,
                    {
                        "name": self.sitemap,
                        "update": site['update'] or (not html_folder and folder_update),
                        "html": True
                    }
                ]
            )

        if html_folder:
            site['html'] = True
        elif len(files) or len(folders) or has_index:
            site['files'] = sorted(files + folders)

    def get_html_title(self, html, fallback):
        """Get title from HTML file."""

        title = fallback
        try:
            with codecs.open(html, 'r', encoding='utf-8') as f:
                m = re.search(r'<title>(.*?)</title>', f.read())
                if m:
                    title = m.group(1)
        except Exception:
            pass
        return title

    def get_md_title(self, md, fallback):
        """Get title from Markdown file."""

        title = fallback
        yaml_pattern = re.compile(br'^---[ \t]*\r?\n')
        yaml_lines = []

        try:
            with codecs.open(md, 'rb') as f:
                if yaml_pattern.match(f.readline()) is not None:
                    for line in f:
                        if yaml_pattern.match(line) is None:
                            yaml_lines.append(line)
                        else:
                            try:
                                frontmatter = yaml.load(''.join(yaml_lines).decode('utf-8'))
                                title = frontmatter.get('title', fallback)
                            except Exception:
                                pass
                            break
        except Exception:
            pass
        return title

    ###########################
    # Go!!!
    ###########################
    def run(self, treepath, root='root', sitemap=None, quiet=False):
        """Walk the path converting Markdown source to HTML."""

        cwd = os.getcwd()
        self.quiet = quiet
        self.treepath = os.path.abspath(treepath)
        self.root = root
        self.sitemap = sitemap
        self.archive = ''
        self.navbar = []
        site = {
            "index": None,
            "html": False,
            "update": False,
            "files": []
        }

        os.chdir(treepath)

        self.crawl(site)
        if not site['files'] and site['index'] is None:
            site = {}

        if site:
            if self.sitemap:
                self.archive += '---\ntitle: %s\n---\n[TOC]\n# Index\n\n' % self.sitemap
                self.archive += '- [%s](./index.html)\n' % self.root
            self.level = -1
            self.convert(site, '.')

            if self.sitemap:
                archive = self.stream_convert(self.archive, relpath='.')
                self.log('Generating the site map...')
                if archive is not None:
                    with codecs.open(os.path.join('.', '%s.html' % self.sitemap), 'w', encoding='utf-8') as f:
                        f.write(archive)

                # Add bread crumb bar
                self.navbar.append('.')
                self.add_breadcrumbs('.')
                self.navbar.pop(-1)

        os.chdir(cwd)


if __name__ == "__main__":

    def main():
        """Main function."""

        import argparse

        parser = argparse.ArgumentParser(
            prog='Md2HtmlTreeBuilder',
            description='Build a simple static website from a markdown tree using PyMdown.'
        )
        # Flag arguments
        parser.add_argument(
            '--version',
            action='version',
            version="%(prog)s " + __version__
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            default=False, help=argparse.SUPPRESS
        )
        # Input configuration
        parser.add_argument(
            '--settings', '-s',
            default=None,
            help="Specify settings file."
        )
        parser.add_argument(
            '--root', '-r',
            default='root',
            help="Name of root folder."
        )
        parser.add_argument(
            '--force-update', '-f',
            action='store_true', default=False,
            help='Force an update of all files even if the file appears to not need updating.'
        )
        parser.add_argument(
            '--site-map', '-S',
            default=None,
            help="Generate a site-map in root with the given name."
        )
        parser.add_argument(
            '--tab-size', '-t',
            default=4, type=int,
            help="Tab size for internal generated markdown. Must match PyMdown settings."
        )
        parser.add_argument('tree', default=None, help="Tree to build")

        args = parser.parse_args()

        if args.debug:
            global DEBUG
            DEBUG = True

        try:
            tabsize = int(args.tab_size)
            if tabsize <= 0:
                tabsize = 4
        except Exception:
            tabsize = 4

        tree_builder = Md2HtmlTreeBuilder(
            tab_size=tabsize,
            settings=args.settings,
            force_update=args.force_update
        )
        tree_builder.run(
            args.tree, args.root,
            sitemap=args.site_map
        )
    sys.exit(main())

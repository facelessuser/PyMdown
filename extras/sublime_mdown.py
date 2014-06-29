import sublime
import sublime_plugin
from os.path import basename, dirname
import subprocess


def parse_file_name(file_name):
    if file_name is None:
        title = "Untitled"
        basepath = None
    else:
        title = basename(file_name)
        basepath = dirname(file_name)
    return title, basepath


class MdownPreviewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        title, basepath = parse_file_name(self.view.file_name())
        self.convert(title, basepath)

    def convert(self, title, basepath):
        binary = sublime.load_settings("mdown.sublime-settings").get("binary", None)

        if binary is not None:
            cmd = [binary, "-t", title, "-s", "-p"]
            if basepath is not None:
                cmd += ["-b", basepath]

            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in self.view.lines(sublime.Region(0, self.view.size())):
                p.stdin.write((self.view.substr(line) + '\n').encode('utf-8'))
            print(p.communicate()[0].decode("utf-8"))

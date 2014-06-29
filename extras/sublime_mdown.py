import sublime
import sublime_plugin
from os.path import basename, dirname
import subprocess
import sys

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def parse_file_name(file_name):
    if file_name is None:
        title = "Untitled"
        basepath = None
    else:
        title = basename(file_name)
        basepath = dirname(file_name)
    return title, basepath


class MdownOutputCommand(sublime_plugin.TextCommand):
    message = "<placeholder>"

    def run(self, edit):
        self.title, self.basepath = parse_file_name(self.view.file_name())
        self.binary = sublime.load_settings("mdown.sublime-settings").get("binary", {}).get(_PLATFORM, "")
        self.reject = sublime.load_settings("mdown.sublime-settings").get("critic_reject", False)
        self.cmd = [self.binary, "-T", self.title, "-s"]
        if self.basepath is not None:
            self.cmd += ["-b", self.basepath]
        if self.binary:
            self.convert(edit)

    def convert(self, edit):
        pass

    def call(self):
        print(self.cmd)
        p = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in self.view.lines(sublime.Region(0, self.view.size())):
            p.stdin.write((self.view.substr(line) + '\n').encode('utf-8'))
        text = p.communicate()[0].decode("utf-8")
        self.returncode = p.returncode
        return text

    def error_message(self):
        sublime.error_message(self.message)


class MdownPreviewCommand(MdownOutputCommand):
    message = "mdown failed to generate your preview!"

    def convert(self, edit):
        self.cmd.append("-p")
        if self.reject:
            self.cmd.append("-r")

        print(self.call())
        if self.returncode:
            self.error_message()


class MdownCriticPreviewCommand(MdownOutputCommand):
    message = "mdown failed to generate your preview!"

    def convert(self, edit):
        self.cmd.append("-p")
        self.cmd.append("-c")

        print(self.call())
        if self.returncode:
            self.error_message()


class MdownCriticStripCommand(MdownOutputCommand):
    message = "mdown failed to strip your critic comments!"

    def run(self, edit, reject=False):
        self.title, self.basepath = parse_file_name(self.view.file_name())
        self.binary = sublime.load_settings("mdown.sublime-settings").get("binary", None)
        self.reject = reject
        self.cmd = [self.binary, "-T", self.title, "-s"]
        if self.basepath is not None:
            self.cmd += ["-b", self.basepath]
        if self.binary:
            self.convert(edit)

    def convert(self, edit):
        self.cmd += ["-C", "-p", "-q"]
        if self.reject:
            self.cmd.append("-r")

        text = self.call()
        if self.returncode:
            self.error_message()
        else:
            self.view.replace(edit, sublime.Region(0, self.view.size()), text)

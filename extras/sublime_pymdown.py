import sublime
import sublime_plugin
from os.path import join, basename, dirname, exists, splitext
import _thread as thread
import codecs
import subprocess
import sys
import traceback
try:
    from SubNotify.sub_notify import SubNotifyIsReadyCommand as Notify
except:
    class Notify:
        @classmethod
        def is_ready(cls):
            return False

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def worker_thread(worker_in, worker_out):
    """
    Start worker thread
    """

    WorkerStatus.working

    for pth in worker_in.paths:
        cmd = [worker_in.binary]
        if worker_in.title:
            cmd.append("--title=%s" % worker_in.title)
        if worker_in.basepath:
            cmd.append("--basepath=%s" % worker_in.basepath)
        if worker_in.settings:
            cmd.append("-s", worker_in.settings)
        if worker_in.critic_accept:
            cmd.append('-a')
        else:
            cmd.append('-r')
        if worker_in.batch:
            cmd.append('-b')
        if worker_in.preview:
            cmd.append('-p')

        try:
            if len(worker_in.patterns):
                cmd += [join(pth, p) for p in worker_in.patterns]

                if _PLATFORM == "windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    p = subprocess.Popen(
                        cmd, startupinfo=startupinfo,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                else:
                    p = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )

                text = p.communicate()[0].decode("utf-8")
                status = p.returncode

                worker_out.complete(text, status)
                sublime.set_timeout(lambda x=text: worker_report(x), 0)
                if p.returncode:
                    sublime.set_timeout(
                        lambda x="PyModown: Batch Processing Error Occured!": worker_thread(x, True, True)
                    )
        except:
            sublime.set_timeout(lambda x=str(traceback.format_exc()): worker_report(x), 0)
            sublime.set_timeout(
                lambda x="PyModown: A Batch Command Failed!": worker_thread(x, True, True)
            )

    sublime.set_timeout(lambda x="PyMdown: Batch Job Completed!": worker_report(x, True), 0)
    WorkerStatus.working = False


def worker_report(text, user_notify=False, is_error=False):
    if user_notify:
        if is_error:
            error(text)
        else:
            notify(text)
    else:
        print(text)


def notify(msg):
    settings = sublime.load_settings("reg_replace.sublime-settings")
    if settings.get("use_sub_notify", False) and Notify.is_ready():
        sublime.run_command("sub_notify", {"title": "PyMdown", "msg": msg})
    else:
        sublime.status_message(msg)


def error(msg):
    settings = sublime.load_settings("reg_replace.sublime-settings")
    if settings.get("use_sub_notify", False) and Notify.is_ready():
        sublime.run_command("sub_notify", {"title": "PyMdown", "msg": msg, "level": "error"})
    else:
        sublime.error_message("PyMdown:\n%s" % msg)


def parse_file_name(file_name):
    if file_name is None or not exists(file_name):
        title = "Untitled"
        basepath = None
    else:
        title = basename(file_name)
        basepath = dirname(file_name)
    return title, basepath


def handle_line_endings(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')


class WorkerStatus(object):
    working = False


class WorkerInput(object):
    def __init__(self):
        self.binary = None
        self.critic_accept = True
        self.paths = []
        self.patterns = ['*.mdown', '*.markdown', '*.markdn', '*.md']
        self.title = None
        self.basepath = None
        self.batch = False
        self.preview = False
        self.settings = None
        self.callback = None


class WorkerOutput(object):
    def __init__(self):
        self.result = ''
        self.status = 0

    def complete(self, result, status):
        self.result = result
        self.status = status


class PyMdownBatchCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], preview=False):
        if not WorkerStatus.working:
            w_in = WorkerInput()
            w_in.binary = sublime.load_settings("pymdown.sublime-settings").get("binary", {}).get(_PLATFORM, "")
            w_in.critic_accept = sublime.load_settings("pymdown.sublime-settings").get("critic_reject", False)
            w_in.batch = True
            w_in.paths = paths
            w_in.preview = preview
            thread.start_new_thread(worker_thread, (w_in, WorkerOutput()))

    def is_enabled(self, paths=[], patterns=[]):
        return not WorkerStatus.working


class PyMdownInsertText(sublime_plugin.TextCommand):
    wbfr = None

    def run(self, edit, save=False):
        self.view.insert(edit, 0, handle_line_endings(PyMdownInsertText.wbfr))
        PyMdownInsertText.clear_wbfr()
        if save:
            self.view.run_command('save')

    @classmethod
    def set_wbfr(cls, text):
        cls.wbfr = text

    @classmethod
    def clear_wbfr(cls):
        cls.wbfr = None


class PyMdownCommand(sublime_plugin.TextCommand):
    message = "<placeholder>"

    def setup(self, alternate_settings=None):
        self.title, self.basepath = parse_file_name(self.view.file_name())
        self.binary = sublime.load_settings("pymdown.sublime-settings").get("binary", {}).get(_PLATFORM, "")
        self.reject = sublime.load_settings("pymdown.sublime-settings").get("critic_reject", False)
        self.settings = alternate_settings
        self.cmd = [self.binary, "--title=%s" % self.title]
        if self.basepath is not None:
            self.cmd += ["--basepath=%s" % self.basepath]
        if self.settings is not None and exists(self.settings):
            self.cmd += ["-s", self.settings]

    def convert(self, edit):
        pass

    def call(self):
        print(self.cmd)
        if _PLATFORM == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            p = subprocess.Popen(
                self.cmd, startupinfo=startupinfo,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        else:
            p = subprocess.Popen(
                self.cmd,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        sels = self.view.sel()
        regions = []
        if len(sels):
            for sel in sels:
                if sel.size():
                    regions.append(sel)
        if len(regions) == 0:
            regions.append(sublime.Region(0, self.view.size()))
        for region in regions:
            for line in self.view.lines(region):
                p.stdin.write((self.view.substr(line) + '\n').encode('utf-8'))
        text = p.communicate()[0].decode("utf-8")
        self.returncode = p.returncode
        return text

    def error_message(self):
        error(self.message)


class PyMdownPreviewCommand(PyMdownCommand):
    message = "pymdown failed to generate html!"

    def run(self, edit, target="browser", plain=False, alternate_settings=None):
        self.setup(alternate_settings)
        self.target = target
        self.plain = plain
        if self.binary:
            self.convert(edit)

    def output(self, rbfr):
        if self.target == "browser":
            # Nothing to do
            notify("Conversion complete!\nOpening in browser...")
            # print(handle_line_endings(rbfr))
        elif self.target == "clipboard":
            sublime.set_clipboard(rbfr)
            notify("Conversion complete!\nResult copied to clipboard.")
        elif self.target == "sublime":
            window = self.view.window()
            if window is not None:
                view = window.new_file()
                PyMdownInsertText.set_wbfr(rbfr)
                view.run_command("py_mdown_insert_text")
                notify("Conversion complete!\nResult exported to Sublime.")
            else:
                error("Could not export!\nView has no window")
        elif self.target == "save":
            save_location = self.view.file_name()
            if save_location is None or not exists(save_location):
                # Save as...
                window = self.view.window()
                if window is not None:
                    view = window.new_file()
                    if view is not None:
                        PyMdownInsertText.set_wbfr(rbfr)
                        view.run_command("pymdown_insert_text", {"save": True})
                        notify("Conversion complete!\nReady to save...")
                    else:
                        error("Failed to create new view!")
                else:
                    error("Could not save!\nView has no window")
            else:
                # Save
                htmlfile = splitext(save_location)[0] + '.html'
                try:
                    with codecs.open(htmlfile, "w", encoding="utf-8") as f:
                        f.write(rbfr)
                    notify("Conversion complete!\nHtml saved.")
                except:
                    print(traceback.format_exc())
                    error("Failed to save file!")

    def convert(self, edit):
        if self.target == "browser":
            self.cmd.append("-p")
        else:
            self.cmd.append("-q")

        if self.plain:
            self.cmd.append("-P")

        if self.reject:
            self.cmd.append("-r")
        else:
            self.cmd.append('-a')

        rbfr = self.call()

        if self.returncode:
            if self.target == "browser":
                print(rbfr)
            self.error_message()
        else:
            self.output(rbfr)


class PyMdownCriticStripCommand(PyMdownCommand):
    message = "pymdown failed to strip your critic comments!"

    def run(self, edit, reject=False, alternate_settings=None):
        self.setup(alternate_settings)
        self.reject = reject
        if self.binary:
            self.convert(edit)

    def convert(self, edit):
        self.cmd += ["--critic-dump", "-q"]
        if self.reject:
            self.cmd.append("-r")
        else:
            self.cmd.append("-a")

        text = self.call()
        if self.returncode:
            self.error_message()
        else:
            self.view.replace(edit, sublime.Region(0, self.view.size()), handle_line_endings(text))
            notify("Critic stripping succesfully completed!")

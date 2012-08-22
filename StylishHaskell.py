import sublime
import sublime_plugin
import subprocess
import errno
import os
import tempfile


s = sublime.load_settings("StylishHaskell.sublime-settings")
paths = s.get('add_to_PATH')

if not any(paths):
    try:
        sublHask = sublime.load_settings("SublimeHaskell.sublime-settings")
        paths = sublHask.get("add_to_PATH")
    except:
        pass

path = ':'.join(paths)


class StylishhaskellCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        regions = []
        for region in self.view.sel():
            # If no selection, use the entire file as the selection
            regions.append(sublime.Region(region.a, region.b))
            if region.empty() and s.get("use_entire_file_if_no_selection"):
                selection = sublime.Region(0, self.view.size())
            else:
                selection = region
            try:
                result = self.callStylish(self.view.substr(selection))
                if result:
                    self.view.replace(edit, selection, result)
            except Exception as e:
                sublime.status_message(str(e))
        self.view.sel().clear()
        for region in regions:

            self.view.sel().add(region)

    def callStylish(self, string):
        try:
            env = os.environ
            env["PATH"] = (path + ":" if path else "") + os.environ['PATH']
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(string)
            tfile.close()
            p2 = subprocess.Popen("stylish-haskell " + tfile.name, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, shell=True)
            result = p2.communicate()[0]
            os.unlink(tfile.name)
            return result
        except OSError as e:
            if e.errno == errno.ENOENT:
                sublime.error_message("StylishHaskell: stylish-haskell executable was not found!\n"
                    + "Try adjusting the 'add_to_PATH' setting.\n")
        except Exception as e:
            sublime.error_message("error " + str(e))

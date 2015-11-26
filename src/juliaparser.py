import os
import subprocess


class JuliaParser:
    cached_files = {}

    def parsefile(self, sourcepath):
        if not os.path.exists(sourcepath):
            raise ValueError("Can't parse julia file: " + sourcepath)
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, "parsefile.jl")
        p = subprocess.Popen(["julia", scriptpath, sourcepath],
                stdout=subprocess.PIPE, universal_newlines=True)
        (buf, err) = p.communicate()
        if err:
            raise Exception(err)
        d = eval(buf)
        self.cached_files[sourcepath] = d
        return d

    def functions_from_file(self, sourcepath):
        if sourcepath in self.cached_files:
            d = self.cached_files[sourcepath]
        else:
            d = self.parsefile(sourcepath)
        return d

    def function_from_file(self, sourcepath, functionname):
        if sourcepath in self.cached_files:
            d = self.cached_files[sourcepath]
        else:
            d = self.parsefile(sourcepath)
        for func in d:
            if func["name"] == functionname:
                return func

    def parsefunction(self, functionstring):
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, "parsefunc.jl")
        p = subprocess.Popen(["julia", scriptpath, functionstring],
                stdout=subprocess.PIPE, universal_newlines=True)
        (buf, err) = p.communicate()
        function = eval(buf)
        return function

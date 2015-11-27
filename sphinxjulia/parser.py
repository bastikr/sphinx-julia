import os
import subprocess

scriptname_parsefile = "parsetools/parsefile.jl"
scriptname_parsefunc = "parsetools/parsefunc.jl"


class JuliaParser:
    cached_files = {}

    def parsefile(self, sourcepath):
        if not os.path.exists(sourcepath):
            raise ValueError("Can't parse julia file: " + sourcepath)
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptname_parsefile)
        p = subprocess.Popen(["julia", scriptpath, sourcepath],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
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
            if func["qualifier"]+"."+func["name"] == functionname:
                return func
        for func in d:
            if func["name"] == functionname:
                return func
        errortext = "Function {} not found in: {}"
        raise ValueError(errortext.format(functionname, sourcepath))

    def parsefunction(self, functionstring):
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptname_parsefunc)
        p = subprocess.Popen(["julia", scriptpath, functionstring],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        (buf, err) = p.communicate()
        if err:
            raise Exception(err)
        function = eval(buf)
        return function

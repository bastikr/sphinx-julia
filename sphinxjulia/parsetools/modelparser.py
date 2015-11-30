import os
import subprocess
import model

scriptdir = "scripts"
scripts = {
    "file": "sourcefile2pythonmodel.jl",
    "abstracttype": "parse_abstracttype.jl",
    "compositetype": "parse_compositetype.jl",
    "module": "parse_module.jl",
    "function": "parse_function.jl"
}

eval_environment = {x: getattr(model, x) for x in dir(model) if not x.startswith("_")}

class JuliaParser:
    cached_files = {}

    def parsefile(self, sourcepath):
        if not os.path.exists(sourcepath):
            raise ValueError("Can't find file: " + sourcepath)
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptdir, scripts["file"])
        p = subprocess.Popen(["julia", scriptpath, sourcepath],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        (buf, err) = p.communicate()
        if err:
            raise Exception(err)
        model = eval(buf, eval_environment)
        self.cached_files[sourcepath] = model
        return model

    def parsestring(self, objtype, text):
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptdir, scripts[objtype])
        p = subprocess.Popen(["julia", scriptpath, text],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True)
        (buf, err) = p.communicate()
        if err:
            raise Exception(err)
        model = eval(buf, eval_environment)
        return model

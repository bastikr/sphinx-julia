"""
Convert a valid Julia code to its corresponding JuliaModel.

Uses the julia native parse function to generate an AST, then creates
the JuliaModel in python.
"""
from __future__ import unicode_literals

import os
import subprocess

from sphinx.util import logging
logger = logging.getLogger(__name__)

from . import model

try:
    import julia
except ImportError:
    logger.warn("PyJulia not found - using slower alternative.")
    julia = None

scriptdir = "parsetools/scripts"
scripts = {
    "file": "sourcefile2pythonmodel.jl",
}
eval_environment = {x: getattr(model, x) for x in dir(model) if not x.startswith("_")}

class ParseError(Exception):
    def __init__(self, source, errormessage):
        self.source = source
        self.errormessage = errormessage


class JuliaParser:
    cached_files = {}
    _julia = None

    @property
    def julia(self):
        if isinstance(self._julia, Exception):
            return None
        elif self._julia is None:
            try:
                self._julia = julia.Julia()
            except Exception as e:
                logger.warn("Creating julia.Julia raised an error - falling back to slower alternative.")
                self._julia = e
                return None
        return self._julia

    def parsefile(self, sourcepath):
        sourcepath = os.path.realpath(sourcepath)
        if not os.path.exists(sourcepath):
            raise ValueError("Can't find file: " + sourcepath)
        if sourcepath in self.cached_files:
            return self.cached_files[sourcepath]
        if self.julia:
            return self.parsefile_pyjulia(sourcepath)
        else:
            return self.parsefile_script(sourcepath)

    def parsefile_pyjulia(self, sourcepath):
        j = self.julia
        current_dir= os.path.dirname(os.path.realpath(__file__))
        parsetools_dir = os.path.join(current_dir, "parsetools/src/")

        j.eval('push!(LOAD_PATH, "{}")'.format(parsetools_dir))
        j.eval('using parsetools')
        j.eval('model = parsetools.reader.read_file("{}")'.format(sourcepath))
        text = j.eval('string(model)')
        model = eval(text, eval_environment)
        self.cached_files[sourcepath] = model
        return model

    def parsefile_script(self, sourcepath):
        directory = os.path.dirname(os.path.realpath(__file__))
        scriptpath = os.path.join(directory, scriptdir, scripts["file"])
        p = subprocess.Popen(["julia", scriptpath, sourcepath],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (buf, err) = p.communicate()
        if p.returncode != 0:
            print("Parsing file {} failed with error message:".format(sourcepath))
            print("-"*80)
            print(err.decode("utf-8"))
            print("-"*80)
            raise ParseError(sourcepath, err)
        # buf is a bytestring in utf-8 encoding.
        text = buf.decode("utf-8")
        model = eval(text, eval_environment)
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
            print("Parsing {} from string:".format(objtype))
            print("-"*80)
            print(text)
            print("-"*80)
            print("failed with error message:")
            print("-"*80)
            print(err.decode("utf-8"))
            print("-"*80)
            raise ParseError(text, err)
        model = eval(buf, eval_environment)
        return model

    def __getstate__(self):
        return {"cached_files": self.cached_files}

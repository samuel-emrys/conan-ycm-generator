import json
import os

from conan.tools.files import save

def prefixed(prefix, values):
    return [prefix + x for x in values]

def cppstd_to_flag(cppstd: str) -> str:
    if not cppstd:
        # Default to c++14 to account for older libraries
        return "c++14"
    if "gnu" in cppstd:
        version = cppstd.split("gnu")[1]
        return f"gnu++{version}"
    return f"c++{cppstd}"

class ycm:

    def __init__(self, conanfile):
        self._conanfile = conanfile
        self._template = """
# This file is NOT licensed under the GPLv3, which is the license for the rest
# of YouCompleteMe.
#
# Here's the license text for this file:
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>

import os
import json
import ycm_core
import logging
import pathlib


_logger = logging.getLogger(__name__)


def DirectoryOfThisScript():
  return os.path.dirname( os.path.abspath( __file__ ) )


# These are the compilation flags that will be used in case there's no
# compilation database set (by default, one is not set).
# CHANGE THIS LIST OF FLAGS. YES, THIS IS THE DROID YOU HAVE BEEN LOOKING FOR.
flags = [
 '--std={cxx_std}',
 '-x',
 'c++',
]

with open(".conan_ycm_path") as f:
    contents = f.readline()
    conan_ycm_path = pathlib.Path(contents)

if not conan_ycm_path.exists():
    raise Exception(f"{{conan_ycm_path}} doesn't exist!")

conan_flags = json.loads(open(conan_ycm_path / "conan_ycm_flags.json", "r").read())

flags.extend(conan_flags["flags"])
flags.extend(conan_flags["defines"])
flags.extend(conan_flags["includes"])


# Set this to the absolute path to the folder (NOT the file!) containing the
# compile_commands.json file to use that instead of 'flags'. See here for
# more details: http://clang.llvm.org/docs/JSONCompilationDatabase.html
#
# You can get CMake to generate this file for you by adding:
#   set( CMAKE_EXPORT_COMPILE_COMMANDS 1 )
# to your CMakeLists.txt file.
#
# Most projects will NOT need to set this to anything; you can just change the
# 'flags' list of compilation flags. Notice that YCM itself uses that approach.
compilation_database_folder = os.path.join(DirectoryOfThisScript(), 'Debug')

if os.path.exists( compilation_database_folder ):
  database = ycm_core.CompilationDatabase( compilation_database_folder )
  if not database.DatabaseSuccessfullyLoaded():
      _logger.warn("Failed to load database")
      database = None
else:
  database = None

SOURCE_EXTENSIONS = [ '.cpp', '.cxx', '.cc', '.c', '.m', '.mm' ]

def GetAbsolutePath(include_path, working_directory):
    if os.path.isabs(include_path):
        return include_path
    return os.path.join(working_directory, include_path)


def MakeRelativePathsInFlagsAbsolute( flags, working_directory ):
  if not working_directory:
    return list( flags )
  new_flags = []
  make_next_absolute = False
  path_flags = [ '-isystem', '-I', '-iquote', '--sysroot=' ]
  for flag in flags:
    new_flag = flag

    if make_next_absolute:
      make_next_absolute = False
      new_flag = GetAbsolutePath(flag, working_directory)

    for path_flag in path_flags:
      if flag == path_flag:
        make_next_absolute = True
        break

      if flag.startswith( path_flag ):
        path = flag[ len( path_flag ): ]
        new_flag = flag[:len(path_flag)] + GetAbsolutePath(path, working_directory)
        break

    if new_flag:
      new_flags.append( new_flag )
  return new_flags


def IsHeaderFile( filename ):
  extension = os.path.splitext( filename )[ 1 ]
  return extension.lower() in [ '.h', '.hxx', '.hpp', '.hh' ]


def GetCompilationInfoForFile( filename ):
  # The compilation_commands.json file generated by CMake does not have entries
  # for header files. So we do our best by asking the db for flags for a
  # corresponding source file, if any. If one exists, the flags for that file
  # should be good enough.
  if IsHeaderFile( filename ):
    basename = os.path.splitext( filename )[ 0 ]
    for extension in SOURCE_EXTENSIONS:
      replacement_file = basename + extension
      if os.path.exists( replacement_file ):
        compilation_info = database.GetCompilationInfoForFile( replacement_file )
        if compilation_info.compiler_flags_:
          return compilation_info
    return None
  return database.GetCompilationInfoForFile( filename )


def Settings( filename, **kwargs ):
  relative_to = None
  compiler_flags = None

  if database:
    # Bear in mind that compilation_info.compiler_flags_ does NOT return a
    # python list, but a "list-like" StringVec object
    compilation_info = GetCompilationInfoForFile( filename )
    if compilation_info is None:
      relative_to = DirectoryOfThisScript()
      compiler_flags = flags
    else:
      relative_to = compilation_info.compiler_working_dir_
      compiler_flags = compilation_info.compiler_flags_

  else:
    relative_to = DirectoryOfThisScript()
    compiler_flags = flags

  final_flags = MakeRelativePathsInFlagsAbsolute( compiler_flags, relative_to )
  for flag in final_flags:
      if flag.startswith("-W"):
          final_flags.remove(flag)
  _logger.info("Final flags for %s are %s" % (filename, ' '.join(final_flags)))

  return {{
    'flags': final_flags + ["-I./include", "-I/usr/include", "-I/usr/include/c++/{cxx_version}"],
    'do_cache': True
  }}
"""

    def generate(self):
        conan_flags = {
            "includes": [],
            "defines": [],
            "flags": [],
        }
        for name, dep in self._conanfile.dependencies.items():
            conan_flags["includes"].extend(prefixed("-isystem", dep.cpp_info.includedirs))
            conan_flags["defines"].extend(prefixed("-D", dep.cpp_info.defines))
            conan_flags["flags"].extend(dep.cpp_info.cxxflags)

        cxx_version = ""
        try:
            cxx_version = str(self._conanfile.settings.compiler.version).split(".")[0]
        except Exception:
            pass

        cxx_std = cppstd_to_flag(str(self._conanfile.settings.get_safe("compiler.cppstd")))
        ycm_data = self._template.format(cxx_std=cxx_std, cxx_version=cxx_version)
        flags_data = json.dumps(conan_flags, indent=4)

        save(self._conanfile, os.path.join(self._conanfile.generators_folder, "conan_ycm_extra_conf.py"), ycm_data)
        save(self._conanfile, os.path.join(self._conanfile.generators_folder, "conan_ycm_flags.json"), flags_data)
        save(self._conanfile, os.path.join(self._conanfile.recipe_folder, ".conan_ycm_path"), self._conanfile.generators_folder)

# ycm generator

This generator exists largely to replace the functionality made available by the `ycm` generator that was previously distributed with the conan client, and has been deprecated and removed in conan 2.0.

This generator will generate `.conan_ycm_path` in your project root folder, and `conan_ycm_extra_conf.py` and `conan_ycm_flags.json` in your generators folder. These files will be overwritten each time you run `conan install` or `conan build`.

## Installation

```bash
$ conan config install https://github.com/samuel-emrys/conan-ycm-generator.git --type git
```

## Usage

```bash
$ conan install . -g ycm
```

Copy `conan_ycm_extra_conf.py` to the project root folder with the name `.ycm_extra_conf.py`. You can (and probably should) edit this file to add your project specific configuration.

```bash
$ cp build/Release/generators/conan_ycm_extra_conf.py .ycm_extra_conf.py
```

This file will determine which build configuration to use for autocompletion and symbol resolution based on the last execution of `conan install`. To illustrate, assuming that `conanfile.generators_folder=build/<build_type>/generators`:

```bash
$ conan install . -s:h build_type=Debug -g ycm # will look for build/Debug/generators/conan_ycm_flags.json
$ conan install . -s:h build_type=Release -g ycm # will look for build/Release/generators/conan_ycm_flags.json
```

This is discovered based on the path to the build folder, contained within `.conan_ycm_path`.

NOTE: This is project configuration specific to the user, so these files would normally not be committed to your version control. You may add the following to your `.gitignore`:

```
build/
.conan_ycm_path
.ycm_extra_conf
conan_ycm_extra_conf.py
conan_ycm_flags.json
```

## Support

* For support regarding this generator, please open an issue.
* For support regarding YouCompleteMe, see the [YouCompleteMe Documentation](https://ycm-core.github.io/YouCompleteMe/)

from os.path import expanduser
from conans import ConanFile, CMake, tools
import os


class XalanCConan(ConanFile):
    name = "xalan-c"
    version = "1.12.0"
    license = "Apache-2.0" 
    author = "None"
    requires = "xerces-c/3.2.3@_/_"
    description = """Xalan-C++ version is a robust implementation of the W3C Recommendations for XSL Transformations (XSLT) and the XML Path Language (XPath). It works with the Xerces-C++ XML parser.
                    The Xalan-C++ project creates and distributes a standard XSLT library and a simple Xalan command-line utility for transforming XML documents.""" 
    topics = ("xml", "XSLT", "xalan", "xalan-c", "xalan-c++")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared":[True],
        "fPIC":[True, False]
    }
    default_options={"shared": True, "fPIC": False, "xerces-c:shared": True}
    generators = "cmake", "cmake_find_package"
    url = "https://github.com/djimenezgallegos/xalanc_recipe"
    _cmake = None
    _temp_folder = None
    _source_folder = None
    _build_folder = None
    _lib_folder = None
    _bin_folder = None

    def imports(self):
        self._temp_folder = expanduser("~") + "/xalan-c"
        self._build_folder = self._temp_folder + "/build"
        self._lib_folder = self._build_folder + "/lib"
        self._bin_folder = self._build_folder + "/bin"
        self.copy("*.dll", dst=self._bin_folder, src="bin")
        self.copy("*xerces-c*.lib", dst=self._bin_folder, src="lib")
        self.copy("*.so", dst=self._bin_folder, src="lib")

    def build_requirements(self):
        self.build_requires("xerces-c/3.2.3@_/_", force_host_context=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os not in ("Windows", "Macos", "Linux"):
            raise ConanInvalidConfiguration("OS is not supported")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # https://apache.github.io/xalan-c/build.html
        self._cmake.definitions["transcoder"] = "default"
        self._cmake.definitions["message-loader"] = "inmemory"
        self._cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_CURL"] = True
        self._cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_ICU"] = True
        self._cmake.definitions["CMAKE_ARCHIVE_OUTPUT_DIRECTORY"] = self._lib_folder
        self._cmake.definitions["CMAKE_LIBRARY_OUTPUT_DIRECTORY"] = self._lib_folder
        self._cmake.definitions["CMAKE_RUNTIME_OUTPUT_DIRECTORY"] = self._bin_folder
        
        if self.settings.os == "Windows":
            self._cmake.definitions["CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE"] = self._bin_folder
            self._cmake.definitions["CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG"] = self._bin_folder
            self._cmake.definitions["CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG"] = self._lib_folder
            self._cmake.definitions["CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE"] = self._lib_folder
            self._cmake.definitions["CMAKE_ARCHIVE_OUTPUT_DIRECTORY_DEBUG"] = self._lib_folder
            self._cmake.definitions["CMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELEASE"] = self._lib_folder

        self._cmake.configure(source_folder=self._source_folder, build_folder=self._build_folder)
        return self._cmake

    def source(self):
        git = tools.Git(folder="xalan-c")
        git.clone(url="https://github.com/apache/xalan-c.git", branch="Xalan-C_1_12_0", shallow=True)
        self._source_folder = git.get_repo_root()
        
    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_folder)
        cmake = self._configure_cmake()
        cmake.install()
        # remove unneeded directories
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        #remove tempfolder
        tools.rmdir(self._temp_folder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.names["cmake_find_package"] = "XalanC"
        self.cpp_info.names["cmake_find_package_multi"] = "XalanC"

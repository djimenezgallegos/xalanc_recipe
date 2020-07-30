from os.path import expanduser
from conans import ConanFile, CMake, tools
import os


class XalanCConan(ConanFile):
    name = "xalan-c"
    version = "1.12.0"
    license = "Apache-2.0" 
    author = "None"
    description = """Xalan-C++ version is a robust implementation of the W3C Recommendations for XSL Transformations (XSLT) and the XML Path Language (XPath). It works with the Xerces-C++ XML parser.
                    The Xalan-C++ project creates and distributes a standard XSLT library and a simple Xalan command-line utility for transforming XML documents.""" 
    topics = ("xml", "XSLT", "xalan", "xalan-c", "xalan-c++")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC":[True, False],
        "xerces_shared":[True, False]
    }
    default_options = {"fPIC": True, "xerces_shared":False}
    generators = "cmake", "cmake_find_package"
    url = "https://github.com/djimenezgallegos/xalanc_recipe"
    _cmake = None
    #delete temp folder manually when not needed
    _temp_folder = os.path.join(expanduser("~"), "conan_build", "xalan-c")
    _source_folder = os.path.join(_temp_folder, "git")
    _build_folder =  os.path.join(_temp_folder, "build")
    _lib_folder = os.path.join(_build_folder, "lib")
    _bin_folder = os.path.join(_build_folder, "bin")

    def _cleanUp(self):
        if os.path.exists(self._build_folder):
            tools.rmdir(self._build_folder)

    def imports(self):
        self._cleanUp()
        self.copy("*.dll", dst=self._bin_folder, src="bin")
        self.copy("*.lib", dst=self._lib_folder, src="lib")
        self.copy("*.a", dst=self._lib_folder, src="lib")
        self.copy("*.so", dst=self._lib_folder, src="lib")

    def requirements(self):
        self.requires("xerces-c/3.2.3@_/_")

    def build_requirements(self):
        self.build_requires("xerces-c/3.2.3@_/_", force_host_context=True)

    def config_options(self):
        del self.options.static
        if self.settings.os == "Windows":
            del self.options.fPIC


    def configure(self):
        if self.settings.os not in ("Windows", "Macos", "Linux"):
            raise ConanInvalidConfiguration("OS is not supported")
        if self.options.xerces_shared == True:
            self.options["xerces-c"].shared = True

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # https://apache.github.io/xalan-c/build.html
        self._cmake.definitions["transcoder"] = "default"
        self._cmake.definitions["message-loader"] = "inmemory"
        self._cmake.definitions["BUILD_SHARED_LIBS:BOOL"] = "ON"
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
        if os.path.exists(self._source_folder):
            tools.rmdir(self._source_folder)
        git = tools.Git(folder=self._source_folder)
        git.clone(url="https://github.com/apache/xalan-c.git", branch="Xalan-C_1_12_0", shallow=True)
        
        
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
        tools.rmdir(self._build_folder) #delete build folder after every build

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        self.cpp_info.names["cmake_find_package"] = "XalanC"
        self.cpp_info.names["cmake_find_package_multi"] = "XalanC"

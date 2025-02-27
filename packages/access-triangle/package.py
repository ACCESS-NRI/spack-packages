# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
# ----------------------------------------------------------------------------
#
#     spack install access-triangle-git
#
# You can edit this file again by typing:
#
#     spack edit access-triangle-git
#
# ----------------------------------------------------------------------------

from spack.package import *
import glob
import os


class AccessTriangle(MakefilePackage):
    """Spack package for the ISSM Triangle library."""

    homepage = "https://github.com/ACCESS-NRI/issm-triangle"
    git = 'https://github.com/ACCESS-NRI/issm-triangle.git'

    version('main')

    # # If on some systems 'gmake' is truly required, keep it. Otherwise, 'make'
    # # is often sufficient because Spack sets MAKE appropriately.
    depends_on('gmake',  type='build')
    depends_on('libx11', type='link')
    
    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/issm-triangle/archive/refs/heads/{0}.tar.gz".format(version)

    def edit(self, spec, prefix):
        """
        Below, we just copy in the 'configs'
        so that the build can find them in `self.build_directory`.
        """
        src_dir = join_path(self.stage.source_path, "src")
        mkdirp(src_dir)
        
        # Copy necessary files to src directory
        install('configs/makefile', src_dir)
        install('configs/linux/configure.make', src_dir)
        install('triangle.c', src_dir)
        install('triangle.h', src_dir)
        
    def build(self, spec, prefix):
        """
        This is where we actually call `make shared`.
        Using MakefilePackage, you *could* rely on build_targets,
        but we'll be explicit here so you can see it clearly.
        """
        with working_dir(join_path(self.stage.source_path, "src")):
            make('shared')
            
        #raise an exception

    def install(self, spec, prefix):
        """
        Copy the resulting library and headers into the Spack prefix.
        """
        src = join_path(self.stage.source_path, "src")

        # Create prefix directories
        mkdirp(prefix.include)
        mkdirp(prefix.lib)

        with working_dir(src):
            # Make sure we see what's actually there, for debugging:
            ls_output = Executable('ls')('-l', '.', output=str, error=str)
            print("Files in build directory:\n", ls_output)
            
            install('triangle.h', prefix.include)

            for libfile in glob.glob("libtriangle.*"):
                install(libfile, prefix.lib)

            


            

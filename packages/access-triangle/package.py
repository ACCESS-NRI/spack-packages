# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.package import *
import glob
import os


class AccessTriangle(MakefilePackage):
    """Triangle is a two-dimensional mesh generator and Delaunay
    triangulator. Triangle generates exact Delaunay triangulations,
    constrained Delaunay triangulations, conforming Delaunay
    triangulations, Voronoi diagrams, and high-quality triangular
    meshes."""

    homepage = "https://github.com/ACCESS-NRI/issm-triangle"
    git = 'https://github.com/ACCESS-NRI/issm-triangle.git'

    version('main')
    
    # variant for building the showme utility (requires X11).
    variant('showme', default=False,
            description='Build the showme utility (requires libX11).')

    # Make libX11 conditional on +showme
    depends_on('libx11', when='+showme', type='link')
    
    def url_for_version(self, version):
        return "https://github.com/ACCESS-NRI/issm-triangle/archive/refs/heads/{0}.tar.gz".format(version)

    def edit(self, spec, prefix):
        """
        This stage is where you typically patch or customise the makefile.
        If the package comes with a pre-written Makefile that needs minimal
        changes, you can do them here. Below, we just copy in the 'configs'
        so that the build can find them in `src_dir`.
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
        Using MakefilePackage, you *could* rely on build_targets
        """
        with working_dir(join_path(self.stage.source_path, "src")):
            make('shared')
            if '+showme' in spec:
                make('showme')
            

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
            
            # Install showme only if +showme is chosen
            if '+showme' in spec:
                install('showme', prefix.bin)

            


            

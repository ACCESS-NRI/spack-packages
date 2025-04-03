# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright 2023 Angus Gibson
# Modified by Justin Kin Jun Hew, 2025
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
import sys


class Issm(AutotoolsPackage):
    """Ice-sheet and Sea-Level System Model"""

    homepage = "https://issm.jpl.nasa.gov/"
    git = "https://github.com/ACCESS-NRI/ISSM.git"

    maintainers("justinh2002")

    version("upstream", branch="main", git="https://github.com/ISSMteam/ISSM.git")
    
    version("main", branch="main", git="https://github.com/ACCESS-NRI/ISSM.git")
    version("access-development", branch="access-development", git="https://github.com/ACCESS-NRI/ISSM.git", preferred=True)

    variant("wrappers", default=False,
            description="Enable building with MPI wrappers")
    #
    # Build dependencies
    #
    depends_on("autoconf", type="build")
    depends_on("automake", type="build")
    depends_on("libtool",  type="build")
    depends_on("m4",       type="build")
    depends_on("mpi")
    depends_on("petsc+metis+mumps+scalapack")
    depends_on("m1qn3")

    conflicts("%gcc@14:", msg="ISSM cannot be built with GCC versions above 13")
    #
    # Optional libraries
    #
    depends_on('access-triangle', when='+wrappers')
    depends_on("parmetis",  when="+wrappers")
    depends_on("python@3.9.2:", when="+wrappers", type=("build", "run"))
    depends_on("py-numpy", when="+wrappers", type=("build", "run"))

    def url_for_version(self, version):
        # Example of how you might form a URL for a particular version:
        return "https://github.com/ACCESS-NRI/ISSM/archive/refs/heads/{0}.tar.gz".format(version)

    def autoreconf(self, spec, prefix):
        # If the repo has an Autotools build system, run autoreconf:
        autoreconf("--install", "--verbose", "--force")
        
    def setup_run_environment(self, env):
        env.prepend_path("LD_LIBRARY_PATH", self.prefix.lib)

    def configure_args(self):
        """Populate configure arguments, including optional flags to mimic 
        your manual `./configure` invocation on Gadi."""
        args = [
            "--enable-debugging",
            "--enable-development",
            "--enable-shared",
            "--without-kriging",
        ]

        #
        # Wrappers
        #
        if "+wrappers" in self.spec:
            args.append("--with-wrappers=yes")        
            args.append("--with-parmetis-dir={0}".format(self.spec["parmetis"].prefix))
            args.append("--with-triangle-dir={0}".format(self.spec["access-triangle"].prefix))
            python_spec = self.spec["python"]
            python_version = python_spec.version.up_to(2)
            python_prefix = self.spec["python"].prefix

            args.append("--with-python-version={0}".format(python_version))
            args.append("--with-python-dir={0}".format(python_prefix))

            numpy_prefix = self.spec['py-numpy'].prefix
            numpy_include_dir = join_path(self.spec['py-numpy'].prefix, 'lib', 'python{0}'.format(self.spec['python'].version.up_to(2)), 'site-packages', 'numpy')
            args.append("--with-python-numpy-dir={0}".format(numpy_include_dir))
        else:
            args.append("--with-wrappers=no")

        #
        # MPI: Even if we use Spack's MPI wrappers, the build system may 
        # want explicit mention of MPI includes and compilers:
        #
        args.append("--with-mpi-include={0}".format(self.spec["mpi"].prefix.include))
        args.append("CC=" + self.spec["mpi"].mpicc)
        args.append("CXX=" + self.spec["mpi"].mpicxx)
        args.append("FC=" + self.spec["mpi"].mpifc)
        args.append("F77=" + self.spec["mpi"].mpif77)

        #
        # PETSc, MUMPS, METIS, SCALAPACK, etc.
        # (Spack typically puts these in the compiler/link environment,
        #  but if the ISSM configure script looks for explicit --with-* 
        #  flags, we pass them.)
        #
        args.append("--with-petsc-dir={0}".format(self.spec["petsc"].prefix))
        args.append("--with-metis-dir={0}".format(self.spec["metis"].prefix))
        args.append("--with-mumps-dir={0}".format(self.spec["mumps"].prefix))
        # If you rely on sca/lapack from PETSc, these lines might 
        # not be strictly necessary. If ISSM's configure script 
        # checks them individually, add them:
        args.append("--with-scalapack-dir={0}".format(self.spec["scalapack"].prefix))

        # Some codes want the actual library subdir for m1qn3, 
        # e.g. "prefix.lib" or "prefix" depending on the configure logic:
        #
        args.append("--with-m1qn3-dir={0}".format(self.spec["m1qn3"].prefix.lib))
        

        # args.append("--with-python-version=3.9")
        # args.append("--with-python-dir=/apps/python3/3.9.2")
        # numpy_core_dir = "/apps/python3/3.9.2/lib/python3.9/site-packages/numpy-1.20.0-py3.9-linux-x86_64.egg/numpy"
        # args.append("--with-python-numpy-dir={0}".format(numpy_core_dir))
        
        # numpy_prefix = self.spec['py-numpy'].prefix
        # args.append('--with-python-numpy-dir={0}'.format(numpy_prefix))
        
        return args
    
    def build(self, spec, prefix):
        """Force serial build only if +wrappers is enabled."""
        if "+wrappers" in self.spec:
            old_parallel = self.parallel
            try:
                self.parallel = False  # force single job for 'make'
                super().build(spec, prefix)
            finally:
                self.parallel = old_parallel
        else:
            # Normal parallel build
            super().build(spec, prefix)

    def install(self, spec, prefix):
        # Run the normal Autotools install logic
        super().install(spec, prefix)

        # Copy only the examples directory directly into the prefix directory
        examples_src = join_path(self.stage.source_path, 'examples')
        examples_dst = join_path(prefix, 'examples')
        install_tree(examples_src, examples_dst)


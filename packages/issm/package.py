# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# Copyright 2023 Angus Gibson
# Justin Kin Jun Hew, 2025
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


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
    
    variant("examples", default=False,
            description="Build examples")
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

    flag_handler = build_system_flags

    def url_for_version(self, version):
        if version == Version("upstream"):
            return "https://github.com/ISSMteam/ISSM/archive/refs/heads/main.tar.gz"
        else:
            return "https://github.com/ACCESS-NRI/ISSM/archive/refs/heads/{0}.tar.gz".format(version)

    def autoreconf(self, spec, prefix):
        # If the repo has an Autotools build system, run autoreconf:
        autoreconf("--install", "--verbose", "--force")
        
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
        # PETSc, MUMPS, METIS, SCALAPACK, etc.
        # (Spack typically puts these in the compiler/link environment,
        #  but if the ISSM configure script looks for explicit --with-* 
        #  flags, we pass them.)
        #
        args.append("--with-petsc-dir={0}".format(self.spec["petsc"].prefix))
        args.append("--with-metis-dir={0}".format(self.spec["metis"].prefix))
        args.append("--with-mumps-dir={0}".format(self.spec["mumps"].prefix))
        args.append("--with-m1qn3-dir={0}".format(self.spec["m1qn3"].prefix.lib))
        #
        # MPI: Even if we use Spack's MPI wrappers, the build system may 
        # want explicit mention of MPI includes and compilers:
        #
        args.append("--with-mpi-include={0}".format(self.spec["mpi"].prefix.include))
        args.append("CC=" + self.spec["mpi"].mpicc)
        args.append("CXX=" + self.spec["mpi"].mpicxx)
        args.append("FC=" + self.spec["mpi"].mpifc)
        args.append("F77=" + self.spec["mpi"].mpif77)
        
        # If you rely on sca/lapack from PETSc, these lines might 
        # not be strictly necessary. If ISSM's configure script 
        # checks them individually, add them:
        args.append("--with-scalapack-dir={0}".format(self.spec["scalapack"].prefix))
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
            numpy_include_dir = join_path(numpy_prefix, 'lib', 'python{0}'.format(python_version), 'site-packages', 'numpy')
            args.append("--with-python-numpy-dir={0}".format(numpy_include_dir))
        else:
            args.append("--with-wrappers=no")

        
        return args
    
    def install(self, spec, prefix):
        # Run the normal Autotools install logic
        make("install", parallel=False)
        
        if "+examples" in self.spec:
            # Copy the examples directory directly into the prefix directory
            examples_src = join_path(self.stage.source_path, 'examples')
            examples_dst = join_path(prefix, 'examples')
            install_tree(examples_src, examples_dst)


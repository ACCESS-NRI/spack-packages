from spack.package import *


class Gcom(Package):
    """
    GCOM is a wrapper around multiprocessing libraries such as MPI
    """

    homepage = "https://code.metoffice.gov.uk/trac/gcom"
    svn = "file:///g/data/ki32/mosrs/gcom/main/trunk"

    maintainers = ["scottwales"]

    # See 'fcm kp fcm:gcom.xm' for release versions
    version("7.8", revision=1147)
    version("7.9", revision=1166)
    version("8.0", revision=1181)

    variant("mpi", default=True, description="Build with MPI")

    depends_on("fcm", type="build")
    depends_on("mpi", when="+mpi")

    def install(self, spec, prefix):
        fcm = which("fcm")

        # Set up variables used by fcm-make/gcom.cfg
        env["ACTION"] = "preprocess build"
        env["GCOM_SOURCE"] = "$HERE/.."
        env["DATE"] = ""
        env["REMOTE_ACTION"] = ""
        env["ROSE_TASK_MIRROR_TARGET"] = "localhost"

        # Decide on the build variant
        if spec.satisfies("%intel"):
            mach_c = "ifort"
        elif spec.satisfies("%gcc"):
            mach_c = "gfortran"
        else:
            raise NotImplentedError("Unknown compiler")
        if "+mpi" in spec:
            mach_m = "mpp"
        else:
            mach_m = "serial"

        env["GCOM_MACHINE"] = f"nci_gadi_{mach_c}_{mach_m}"

        # Do the build with fcm
        fcm("make", "-f", "fcm-make/gcom.cfg")

        # Install the library
        mkdirp(prefix.lib)
        install("build/lib/libgcom.a", prefix.lib + "/libgcom.a")
        install_tree("build/include", prefix.include)

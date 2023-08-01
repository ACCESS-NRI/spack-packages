from spack.package import *


class Fcm(Package):
    """
    FCM is a build system for Fortran programs
    """

    homepage = "https://github.com/metomi/fcm"

    maintainers = ["scottwales"]

    version(
        "2021.05.0",
        sha256="b4178b488470aa391f29b46d19bd6395ace42ea06cb9678cabbd4604b46f56cd",
    )

    def url_for_version(self, version):
        return "https://github.com/metomi/fcm/archive/refs/tags/{0}.tar.gz".format(version)

    def install(self, spec, prefix):
        install_tree(".", prefix)

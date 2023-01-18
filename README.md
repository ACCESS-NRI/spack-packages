# ACCESS-NRI Spack packages

This is a spack package repository maintained by ACCESS-NRI for packages that are not available by default in spack. Where possible packages developed will be contributed to the builtin spack supported packages. In some cases it is not possible to do this, for example software packages that we are not the copyright holders where it isn't appropriate to distribute a package that only supports ACCESS-NRI build use-cases.

The namespace of the pacakge repository is access.nri

## How to utilise this package repository

By default you have a single package repository (`builtin`) when you clone spack
```bash
$ spack repo list
==> 1 package repository.
builtin    $SPACK_ROOT/var/spack/repos/builtin
```
(note `$SPACK_ROOT` is substituted in all paths to make the description installation independent)

And the package is not available:
```
$ spack list oasis3_mct
==> 0 packages
```

To use the packages in this repository first clone the repo to a path of your choosing (represented here as `$PACKAGE_PATH`)
```
git clone git@github.com:ACCESS-NRI/spack_packages.git $PACKAGE_PATH/spack_packages
```
and then add the location of the repository to your spack instance
```
git repo add $PACKAGE_PATH/spack_packages
```
and then confirm it is has been added correctly:
```
$ spack repo list
==> 2 package repositories.
access.nri    $PACKAGE_PATH/spack_packages
builtin       $SPACK_ROOT/var/spack/repos/builtin
```
Now the `oasis3-mct` package should be available to install
```
$ spack list oasis3-mct
oasis3-mct
==> 1 packages
```

## More information

For more information see the extensive [spack documentation](https://spack.readthedocs.io/en/latest/repositories.html) on how to utilise repository files. 

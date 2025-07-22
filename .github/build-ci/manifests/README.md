# `spack-packages` Build CI Manifests

## Overview

This folder contains both a very simple default manifest `template.spack.yaml.j2`, and any number of package-specific `PACKAGE/*spack.yaml.j2` files.

These files are used to test various configurations of packages defined in this repository. When a package/packages are modified in a PR or through a `workflow_dispatch` event, the `ci.yml` workflow collects the package-specific manifest files, or `template.spack.yaml.j2` with the package name templated in, and attempts installation.

## Example File Structure

```txt
.github/
└── build-ci/
    └── manifests/
        ├── template.spack.yaml.j2
        ├── mom5/
        │   ├── intel.spack.yaml.j2
        │   └── amd.spack.yaml.j2
        └── cice5/
            └── spack.yaml.j2
```

For example, say that a PR modifies `mom5` and `oasis3-mct`. For `mom5`, the CI will find all manifests within the `.github/build-ci/manifests/mom5` folder. For `oasis3-mct`, the CI will find no specific manifests, and will therefore use `.github/build-ci/manifests/template.spack.yaml.j2`, with the `{{ package }}` section filled in with `oasis3-mct`. It will attempt to install those manifests via spack, and will report on failures.

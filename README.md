# fedora-blueprints

In a [change request for Fedora 39](https://fedoraproject.org/wiki/Changes/FedoraWorkstationImageBuilder) [osbuild-composer](https://github.com/osbuild/osbuild-composer) was considered to build the Fedora Workstation ISO artifacts. The outcome was that `osbuild-composer` needs to provide a way for edition and spin maintainers to define those. We plan to have a new change request for Fedora 40 where we can build a subset of spins and show how other spins and editions could be built as well. We plan to use the time in between those releases to verify the compatibility of the produced artifacts with lorax and livemediacreator.

This is an **experimental** repository to try how Fedora Editions and Spins could be defined in `osbuild-composer`'s blueprint format and what problems need to be solved to make this feasible. All these blueprints are still in development and might not yield the same artifacts as current kickstart setups.

## Usage

Install the Packit-built RPMs for the [following PR](x):

```
copr enable ...
dnf install osbuild-composer composer-cli
```

Build the blueprints you want:

```
composer-cli blueprints push blueprints/*
composer-cli compose start blueprint iso-live
```

## Issues

- [ ] the dnf state database needs to be populated after installation of packages
- [ ] `sysconfig/livesys` and `sysconfig/desktop` should be configured through a customizations -> https://github.com/osbuild/fedora-blueprints/issues/4
- [ ] `kde-live.toml` blueprint can't be processed as it needs to create a directory disallowed by policy -> https://github.com/osbuild/fedora-blueprints/issues/2
- [ ] packages can't be excluded from comps -> https://github.com/osbuild/fedora-blueprints/issues/6

## Format

Generally the blueprints (found in [blueprints/](blueprints/)) are much shorter than their kickstart counterparts. That is because in `osbuild-composer` a lot of work is handled by the `image type`. It's also notable that package lists [have no excludes](https://github.com/osbuild/osbuild-composer/issues/3535) and there is [no inheritance](https://github.com/osbuild/osbuild-composer/issues/3537). Both these subjects are still under discussion for inclusion in `osbuild-composer`.

## Extras

This repository comes with a bunch of extras to make figuring out the kickstarts, their includes, the package sets, and other things a bit easier for myself. You can find these scripts in `scripts/`.

### A graph of kickstart includes

`scripts/ksu.py` offers a way to generate graphviz `.dot` files of the kickstarts and their includes:

```
€ scripts/ksu.py graph external/fedora-kickstarts > figures/kickstart-graph.dot 
€ dot -Ksfdp -Tpng -Goverlap=false figures/kickstart-graph.dot > figures/kickstart-graph.png

# Optional
€ xdg-open figures/kickstart-graph.png
```

The resulting image looks like:

![Graph of Kickstart includes](figures/kickstart-graph.png)

### What actually is the base package set for all the kickstarts?

`scripts/ksu.py` offers a way to generate the shared package set across all kickstarts, or starting from a single root kickstart. Here is it's output:


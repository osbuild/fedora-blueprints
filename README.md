# fedora-blueprints

This is an **experimental** repository to try how Fedora Editions and Spins could be defined in [osbuild-composer](https://github.com/osbuild/osbuild-composer)'s blueprint format and what problems need to be solved to make this feasible.

## Extras

This repository comes with a bunch of extras to make figuring out the kickstarts, their includes, the package sets, and other things a bit easier for myself. You can find these scripts in `bin/`.

### Graph Kickstart includes

`bin/ksu.py` offers a way to generate graphviz `.dot` files of the kickstarts and their includes:

```
€ bin/ksu.py graph ext/fedora-kickstarts > img/kickstart-graph.dot 
€ dot -Ksfdp -Tpng -Goverlap=false img/kickstart-graph.dot > img/kickstart-graph.png

# Optional
€ xdg-open img/kickstart-graph.png
```

The resulting image looks like:

![Graph of Kickstart includes](img/kickstart-graph.png)

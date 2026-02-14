# Custom Krew Plugin Index for kubectl-assess

This repository provides a custom Krew plugin index for the `kubectl-assess` plugin.

## Directory Structure

```
plugins/
  assess.yaml
```

## Usage

=```sh

# Add this custom index to your Krew installation:
kubectl krew index add custom-assess-index <REPO-URL>

# install the plugin
kubectl krew install custom-assess-index/assess
```

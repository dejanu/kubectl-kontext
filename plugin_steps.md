# Custom Krew Plugin Index for kubectl-assess

This repository provides a custom Krew plugin index for the `kubectl-assess` plugin.

## Directory Structure

```
plugins/
  assess.yaml
```

## Usage

```sh
# Used plugin locally
sudo cp kubectl-assess /usr/local/bin/
export PATH="$PATH:$(pwd)"  

# Add this custom index to your Krew installation:
kubectl krew index add custom-assess-index https://github.com/dejanu/k8s_assess/blob/main/plugins/assess.yaml

# install the plugin
kubectl krew install custom-assess-index/assess
```

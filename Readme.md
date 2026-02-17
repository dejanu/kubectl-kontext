# kubectl-kontext

Kubernetes cluster assessment plugin optimized for AI analysis. 
 **Summary-first** design, which matches how AI models process information most effectively.

How it works (3 phases):                                                                                                                                                                                                              
  1. Fetch heavy JSON data in parallel (pods, nodes, events) from the cluster
  2. Run ~15 independent lightweight kubectl calls concurrently
  3. Assemble the summary sequentially from cached data using jq


| Section | Purpose |
|---------|---------|
| Quick Summary | Key metrics for AI |
| Nodes | Count, resources, capacity |
| Resource Allocation | CPU/memory per node (overcommitment %) |
| Pods Without Limits/Requests | Resource governance gaps |
| Top Memory Consumers | Heavy workloads |
| Top Pod Restarts | Stability issues |
| Warning Events | Active problems |
| PDBs/LimitRanges/Quotas | Resource policies |
| Network Policies | Security posture |
| Node Taints | Scheduling controls |

## Install

```bash
# Place kubectl-kontext in your path
export PATH="$PATH:$(pwd)" # or cp kubectl-kontext /usr/local/bin/

# Install kubectl-kontext from index
kubectl krew index add my-index https://github.com/dejanu/kubectl-kontext.git

kubectl krew search my-index

kubectl krew install my-index/kontext
```

## Usage: leveraging unix composition

* Claude code in headless mode

```bash
# copy to Clipboard 
kubectl kontext | pbcopy 

# Quick assessment
kubectl kontext | claude --model sonnet -p 'List critical issues and recommendations'

kubectl kontext | claude -p 'Analyze this cluster. Prioritize issues by severity (critical/high/medium/low). For each issue provide: problem, impact, fix.' | tee analysis.md

# K3s evaluation
kubectl kontext | claude --model sonnet -p 'Based on this report, is K8S suitable alternative for this K3S cluster? Consider: node count, workload complexity, HA requirements.'

# Quick health check (fast/cheap)
kubectl kontext | claude --model haiku -p 'One paragraph: Is this cluster healthy? Top 3 concerns if any.'

```

* Ollama locally (with desire [model](https://ollama.com/library?sort=popular))

```bash
# start ollama locally as docker container with phi3
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec ollama ollama run phi3

kubectl kontext | docker exec -i ollama ollama run phi3 "Analyze this Kubernetes cluster report"
```
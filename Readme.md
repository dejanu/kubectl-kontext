# kubectl-kontext

Kubernetes cluster assessment plugin optimized for AI analysis. 
 Summary-first design, which matches how AI models process information most effectively.

How it works (3 phases):                                                                                                                                                                                                              
  1. Fetch heavy JSON data in parallel (pods, nodes, events) from the cluster
  2. Run ~15 independent lightweight kubectl calls concurrently
  3. Assemble the report sequentially from cached data using jq


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
# local cp kubectl-kontext /usr/local/bin/
export PATH="$PATH:$(pwd)" 

kubectl krew index add my-index https://github.com/dejanu/kubectl-kontext.git

kubectl krew search my-index

kubectl krew install my-index/kontext
```

## Usage

* For unix composition with claude code in headless mode

```bash
kubectl kontext | pbcopy 

# Quick assessment
kubectl kontext | claude --model sonnet -p 'List critical issues and recommendations'

kubectl kontext | claude clear -p 'Analyze this cluster. Prioritize issues by severity (critical/high/medium/low). For each issue provide: problem, impact, fix.' | tee analysis.md

# K3s evaluation
kubectl kontext | claude --model sonnet -p 'Based on this report, is K3s suitable or should this be vanilla K8s? Consider: node count, workload complexity, HA requirements.'

# Quick health check (fast/cheap)
kubectl kontext | claude --model haiku -p 'One paragraph: Is this cluster healthy? Top 3 concerns if any.'

```
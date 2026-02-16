# kubectl-assess

Kubernetes cluster assessment plugin optimized for AI analysis.
 summary → metrics → details, which matches how AI models process information most effectively.

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
# local cp kubectl-assess /usr/local/bin/
export PATH="$PATH:$(pwd)" 

kubectl krew index add alex-index https://github.com/dejanu/k8s_assess.git

kubectl krew search alex-index

kubectl krew install alex-index/assess
```

## Usage

* For unix composition with claude code in headless mode

```bash
kubectl assess | pbcopy 

# Quick assessment
kubectl assess | claude --model sonnet -p 'List critical issues and recommendations'

kubectl assess | claude clear -p 'Analyze this cluster. Prioritize issues by severity (critical/high/medium/low). For each issue provide: problem, impact, fix.' | tee analysis.md

# K3s evaluation
kubectl assess | claude --model sonnet -p 'Based on this report, is K3s suitable or should this be vanilla K8s? Consider: node count, workload complexity, HA requirements.'

# Quick health check (fast/cheap)
kubectl assess | claude --model haiku -p 'One paragraph: Is this cluster healthy? Top 3 concerns if any.'

```
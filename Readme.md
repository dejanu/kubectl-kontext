# kubectl-assess

Kubernetes cluster assessment plugin optimized for AI analysis.
 summary → metrics → details, which matches how AI models process information most effectively.

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
kubectl krew index add custom-assess-index https://github.com/dejanu/k8s_assess/blob/main/plugins/assess.yaml

kubectl krew install custom-assess-index/assess
```

## Usage

* For unix composition with claude code in headless mode

```bash
# Quick assessment
kubectl assess | claude --model sonnet -p 'Analyze this cluster for. Prioritize issues by severity (critical/high/medium/low). For each issue provide: problem, impact, fix.' | tee analysis.md

# K3s evaluation
kubectl assess | claude --model sonnet -p 'Based on this report, is K3s suitable or should this be vanilla K8s? Consider: node count, workload complexity, HA requirements.'

# Quick health check (fast/cheap)
kubectl assess | claude --model haiku -p 'One paragraph: Is this cluster healthy? Top 3 concerns if any.'


#Built-in analysis modes (require claude CLI):
kubectl assess --analyze              # Comprehensive cluster analysis
kubectl assess --health               # Quick health check
kubectl assess --security             # Security-focused review
kubectl assess --capacity             # Capacity planning focus
```
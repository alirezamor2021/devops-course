# KubernetesSubmissions

NB: Docker images version is like {CHAPTER}.{EXERCISE_NUMBER}.0

## Exercises

### Chapter 2

- [1.1.](https://github.com/alirezamor2021/devops-course/tree/1.1)
- [1.2.](https://github.com/alirezamor2021/devops-course/tree/1.2)
- [1.3.](https://github.com/alirezamor2021/devops-course/tree/1.3)
- [1.4.](https://github.com/alirezamor2021/devops-course/tree/1.4)
- [1.5.](https://github.com/alirezamor2021/devops-course/tree/1.5)
- [1.6.](https://github.com/alirezamor2021/devops-course/tree/1.6)
- [1.7.](https://github.com/alirezamor2021/devops-course/tree/1.7)
- [1.8.](https://github.com/alirezamor2021/devops-course/tree/1.8)
- [1.9.](https://github.com/alirezamor2021/devops-course/tree/1.9)
- [1.10.](https://github.com/alirezamor2021/devops-course/tree/1.10)
- [1.11.](https://github.com/alirezamor2021/devops-course/tree/1.11)
- [1.12.](https://github.com/alirezamor2021/devops-course/tree/1.12)
- [1.13.](https://github.com/alirezamor2021/devops-course/tree/1.13)


### Chapter 3
- [2.1](https://github.com/alirezamor2021/devops-course/tree/2.1)
- [2.2](https://github.com/alirezamor2021/devops-course/tree/2.2)
- [2.3](https://github.com/alirezamor2021/devops-course/tree/2.3)
- [2.4](https://github.com/alirezamor2021/devops-course/tree/2.4)
- [2.5](https://github.com/alirezamor2021/devops-course/tree/2.5)
- [2.6](https://github.com/alirezamor2021/devops-course/tree/2.6)
- [2.7](https://github.com/alirezamor2021/devops-course/tree/2.7)
- [2.8](https://github.com/alirezamor2021/devops-course/tree/2.8)
- [2.9](https://github.com/alirezamor2021/devops-course/tree/2.9)
- [2.10](https://github.com/alirezamor2021/devops-course/tree/2.10)

### Chapter 4
- [3.1](https://github.com/alirezamor2021/devops-course/tree/3.1)
- [3.2](https://github.com/alirezamor2021/devops-course/tree/3.2)
- [3.3](https://github.com/alirezamor2021/devops-course/tree/3.3)
- [3.4](https://github.com/alirezamor2021/devops-course/tree/3.4)
- [3.5](https://github.com/alirezamor2021/devops-course/tree/3.5)
- [3.6](https://github.com/alirezamor2021/devops-course/tree/3.6)
- [3.7](https://github.com/alirezamor2021/devops-course/tree/3.7)
- [3.8](https://github.com/alirezamor2021/devops-course/tree/3.8)
- [3.9](https://github.com/alirezamor2021/devops-course/tree/3.9)

# DBaaS vs. Self-Managed (DIY) Database

## Summary

| Aspect | DBaaS | DIY (self-managed) |
|---|---|---|
| Initial setup effort | Low (minutes to hours) | High (days: install, harden, tune, monitor) |
| Infrastructure cost | Higher (managed premium) | Lower (raw VM and storage) |
| Operational cost (people/time) | Low | High (patching, on-call, upgrades) |
| Maintenance | Provider handles patches and minor upgrades | Fully your responsibility |
| Backups | Built in (snapshots and PITR) | Must be built, scheduled and monitored |
| Restore ease | Simple, often one click or API call | Manual process, needs scripts and testing |
| High availability | Often one click | Complex (replication, failover, fencing) |
| Flexibility / control | Limited (extensions, configs, OS access) | Full control |
| Vendor lock-in | Medium to high | Low |

## DBaaS

### Pros
- **Fast, low-effort initialization:** a production-ready instance with networking, encryption and monitoring in minutes, or as a few lines of infrastructure-as-code.
- **Minimal maintenance:** the provider handles OS and engine patching, and minor (optionally major) version upgrades can be automated.
- **Easy, reliable backups:** automated snapshots and point-in-time recovery (PITR) are built in, and restoring is a console or API operation.
- **Simple high availability:** multi-AZ replicas and automatic failover can be enabled with one setting.
- **Lower operational burden:** the team can focus on the application instead of database administration.

### Cons
- **Higher direct cost:** a premium over raw compute, plus extra charges for backup retention, PITR storage, replicas and cross-region copies.
- **Vendor lock-in:** provider-specific features and tooling make migration to another provider or on-premises harder.
- **Less control:** restricted access to the OS, some configuration parameters and certain extensions.
- **Costs can grow unpredictably** with storage, IOPS and traffic.

## DIY

### Pros
- **Lower infrastructure cost:** you pay only for VMs and storage, which can be significantly cheaper at scale or on predictable workloads.
- **Full control:** any engine version, extension, configuration and OS-level tuning.
- **Portability:** no lock-in, so it is easy to move between providers or on-premises.
- **Custom backup strategy:** any tool (e.g. pgBackRest, Barman, xtrabackup), schedule, retention and storage target.

### Cons
- **High initialization effort:** provisioning, installing, hardening, TLS, user management, tuning and monitoring all have to be set up before production use.
- **Ongoing maintenance:** OS and engine patching, major upgrades, disk management and capacity planning are the team's responsibility.
- **Backups are your job:** you need scripts or tooling for automation, storage for the backups, monitoring for failures and regular restore tests. An untested backup is not a backup.
- **Harder restores:** PITR requires WAL/binlog archiving and a documented, rehearsed procedure.
- **HA is complex and resource-hungry:** replication, failover orchestration (e.g. Patroni), extra nodes and split-brain handling.
- **Hidden cost in engineer time** and on-call burden, which can outweigh the infrastructure savings.

## Conclusion

DBaaS is the better default for small teams or teams without dedicated DBA/DevOps capacity: higher monthly cost, but much lower setup, maintenance and backup risk. DIY makes sense when costs at scale dominate, when custom engine features or full control are required, or when avoiding vendor lock-in is a priority, provided the team can operate it reliably.

- [3.10](https://github.com/alirezamor2021/devops-course/tree/3.10)
- [3.11](https://github.com/alirezamor2021/devops-course/tree/3.11)
- [3.12](https://github.com/alirezamor2021/devops-course/tree/3.12) [GKE logs for the project](the_project/LOGGING.md)


### Chapter 5
- [4.1](https://github.com/alirezamor2021/devops-course/tree/4.1)
- [4.2](https://github.com/alirezamor2021/devops-course/tree/4.2)
- [4.3](https://github.com/alirezamor2021/devops-course/tree/4.3) [Monitoring with Helm](infrastructure/monitoring/README.md)
- [4.4](https://github.com/alirezamor2021/devops-course/tree/4.4) [Argo Rollouts CPU analysis](infrastructure/argo-rollouts/README.md)

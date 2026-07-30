# Pilot extraction performance

Documentation-only summary of pilot registry extraction profiling.

## Cohort interpretation
> This 100-repository cohort is an enriched engineering cohort, not a population sample. Adoption rates must not be interpreted as GitHub-wide prevalence.

## Registry accounting
- Attempted repositories: **100**
- Profile accounting mode: **latest-per-repo**
- Profile rows used in summary: **100**

## Summary

- Profiled repositories: **100**
- Total execution time (sum of per-repo totals): **4435.4 s**
- Median extraction time: **11.2 s**
- Mean extraction time: **44.4 s**
- Successful extractions: **98**
- Skipped repositories: **0**
- Failed repositories: **2**
- Slow-repo threshold: **300 s**

- Missing profile rows: **0**

## Slowest repositories

| Rank | Repository | Total | Clone | Inspection | History | Detector | Blobs | Status |
|------|------------|-------|-------|------------|---------|----------|-------|--------|
| 1 | activeinferenceinstitute/geo-infer | 600.0 s | 1.4 s | 0.0 s | 63.8 s | 0.1 s | 534.4 s | failed |
| 2 | microsoft/vscode | 450.0 s | 13.3 s | 0.0 s | 334.8 s | 0.3 s | 101.5 s | ok |
| 3 | louisshark/chatgpt_system_prompt | 275.4 s | 0.9 s | 0.0 s | 228.9 s | 0.0 s | 45.6 s | ok |
| 4 | azure/azure-sdk-for-python | 206.8 s | 6.1 s | 0.0 s | 136.1 s | 0.8 s | 63.8 s | ok |
| 5 | automattic/wp-calypso | 194.6 s | 7.8 s | 0.0 s | 132.1 s | 0.2 s | 54.5 s | ok |
| 6 | alt-f4-llc/dotfiles.vorpal | 181.8 s | 1.1 s | 0.0 s | 38.4 s | 0.0 s | 142.3 s | ok |
| 7 | jmberesford/retrom | 168.9 s | 0.8 s | 0.0 s | 167.3 s | 0.0 s | 0.7 s | ok |
| 8 | provenance-emu/provenance | 153.7 s | 2.8 s | 0.0 s | 127.4 s | 0.4 s | 23.1 s | ok |
| 9 | prefecthq/prefect | 145.7 s | 4.5 s | 0.0 s | 51.7 s | 0.0 s | 89.4 s | ok |
| 10 | agents2agentsai/ata | 139.8 s | 1.7 s | 0.0 s | 86.2 s | 0.0 s | 51.8 s | ok |

## Slowest phases (aggregate)

- **history**: 2328.9 s (52.5% of attributed phase time)
- **blobs**: 1868.9 s (42.1% of attributed phase time)
- **clone**: 230.8 s (5.2% of attributed phase time)
- **detector**: 5.0 s (0.1% of attributed phase time)
- **cleanup**: 0.8 s (0.0% of attributed phase time)
- **inspection**: 0.5 s (0.0% of attributed phase time)
- **parquet_write**: 0.0 s (0.0% of attributed phase time)
- **manifest_write**: 0.0 s (0.0% of attributed phase time)

## Clone sizes

- Median clone size: **1.9 MB**
- Mean clone size: **30.0 MB**
- Largest clone: **1247.3 MB**

| Repository | Clone size |
|------------|------------|
| jetbrains/intellij-community | 1247.3 MB |
| microsoft/vscode | 321.2 MB |
| checkmk/checkmk | 238.7 MB |
| automattic/wp-calypso | 162.3 MB |
| vercel/next.js | 107.7 MB |
| azure/azure-sdk-for-python | 93.3 MB |
| dagster-io/dagster | 87.1 MB |
| django/django | 69.5 MB |
| insightsoftwareconsortium/itk | 63.5 MB |
| langgenius/dify | 53.9 MB |
| browseroperator/browser-operator-core | 43.0 MB |
| prefecthq/prefect | 42.3 MB |
| astral-sh/ruff | 41.5 MB |
| langchain-ai/langchain | 40.6 MB |
| agoric/agoric-sdk | 39.0 MB |
| copilotkit/copilotkit | 26.3 MB |
| all-hands-ai/openhands | 26.1 MB |
| continuedev/continue | 23.3 MB |
| datadog/dd-trace-js | 23.3 MB |
| automattic/newspack-workspace | 20.3 MB |
| open-webui/open-webui | 19.5 MB |
| azure/azure-sdk-tools | 17.3 MB |
| agents2agentsai/ata | 17.2 MB |
| provenance-emu/provenance | 16.0 MB |
| crewaiinc/crewai | 10.0 MB |
| pbh-btn/peerbanhelper | 9.4 MB |
| tiangolo/fastapi | 8.2 MB |
| falconchristmas/fpp | 8.1 MB |
| azuread/microsoft-authentication-library-common-for-objc | 7.8 MB |
| modelengine-group/nexent | 6.8 MB |
| aider-ai/aider | 6.7 MB |
| agentwrapper/agent-orchestrator | 6.7 MB |
| fixmyberlin/tilda-geo | 6.4 MB |
| pydantic/pydantic-ai | 6.2 MB |
| prefecthq/fastmcp | 5.2 MB |
| 1jehuang/jcode | 4.9 MB |
| myriad-dreamin/tinymist | 4.6 MB |
| modelcontextprotocol/servers | 3.8 MB |
| googlecloudplatform/vertex-ai-creative-studio | 3.7 MB |
| nvidia/physicsnemo | 3.1 MB |
| alfanous-team/alfanous | 2.9 MB |
| googlecloudplatform/kubernetes-engine-samples | 2.5 MB |
| communitytoolkit/aspire | 2.5 MB |
| agentops-ai/agentops | 2.4 MB |
| agent-threat-rule/agent-threat-rules | 2.3 MB |
| 567-labs/instructor | 2.2 MB |
| jmberesford/retrom | 2.0 MB |
| activeinferenceinstitute/geo-infer | 2.0 MB |
| paloaltonetworks/docusaurus-openapi-docs | 2.0 MB |
| azure/oav | 1.9 MB |
| case211/remnawave-admin | 1.8 MB |
| b-m-capital-research/honeclaw | 1.8 MB |
| 0niel/university-app | 1.7 MB |
| goldenpotato137/potatovn | 1.7 MB |
| flagai-open/flagai | 1.6 MB |
| avarok-cybersecurity/atlas | 1.5 MB |
| owasp/www-project-top-10-for-large-language-model-applications | 1.4 MB |
| datadog/stratus-red-team | 1.4 MB |
| flarecoding/stelluxos | 1.3 MB |
| 0-ai-ug/cate | 1.2 MB |
| 3mfconsortium/gladius | 1.2 MB |
| bnetdocs/bnetdocs-web | 1.2 MB |
| emilstenstrom/justhtml | 1.1 MB |
| louisshark/chatgpt_system_prompt | 1.1 MB |
| memorilabs/memori | 0.9 MB |
| factory-ai/factory | 0.9 MB |
| alphabitcore/nexus-gateway | 0.9 MB |
| hbai-ltd/toonflow-app | 0.9 MB |
| azure-samples/art-voice-agent-accelerator | 0.9 MB |
| bitterbot-ai/bitterbot-desktop | 0.8 MB |
| alt-f4-llc/dotfiles.vorpal | 0.7 MB |
| agiflow/aicode-toolkit | 0.7 MB |
| ardentailabs/de-bench | 0.7 MB |
| anthropics/claude-code | 0.6 MB |
| hkuds/openharness | 0.5 MB |
| newlifex/newlife.redis | 0.5 MB |
| kuberocketci/kuberocketai | 0.5 MB |
| ayayaxiaowang/ayaya_miliastra_editor | 0.4 MB |
| airjen/onebuttonprompt | 0.4 MB |
| ai-planning/l2p | 0.4 MB |
| 9mtm/agent-player | 0.4 MB |
| amap-eai/nav-r2 | 0.4 MB |
| antvirf/stui | 0.3 MB |
| angelmunoz/kipo | 0.3 MB |
| damianb-bitflipper/proton-drive-sync | 0.3 MB |
| eliasoenal/multimon-ng | 0.3 MB |
| prismer-ai/prismer | 0.3 MB |
| houseofmvps/codesight | 0.2 MB |
| creminiai/skillpack | 0.2 MB |
| 1amageek/swiftagent | 0.2 MB |
| agnuxo1/openclaw-p2p | 0.2 MB |
| affitor/affiliate-skills | 0.1 MB |
| ai-escape/open-ice | 0.1 MB |
| azure/kimojio-rs | 0.1 MB |
| 0xn0rmxl/bugbountyskills | 0.1 MB |
| 0xdpfly/gin-app-start | 0.1 MB |
| 26d0/vrchat-ime-chat | 0.1 MB |
| 2030ai/2030ai-claudecode-allecosystem-sync | 0.0 MB |
| ageniti/ageniti | 0.0 MB |
| 1password/scam | 0.0 MB |

## Repositories skipped

None.

## Repositories failed

- **activeinferenceinstitute/geo-infer**: total=600.0 s; timeout_phase=history; slowest phase=timeout:history (63.8 s); failure_reason=timeout:history
- **jetbrains/intellij-community**: total=55.1 s; timeout_phase=n/a; slowest phase=clone (55.0 s); failure_reason=CloneTooLargeError: clone size 1247256628 exceeds limit 500000000

## Recommendations

- History traversal dominates aggregate time: quantify `git log --follow` calls per matched path before changing traversal strategy.
- Clone size is heavy-tailed (max 1247.3 MB): mark oversized repos in the registry before scaling beyond the pilot.
- 2 repositories failed or timed out: inspect receipts and phase timings before re-running.
- Measure first, optimize second — do not change detectors or infrastructure until variance is understood.

## Regeneration

```bash
make e1-pilot   # development
make e1         # full pilot
make paper      # copy exports to ../paper/
```

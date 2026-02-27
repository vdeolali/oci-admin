# OCI DevOps Agent

A Claude AI-powered agent for managing Oracle Cloud Infrastructure (OCI) tenancies through natural language.

## Overview

- **Model**: `claude-sonnet-4-6` (configurable via `MODEL` env var)
- **Auth**: OCI config file (`~/.oci/config`), profile `CVM` by default
- **SDK**: `claude_agent_sdk` v0.1.44 with in-process MCP tool server

## Usage

```bash
# Basic query using default CVM profile
python main.py -q "List all compartments in my tenancy"

# Override OCI profile at runtime
python main.py --profile DEFAULT -q "List all VCNs in compartment ocid1.compartment..."

# List running compute instances
python main.py -q "Show me all running instances in compartment ocid1.compartment.oc1..xxx"

# Check object storage
python main.py -q "List all buckets in compartment ocid1.compartment.oc1..xxx"
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `OCI_PROFILE` | `CVM` | OCI config profile to use |
| `OCI_CONFIG_PATH` | `~/.oci/config` | Path to OCI config file |
| `ANTHROPIC_API_KEY` | _(required)_ | Anthropic API key |
| `MODEL` | `claude-sonnet-4-6` | Claude model ID |

## Tools (14 total)

### Compute (`oci.core.ComputeClient`)
| Tool | Description |
|------|-------------|
| `list_instances` | List VM instances with state and shape |
| `get_instance` | Get details for a single instance by OCID |
| `start_instance` | Send START action to a stopped instance |
| `stop_instance` | Send SOFTSTOP action to a running instance |

### Networking (`oci.core.VirtualNetworkClient`)
| Tool | Description |
|------|-------------|
| `list_vcns` | List VCNs with CIDR blocks |
| `list_subnets` | List subnets, optionally filtered by VCN |
| `list_security_lists` | List security lists with rule counts |

### Storage
| Tool | Description |
|------|-------------|
| `list_buckets` | List Object Storage buckets |
| `get_bucket` | Get metadata for a specific bucket |
| `list_objects` | List objects within a bucket |
| `list_block_volumes` | List Block Storage volumes with size/state |

### Identity/IAM (`oci.identity.IdentityClient`)
| Tool | Description |
|------|-------------|
| `list_compartments` | List all compartments (recursive) |
| `list_users` | List IAM users with state |
| `list_groups` | List IAM groups |
| `list_policies` | List IAM policies in a compartment |

## Architecture

```
main.py                        CLI entry point (click)
  └── src/oci_agent/
        ├── config.py          Pydantic settings (env / .env)
        ├── auth.py            OCIAuth — OCI client factory
        ├── agent.py           OCIAgent — MCP server + claude_agent_sdk query loop
        └── tools/
              ├── compute.py   4 compute tools
              ├── network.py   3 networking tools
              ├── storage.py   4 storage tools
              └── identity.py  4 IAM tools
```

## Safety

State-changing operations (`start_instance`, `stop_instance`) are included in the tool set.
The system prompt instructs Claude to always confirm before executing them. For
programmatic use where safety confirmation is not needed, pass `--profile` explicitly
and include confirmation language in your query.

## Running Tests

```bash
cd /home/vdeolali/claude
uv run pytest tests/ -v
```

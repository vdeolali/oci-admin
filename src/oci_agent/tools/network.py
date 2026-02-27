"""Networking tools — VCNs, Subnets, Security Lists."""

import json

from claude_agent_sdk import SdkMcpTool, tool

from ..auth import OCIAuth


@tool(
    name="list_vcns",
    description="List Virtual Cloud Networks (VCNs) in a compartment with their CIDR blocks.",
    input_schema={
        "type": "object",
        "properties": {
            "compartment_id": {"type": "string", "description": "OCID of the compartment"},
        },
        "required": ["compartment_id"],
    },
)
async def list_vcns(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.virtual_network_client()
    response = client.list_vcns(compartment_id=args["compartment_id"])
    vcns = [
        {
            "id": v.id,
            "display_name": v.display_name,
            "cidr_block": v.cidr_block,
            "lifecycle_state": v.lifecycle_state,
            "dns_label": v.dns_label,
            "time_created": str(v.time_created),
        }
        for v in response.data
    ]
    return {"content": [{"type": "text", "text": json.dumps(vcns, indent=2)}]}


@tool(
    name="list_subnets",
    description="List subnets in a compartment, optionally filtered by VCN.",
    input_schema={
        "type": "object",
        "properties": {
            "compartment_id": {"type": "string", "description": "OCID of the compartment"},
            "vcn_id": {"type": "string", "description": "OCID of the VCN to filter by (optional)"},
        },
        "required": ["compartment_id"],
    },
)
async def list_subnets(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.virtual_network_client()
    kwargs: dict = {"compartment_id": args["compartment_id"]}
    if args.get("vcn_id"):
        kwargs["vcn_id"] = args["vcn_id"]
    response = client.list_subnets(**kwargs)
    subnets = [
        {
            "id": s.id,
            "display_name": s.display_name,
            "cidr_block": s.cidr_block,
            "vcn_id": s.vcn_id,
            "availability_domain": s.availability_domain,
            "lifecycle_state": s.lifecycle_state,
            "dns_label": s.dns_label,
        }
        for s in response.data
    ]
    return {"content": [{"type": "text", "text": json.dumps(subnets, indent=2)}]}


@tool(
    name="list_security_lists",
    description="List security lists in a compartment with their ingress and egress rules.",
    input_schema={
        "type": "object",
        "properties": {
            "compartment_id": {"type": "string", "description": "OCID of the compartment"},
            "vcn_id": {"type": "string", "description": "OCID of the VCN to filter by (optional)"},
        },
        "required": ["compartment_id"],
    },
)
async def list_security_lists(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.virtual_network_client()
    kwargs: dict = {"compartment_id": args["compartment_id"]}
    if args.get("vcn_id"):
        kwargs["vcn_id"] = args["vcn_id"]
    response = client.list_security_lists(**kwargs)
    sls = [
        {
            "id": sl.id,
            "display_name": sl.display_name,
            "lifecycle_state": sl.lifecycle_state,
            "vcn_id": sl.vcn_id,
            "egress_security_rules_count": len(sl.egress_security_rules),
            "ingress_security_rules_count": len(sl.ingress_security_rules),
        }
        for sl in response.data
    ]
    return {"content": [{"type": "text", "text": json.dumps(sls, indent=2)}]}


ALL_TOOLS: list[SdkMcpTool] = [list_vcns, list_subnets, list_security_lists]

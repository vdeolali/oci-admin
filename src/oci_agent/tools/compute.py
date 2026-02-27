"""Compute tools — OCI Compute instances."""

import json

from claude_agent_sdk import SdkMcpTool, tool

from ..auth import OCIAuth


def _make_instance_dict(inst) -> dict:
    return {
        "id": inst.id,
        "display_name": inst.display_name,
        "lifecycle_state": inst.lifecycle_state,
        "shape": inst.shape,
        "compartment_id": inst.compartment_id,
        "region": inst.region,
        "availability_domain": inst.availability_domain,
        "time_created": str(inst.time_created),
    }


@tool(
    name="list_instances",
    description="List compute instances in a compartment with their state and shape.",
    input_schema={
        "type": "object",
        "properties": {
            "compartment_id": {"type": "string", "description": "OCID of the compartment"},
            "limit": {"type": "integer", "description": "Max instances to return (default 20)"},
        },
        "required": ["compartment_id"],
    },
)
async def list_instances(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.compute_client()
    limit = int(args.get("limit", 20))
    response = client.list_instances(
        compartment_id=args["compartment_id"],
        limit=limit,
    )
    instances = [_make_instance_dict(i) for i in response.data]
    return {"content": [{"type": "text", "text": json.dumps(instances, indent=2)}]}


@tool(
    name="get_instance",
    description="Get details for a specific compute instance by OCID.",
    input_schema={
        "type": "object",
        "properties": {
            "instance_id": {"type": "string", "description": "OCID of the instance"},
        },
        "required": ["instance_id"],
    },
)
async def get_instance(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.compute_client()
    response = client.get_instance(instance_id=args["instance_id"])
    return {"content": [{"type": "text", "text": json.dumps(_make_instance_dict(response.data), indent=2)}]}


@tool(
    name="start_instance",
    description="Start a stopped compute instance (sends START action).",
    input_schema={
        "type": "object",
        "properties": {
            "instance_id": {"type": "string", "description": "OCID of the instance to start"},
        },
        "required": ["instance_id"],
    },
)
async def start_instance(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.compute_client()
    response = client.instance_action(instance_id=args["instance_id"], action="START")
    inst = response.data
    return {
        "content": [
            {
                "type": "text",
                "text": f"START action sent to instance {inst.id}. New state: {inst.lifecycle_state}",
            }
        ]
    }


@tool(
    name="stop_instance",
    description="Gracefully stop a running compute instance (sends SOFTSTOP action).",
    input_schema={
        "type": "object",
        "properties": {
            "instance_id": {"type": "string", "description": "OCID of the instance to stop"},
        },
        "required": ["instance_id"],
    },
)
async def stop_instance(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.compute_client()
    response = client.instance_action(instance_id=args["instance_id"], action="SOFTSTOP")
    inst = response.data
    return {
        "content": [
            {
                "type": "text",
                "text": f"SOFTSTOP action sent to instance {inst.id}. New state: {inst.lifecycle_state}",
            }
        ]
    }


ALL_TOOLS: list[SdkMcpTool] = [list_instances, get_instance, start_instance, stop_instance]

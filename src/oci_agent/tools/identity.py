"""IAM / Identity tools — compartments, users, groups, policies."""

import json

from claude_agent_sdk import SdkMcpTool, tool

from ..auth import OCIAuth


@tool(
    name="list_compartments",
    description="List all compartments under a tenancy or parent compartment.",
    input_schema={
        "type": "object",
        "properties": {
            "tenancy_id": {"type": "string", "description": "OCID of the tenancy or parent compartment"},
        },
        "required": ["tenancy_id"],
    },
)
async def list_compartments(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.identity_client()
    response = client.list_compartments(
        compartment_id=args["tenancy_id"],
        compartment_id_in_subtree=True,
        access_level="ACCESSIBLE",
    )
    compartments = [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "lifecycle_state": c.lifecycle_state,
            "compartment_id": c.compartment_id,
            "time_created": str(c.time_created),
        }
        for c in response.data
    ]
    return {"content": [{"type": "text", "text": json.dumps(compartments, indent=2)}]}


@tool(
    name="list_users",
    description="List IAM users in a tenancy with their state.",
    input_schema={
        "type": "object",
        "properties": {
            "tenancy_id": {"type": "string", "description": "OCID of the tenancy"},
        },
        "required": ["tenancy_id"],
    },
)
async def list_users(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.identity_client()
    response = client.list_users(compartment_id=args["tenancy_id"])
    users = [
        {
            "id": u.id,
            "name": u.name,
            "description": u.description,
            "lifecycle_state": u.lifecycle_state,
            "email": u.email,
            "is_mfa_activated": u.is_mfa_activated,
            "time_created": str(u.time_created),
        }
        for u in response.data
    ]
    return {"content": [{"type": "text", "text": json.dumps(users, indent=2)}]}


@tool(
    name="list_groups",
    description="List IAM groups in a tenancy.",
    input_schema={
        "type": "object",
        "properties": {
            "tenancy_id": {"type": "string", "description": "OCID of the tenancy"},
        },
        "required": ["tenancy_id"],
    },
)
async def list_groups(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.identity_client()
    response = client.list_groups(compartment_id=args["tenancy_id"])
    groups = [
        {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "lifecycle_state": g.lifecycle_state,
            "time_created": str(g.time_created),
        }
        for g in response.data
    ]
    return {"content": [{"type": "text", "text": json.dumps(groups, indent=2)}]}


@tool(
    name="list_policies",
    description="List IAM policies in a compartment.",
    input_schema={
        "type": "object",
        "properties": {
            "compartment_id": {"type": "string", "description": "OCID of the compartment"},
        },
        "required": ["compartment_id"],
    },
)
async def list_policies(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.identity_client()
    response = client.list_policies(compartment_id=args["compartment_id"])
    policies = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "lifecycle_state": p.lifecycle_state,
            "statements": p.statements,
            "time_created": str(p.time_created),
        }
        for p in response.data
    ]
    return {"content": [{"type": "text", "text": json.dumps(policies, indent=2)}]}


ALL_TOOLS: list[SdkMcpTool] = [list_compartments, list_users, list_groups, list_policies]

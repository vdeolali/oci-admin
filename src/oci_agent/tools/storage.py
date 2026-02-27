"""Storage tools — Object Storage buckets and Block Volumes."""

import json

from claude_agent_sdk import SdkMcpTool, tool

from ..auth import OCIAuth


@tool(
    name="list_buckets",
    description="List Object Storage buckets in a compartment.",
    input_schema={
        "type": "object",
        "properties": {
            "compartment_id": {"type": "string", "description": "OCID of the compartment"},
        },
        "required": ["compartment_id"],
    },
)
async def list_buckets(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.object_storage_client()
    namespace = client.get_namespace().data
    response = client.list_buckets(
        namespace_name=namespace,
        compartment_id=args["compartment_id"],
    )
    buckets = [
        {
            "name": b.name,
            "namespace": b.namespace,
            "compartment_id": b.compartment_id,
            "created_by": b.created_by,
            "time_created": str(b.time_created),
        }
        for b in response.data
    ]
    return {"content": [{"type": "text", "text": json.dumps(buckets, indent=2)}]}


@tool(
    name="get_bucket",
    description="Get metadata for a specific Object Storage bucket.",
    input_schema={
        "type": "object",
        "properties": {
            "bucket_name": {"type": "string", "description": "Name of the bucket"},
            "namespace": {"type": "string", "description": "Object Storage namespace (leave empty to auto-detect)"},
        },
        "required": ["bucket_name"],
    },
)
async def get_bucket(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.object_storage_client()
    namespace = args.get("namespace") or client.get_namespace().data
    response = client.get_bucket(
        namespace_name=namespace,
        bucket_name=args["bucket_name"],
    )
    b = response.data
    result = {
        "name": b.name,
        "namespace": b.namespace,
        "compartment_id": b.compartment_id,
        "storage_tier": b.storage_tier,
        "public_access_type": b.public_access_type,
        "versioning": b.versioning,
        "time_created": str(b.time_created),
        "etag": b.etag,
    }
    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


@tool(
    name="list_objects",
    description="List objects in an Object Storage bucket.",
    input_schema={
        "type": "object",
        "properties": {
            "bucket_name": {"type": "string", "description": "Name of the bucket"},
            "namespace": {"type": "string", "description": "Object Storage namespace (leave empty to auto-detect)"},
        },
        "required": ["bucket_name"],
    },
)
async def list_objects(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.object_storage_client()
    namespace = args.get("namespace") or client.get_namespace().data
    response = client.list_objects(
        namespace_name=namespace,
        bucket_name=args["bucket_name"],
    )
    objects = [
        {
            "name": o.name,
            "size": o.size,
            "time_modified": str(o.time_modified),
            "md5": o.md5,
            "storage_tier": o.storage_tier,
        }
        for o in (response.data.objects or [])
    ]
    return {"content": [{"type": "text", "text": json.dumps(objects, indent=2)}]}


@tool(
    name="list_block_volumes",
    description="List Block Storage volumes in a compartment with their state and size.",
    input_schema={
        "type": "object",
        "properties": {
            "compartment_id": {"type": "string", "description": "OCID of the compartment"},
        },
        "required": ["compartment_id"],
    },
)
async def list_block_volumes(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.blockstorage_client()
    response = client.list_volumes(compartment_id=args["compartment_id"])
    volumes = [
        {
            "id": v.id,
            "display_name": v.display_name,
            "lifecycle_state": v.lifecycle_state,
            "size_in_gbs": v.size_in_gbs,
            "availability_domain": v.availability_domain,
            "vpus_per_gb": v.vpus_per_gb,
            "time_created": str(v.time_created),
        }
        for v in response.data
    ]
    return {"content": [{"type": "text", "text": json.dumps(volumes, indent=2)}]}


@tool(
    name="get_bucket_sizes_by_user",
    description=(
        "List all Object Storage buckets in a compartment with their approximate size, "
        "grouped by the user OCID that created them. Uses the OCI 'approximateSize' field "
        "so no per-bucket API calls are needed."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "compartment_id": {"type": "string", "description": "OCID of the compartment"},
        },
        "required": ["compartment_id"],
    },
)
async def get_bucket_sizes_by_user(args: dict) -> dict:
    auth = OCIAuth()
    client = auth.object_storage_client()
    namespace = client.get_namespace().data

    # Paginate through all buckets (list gives us name + created_by)
    all_summaries = []
    page = None
    while True:
        kwargs: dict = {
            "namespace_name": namespace,
            "compartment_id": args["compartment_id"],
        }
        if page:
            kwargs["page"] = page
        response = client.list_buckets(**kwargs)
        all_summaries.extend(response.data)
        page = response.next_page if response.has_next_page else None
        if not page:
            break

    # Fetch full bucket details (approximate_size lives on the Bucket object, not BucketSummary)
    by_user: dict[str, dict] = {}
    for summary in all_summaries:
        detail = client.get_bucket(
            namespace_name=namespace,
            bucket_name=summary.name,
        ).data
        user = detail.created_by or summary.created_by or "unknown"
        if user not in by_user:
            by_user[user] = {"total_bytes": 0, "total_objects": 0, "buckets": []}
        size = detail.approximate_size or 0
        count = detail.approximate_count or 0
        by_user[user]["total_bytes"] += size
        by_user[user]["total_objects"] += count
        by_user[user]["buckets"].append({
            "name": detail.name,
            "approximate_size_bytes": size,
            "approximate_size_gb": round(size / (1024 ** 3), 3),
            "approximate_object_count": count,
            "storage_tier": detail.storage_tier,
            "time_created": str(detail.time_created),
        })

    # Sort users by total size descending
    summary = sorted(
        [
            {
                "created_by": user,
                "total_bytes": data["total_bytes"],
                "total_gb": round(data["total_bytes"] / (1024 ** 3), 3),
                "total_objects": data["total_objects"],
                "bucket_count": len(data["buckets"]),
                "buckets": sorted(data["buckets"], key=lambda x: x["approximate_size_bytes"], reverse=True),
            }
            for user, data in by_user.items()
        ],
        key=lambda x: x["total_bytes"],
        reverse=True,
    )

    result = {
        "namespace": namespace,
        "compartment_id": args["compartment_id"],
        "total_buckets": len(all_buckets),
        "by_user": summary,
    }
    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


ALL_TOOLS: list[SdkMcpTool] = [
    list_buckets,
    get_bucket,
    list_objects,
    list_block_volumes,
    get_bucket_sizes_by_user,
]

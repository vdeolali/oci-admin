# oci-admin
Claude generated agent to manage a tenancy on OCI
oci-admin — A Claude-powered CLI agent for managing an OCI tenancy via natural language.

  How it works:
  - You run it with python main.py -q "your question" (or with --profile to select an OCI config profile)
  - It uses the Claude Agent SDK to power a natural language loop
  - The agent calls OCI tools to answer queries or take actions

  Tools implemented across 4 modules:

  ┌──────────┬──────────────────────────────────────────────────────────────────────────────────────┐
  │  Module  │                                        Tools                                         │
  ├──────────┼──────────────────────────────────────────────────────────────────────────────────────┤
  │ Compute  │ list_instances, get_instance, start_instance, stop_instance                          │
  ├──────────┼──────────────────────────────────────────────────────────────────────────────────────┤
  │ Network  │ list_vcns, list_subnets, list_security_lists                                         │
  ├──────────┼──────────────────────────────────────────────────────────────────────────────────────┤
  │ Storage  │ list_buckets, get_bucket, list_objects, list_block_volumes, get_bucket_sizes_by_user │
  ├──────────┼──────────────────────────────────────────────────────────────────────────────────────┤
  │ Identity │ list_compartments, list_users, list_groups, list_policies                            │
  └──────────┴──────────────────────────────────────────────────────────────────────────────────────┘

  Key design decisions:
  - State-changing operations (start_instance, stop_instance) require confirmation before executing
  - OCI authentication via OCIAuth class using profile-based config
  - Built with uv for dependency management

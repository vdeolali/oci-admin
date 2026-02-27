"""OCI DevOps Agent — main agent loop using claude_agent_sdk."""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
)

from .config import settings
from .tools.compute import ALL_TOOLS as COMPUTE_TOOLS
from .tools.identity import ALL_TOOLS as IDENTITY_TOOLS
from .tools.network import ALL_TOOLS as NETWORK_TOOLS
from .tools.storage import ALL_TOOLS as STORAGE_TOOLS

SYSTEM_PROMPT = """\
You are an OCI DevOps agent that helps manage Oracle Cloud Infrastructure tenancies.

Guidelines:
- Always include OCIDs in your responses when referencing resources.
- Present structured data (instances, compartments, etc.) in a readable format.
- Before executing any state-changing operation (start_instance, stop_instance), \
clearly state what you are about to do and confirm the action with the user.
- When listing resources, summarise counts and key attributes.
- If an error occurs, report the OCI error code and message.
"""

STATE_CHANGING_TOOLS = {"start_instance", "stop_instance"}

ALL_TOOL_NAMES = [
    # compute
    "list_instances",
    "get_instance",
    "start_instance",
    "stop_instance",
    # network
    "list_vcns",
    "list_subnets",
    "list_security_lists",
    # storage
    "list_buckets",
    "get_bucket",
    "list_objects",
    "list_block_volumes",
    "get_bucket_sizes_by_user",
    # identity
    "list_compartments",
    "list_users",
    "list_groups",
    "list_policies",
]


class OCIAgent:
    """Claude-powered OCI DevOps agent."""

    def __init__(self, profile: str | None = None, model: str | None = None):
        self.profile = profile or settings.oci_profile
        self.model = model or settings.model

        all_tools = COMPUTE_TOOLS + NETWORK_TOOLS + STORAGE_TOOLS + IDENTITY_TOOLS
        self._mcp_server = create_sdk_mcp_server(
            name="oci-tools",
            version="1.0.0",
            tools=all_tools,
        )

    def _build_options(self) -> ClaudeAgentOptions:
        # Override CLAUDECODE="" so the spawned claude binary doesn't detect a nested session.
        # The SDK transport merges self._options.env after os.environ, so this takes precedence.
        env: dict[str, str] = {"CLAUDECODE": ""}
        api_key = settings.resolved_api_key
        if api_key:
            env["ANTHROPIC_API_KEY"] = api_key

        return ClaudeAgentOptions(
            system_prompt=SYSTEM_PROMPT,
            mcp_servers={"oci": self._mcp_server},
            allowed_tools=ALL_TOOL_NAMES,
            model=self.model,
            permission_mode="bypassPermissions",
            env=env,
        )

    async def run(self, user_query: str) -> str:
        """Run a single query through the agent and print the response.

        Uses ClaudeSDKClient (streaming mode) so that in-process SDK MCP servers
        can complete their control-protocol handshake before stdin is closed.
        """
        options = self._build_options()
        full_response: list[str] = []

        async with ClaudeSDKClient(options) as client:
            await client.query(user_query)
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text, end="", flush=True)
                            full_response.append(block.text)
                elif isinstance(message, ResultMessage):
                    print()
                    if message.is_error:
                        print(f"\n[Error] Session ended with error: {message.result}")

        return "".join(full_response)

"""OCI DevOps Agent — CLI entry point."""

import asyncio

import click


@click.command()
@click.option(
    "--profile",
    default=None,
    help="OCI config profile name (overrides OCI_PROFILE env var, default: CVM)",
)
@click.option(
    "--query", "-q",
    "user_query",
    required=True,
    help="Natural language query to run against the OCI tenancy",
)
def main(profile: str | None, user_query: str) -> None:
    """OCI DevOps Agent powered by Claude AI.

    Examples:

      python main.py -q "List all compartments in my tenancy"

      python main.py --profile DEFAULT -q "List all VCNs"

      python main.py -q "How many compute instances are running in compartment ocid1.compartment..."
    """
    # Import here so the OCI_PROFILE override takes effect before OCIAuth reads settings
    if profile:
        import os
        os.environ["OCI_PROFILE"] = profile

    from src.oci_agent.agent import OCIAgent

    agent = OCIAgent(profile=profile)
    asyncio.run(agent.run(user_query))


if __name__ == "__main__":
    main()

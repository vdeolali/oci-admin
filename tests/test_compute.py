"""Tests for compute tools."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest


def _make_mock_instance(
    ocid="ocid1.instance.oc1..aaa",
    display_name="test-vm",
    lifecycle_state="RUNNING",
    shape="VM.Standard.E4.Flex",
    compartment_id="ocid1.compartment.oc1..xxx",
    region="us-phoenix-1",
    availability_domain="AD-1",
):
    inst = MagicMock()
    inst.id = ocid
    inst.display_name = display_name
    inst.lifecycle_state = lifecycle_state
    inst.shape = shape
    inst.compartment_id = compartment_id
    inst.region = region
    inst.availability_domain = availability_domain
    inst.time_created = "2024-01-01T00:00:00Z"
    return inst


class TestListInstances:
    def test_returns_structured_data(self):
        mock_instance = _make_mock_instance()
        mock_response = MagicMock()
        mock_response.data = [mock_instance]

        mock_client = MagicMock()
        mock_client.list_instances.return_value = mock_response

        with patch("src.oci_agent.tools.compute.OCIAuth") as MockAuth:
            MockAuth.return_value.compute_client.return_value = mock_client

            from src.oci_agent.tools.compute import list_instances

            result = asyncio.run(
                list_instances.handler({"compartment_id": "ocid1.compartment.oc1..xxx"})
            )

        assert "content" in result
        assert len(result["content"]) == 1
        import json
        data = json.loads(result["content"][0]["text"])
        assert isinstance(data, list)
        assert data[0]["id"] == "ocid1.instance.oc1..aaa"
        assert data[0]["lifecycle_state"] == "RUNNING"
        assert data[0]["shape"] == "VM.Standard.E4.Flex"

    def test_respects_limit(self):
        mock_response = MagicMock()
        mock_response.data = []

        mock_client = MagicMock()
        mock_client.list_instances.return_value = mock_response

        with patch("src.oci_agent.tools.compute.OCIAuth") as MockAuth:
            MockAuth.return_value.compute_client.return_value = mock_client

            from src.oci_agent.tools.compute import list_instances

            asyncio.run(
                list_instances.handler({"compartment_id": "ocid1.compartment.oc1..xxx", "limit": 5})
            )

        mock_client.list_instances.assert_called_once_with(
            compartment_id="ocid1.compartment.oc1..xxx",
            limit=5,
        )


class TestGetInstance:
    def test_returns_single_instance(self):
        mock_instance = _make_mock_instance(ocid="ocid1.instance.oc1..bbb", display_name="my-vm")
        mock_response = MagicMock()
        mock_response.data = mock_instance

        mock_client = MagicMock()
        mock_client.get_instance.return_value = mock_response

        with patch("src.oci_agent.tools.compute.OCIAuth") as MockAuth:
            MockAuth.return_value.compute_client.return_value = mock_client

            from src.oci_agent.tools.compute import get_instance

            result = asyncio.run(get_instance.handler({"instance_id": "ocid1.instance.oc1..bbb"}))

        import json
        data = json.loads(result["content"][0]["text"])
        assert data["id"] == "ocid1.instance.oc1..bbb"
        assert data["display_name"] == "my-vm"


class TestStartStopInstance:
    def test_start_instance(self):
        mock_instance = _make_mock_instance(lifecycle_state="STARTING")
        mock_response = MagicMock()
        mock_response.data = mock_instance

        mock_client = MagicMock()
        mock_client.instance_action.return_value = mock_response

        with patch("src.oci_agent.tools.compute.OCIAuth") as MockAuth:
            MockAuth.return_value.compute_client.return_value = mock_client

            from src.oci_agent.tools.compute import start_instance

            result = asyncio.run(start_instance.handler({"instance_id": "ocid1.instance.oc1..aaa"}))

        mock_client.instance_action.assert_called_once_with(
            instance_id="ocid1.instance.oc1..aaa", action="START"
        )
        assert "START" in result["content"][0]["text"]

    def test_stop_instance(self):
        mock_instance = _make_mock_instance(lifecycle_state="STOPPING")
        mock_response = MagicMock()
        mock_response.data = mock_instance

        mock_client = MagicMock()
        mock_client.instance_action.return_value = mock_response

        with patch("src.oci_agent.tools.compute.OCIAuth") as MockAuth:
            MockAuth.return_value.compute_client.return_value = mock_client

            from src.oci_agent.tools.compute import stop_instance

            result = asyncio.run(stop_instance.handler({"instance_id": "ocid1.instance.oc1..aaa"}))

        mock_client.instance_action.assert_called_once_with(
            instance_id="ocid1.instance.oc1..aaa", action="SOFTSTOP"
        )
        assert "SOFTSTOP" in result["content"][0]["text"]

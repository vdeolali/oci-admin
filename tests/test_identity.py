"""Tests for identity/IAM tools."""

import asyncio
import json
from unittest.mock import MagicMock, patch


def _make_mock_compartment(
    ocid="ocid1.compartment.oc1..aaa",
    name="MyCompartment",
    description="Test compartment",
    lifecycle_state="ACTIVE",
    compartment_id="ocid1.tenancy.oc1..xxx",
):
    c = MagicMock()
    c.id = ocid
    c.name = name
    c.description = description
    c.lifecycle_state = lifecycle_state
    c.compartment_id = compartment_id
    c.time_created = "2024-01-01T00:00:00Z"
    return c


class TestListCompartments:
    def test_returns_compartment_list(self):
        mock_compartment = _make_mock_compartment()
        mock_response = MagicMock()
        mock_response.data = [mock_compartment]

        mock_client = MagicMock()
        mock_client.list_compartments.return_value = mock_response

        with patch("src.oci_agent.tools.identity.OCIAuth") as MockAuth:
            MockAuth.return_value.identity_client.return_value = mock_client

            from src.oci_agent.tools.identity import list_compartments

            result = asyncio.run(
                list_compartments.handler({"tenancy_id": "ocid1.tenancy.oc1..xxx"})
            )

        assert "content" in result
        data = json.loads(result["content"][0]["text"])
        assert isinstance(data, list)
        assert data[0]["id"] == "ocid1.compartment.oc1..aaa"
        assert data[0]["name"] == "MyCompartment"
        assert data[0]["lifecycle_state"] == "ACTIVE"

    def test_calls_with_subtree(self):
        mock_response = MagicMock()
        mock_response.data = []

        mock_client = MagicMock()
        mock_client.list_compartments.return_value = mock_response

        with patch("src.oci_agent.tools.identity.OCIAuth") as MockAuth:
            MockAuth.return_value.identity_client.return_value = mock_client

            from src.oci_agent.tools.identity import list_compartments

            asyncio.run(list_compartments.handler({"tenancy_id": "ocid1.tenancy.oc1..xxx"}))

        mock_client.list_compartments.assert_called_once_with(
            compartment_id="ocid1.tenancy.oc1..xxx",
            compartment_id_in_subtree=True,
            access_level="ACCESSIBLE",
        )


class TestListUsers:
    def test_returns_user_list(self):
        mock_user = MagicMock()
        mock_user.id = "ocid1.user.oc1..aaa"
        mock_user.name = "jdoe@example.com"
        mock_user.description = "Jane Doe"
        mock_user.lifecycle_state = "ACTIVE"
        mock_user.email = "jdoe@example.com"
        mock_user.is_mfa_activated = True
        mock_user.time_created = "2024-01-01T00:00:00Z"

        mock_response = MagicMock()
        mock_response.data = [mock_user]

        mock_client = MagicMock()
        mock_client.list_users.return_value = mock_response

        with patch("src.oci_agent.tools.identity.OCIAuth") as MockAuth:
            MockAuth.return_value.identity_client.return_value = mock_client

            from src.oci_agent.tools.identity import list_users

            result = asyncio.run(list_users.handler({"tenancy_id": "ocid1.tenancy.oc1..xxx"}))

        data = json.loads(result["content"][0]["text"])
        assert data[0]["name"] == "jdoe@example.com"
        assert data[0]["is_mfa_activated"] is True


class TestListGroups:
    def test_returns_group_list(self):
        mock_group = MagicMock()
        mock_group.id = "ocid1.group.oc1..aaa"
        mock_group.name = "Administrators"
        mock_group.description = "Admin group"
        mock_group.lifecycle_state = "ACTIVE"
        mock_group.time_created = "2024-01-01T00:00:00Z"

        mock_response = MagicMock()
        mock_response.data = [mock_group]

        mock_client = MagicMock()
        mock_client.list_groups.return_value = mock_response

        with patch("src.oci_agent.tools.identity.OCIAuth") as MockAuth:
            MockAuth.return_value.identity_client.return_value = mock_client

            from src.oci_agent.tools.identity import list_groups

            result = asyncio.run(list_groups.handler({"tenancy_id": "ocid1.tenancy.oc1..xxx"}))

        data = json.loads(result["content"][0]["text"])
        assert data[0]["name"] == "Administrators"

"""OCI authentication and client factory."""

import oci

from .config import settings


class OCIAuth:
    """Factory for authenticated OCI service clients."""

    def __init__(self, profile: str | None = None):
        self.profile = profile or settings.oci_profile
        self._config: dict | None = None

    def get_config(self) -> dict:
        if self._config is None:
            self._config = oci.config.from_file(
                file_location=settings.resolved_oci_config_path,
                profile_name=self.profile,
            )
            oci.config.validate_config(self._config)
        return self._config

    def compute_client(self) -> oci.core.ComputeClient:
        return oci.core.ComputeClient(self.get_config())

    def virtual_network_client(self) -> oci.core.VirtualNetworkClient:
        return oci.core.VirtualNetworkClient(self.get_config())

    def object_storage_client(self) -> oci.object_storage.ObjectStorageClient:
        return oci.object_storage.ObjectStorageClient(self.get_config())

    def blockstorage_client(self) -> oci.core.BlockstorageClient:
        return oci.core.BlockstorageClient(self.get_config())

    def identity_client(self) -> oci.identity.IdentityClient:
        return oci.identity.IdentityClient(self.get_config())

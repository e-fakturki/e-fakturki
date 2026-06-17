from typing import Any

from ksef_client import KsefClient
from ksef_client.services import OnlineSessionResult, OnlineSessionWorkflow
from pydantic import BaseModel, ConfigDict


class EncryptionData(BaseModel):
    """Schema needed for type hinting of encryption data used in ksef session."""


# class KsefSessionParams(BaseModel):
#     """Parameters needed to run a ksef session."""

#     workflow: OnlineSessionWorkflow
#     session: OnlineSessionResult

#     model_config = ConfigDict(arbitrary_types_allowed=True)

from dataclasses import dataclass

@dataclass
class KsefSessionParams:
    """Parameters needed to run a ksef session."""
    workflow: OnlineSessionWorkflow
    session: OnlineSessionResult


def open_ksef_session(
    client: KsefClient,
    access_token: str,
    sym_cert: str,
    form_code: dict[str, Any] | None = None,
    upo_v43: bool = False,
) -> KsefSessionParams:
    """
    Opens a KSeF API session using the access token obtained after authentication.

    Args:
        client: An instance of KsefClient.
        access_token: Access token obtained after authentication.
        sym_cert: Symmetric certificate for encryption.
        form_code: Form code for the session.
        upo_v43: Whether to use UPO v4.3 format.

    Returns:
        An instance of KsefSessionParams containing the session parameters.
    """
    if form_code is None:
        form_code = {
            "systemCode": "FA (3)",
            "schemaVersion": "1-0E",
            "value": "FA",
        }

    workflow = OnlineSessionWorkflow(client.sessions)

    session = workflow.open_session(
        form_code=form_code,
        public_certificate=sym_cert,
        access_token=access_token,
        upo_v43=upo_v43,
    )

    return KsefSessionParams(workflow=workflow, session=session)

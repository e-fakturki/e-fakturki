import tempfile
from pathlib import Path

from ksef_client import KsefClient
from ksef_client.services import AuthCoordinator, AuthResult, XadesKeyPair


def certificate_str_to_temp_file(
    cert_str: str, suffix: str = ".pem", encoding: str = "utf-8"
) -> str:
    """
    Export the certificate content to a temporary file.

    Args:
        cert_str: Content of the certificate.
        suffix: Suffix for the temporary file (e.g., ".pem").
        encoding: Encoding for the temporary file.

    Returns:
        The name of the temporary file.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding=encoding
    ) as tmp:
        tmp.write(cert_str)
        tmp.flush()
        tmp.close()
        return tmp.name


def remove_temp_file(file_path: str) -> None:
    """Removes the temporary file at the specified path."""
    Path(file_path).unlink(missing_ok=True)


def authorize_ksef_with_certificate(
    certificate_path: str,
    private_key_path: str,
    private_key_password: str,
    client: KsefClient,
    context_id_value: str,
    context_identifier: str = "nip",
    subject_id_type: str = "certificateSubject",
    verify_certificate_chain: bool | None = None,
    max_attempts: int = 90,
    poll_interval_s: float = 2.0,
) -> AuthResult:
    """
    Authorizes with KSeF using certificate authentication.

    Args:
        certificate_path: Path to the certificate file.
        private_key_path: Path to the private key file.
        private_key_password: Password for the private key.
        client: An instance of KsefClient.
        context_id_value: Value of the context identifier (e.g., company NIP).
        context_identifier: Type of the context identifier (default: "nip").
        subject_id_type: Type of the subject identifier (default: "certificateSubject").
        verify_certificate_chain: Whether to verify the certificate chain (default: None).
        max_attempts: Maximum number of attempts to check authentication status (default: 90).
        poll_interval_s: Interval in seconds between authentication status checks (default: 2.0).

    Returns:
        An instance of AuthResult containing the authentication result.
    """
    key_pair = XadesKeyPair.from_pem_files(
        certificate_path=certificate_path,
        private_key_path=private_key_path,
        private_key_password=private_key_password,
    )

    return AuthCoordinator(client.auth).authenticate_with_xades_key_pair(
        key_pair=key_pair,
        context_identifier_type=context_identifier,
        context_identifier_value=context_id_value,
        subject_identifier_type=subject_id_type,
        verify_certificate_chain=verify_certificate_chain,
        max_attempts=max_attempts,
        poll_interval_seconds=poll_interval_s,
    )

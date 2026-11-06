from fastapi import APIRouter

from .post_ksef_certificates import router as post_ksef_certificates_router
from .post_single_invoice import router as post_single_invoice_router
from .get_invoices_metadata import router as get_invoices_metadata_router
from .get_single_invoice import router as get_single_invoice_router
from .get_sessions import router as get_sessions_router

router = APIRouter(prefix="/ksef", tags=["ksef"])

router.include_router(post_ksef_certificates_router)
router.include_router(post_single_invoice_router)
router.include_router(get_invoices_metadata_router)
router.include_router(get_single_invoice_router)
router.include_router(get_sessions_router)

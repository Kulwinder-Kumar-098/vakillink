from fastapi import APIRouter, Depends, Body
from app.api.dependencies import require_role
from app.services.admin_service import AdminService

router = APIRouter()
admin_service = AdminService()

@router.get("/queue", dependencies=[Depends(require_role(["admin"]))])
def get_approval_queue():
    """
    Get list of unverified lawyers waiting for admin approval.
    Accessible only to users with the 'admin' role.
    """
    return admin_service.get_pending_lawyers()

@router.post("/approve/{lawyer_id}", dependencies=[Depends(require_role(["admin"]))])
def approve_lawyer(lawyer_id: str):
    """
    Approve a lawyer's Bar Council ID and set is_verified to True.
    """
    return admin_service.approve_lawyer(lawyer_id)

@router.post("/reject/{lawyer_id}", dependencies=[Depends(require_role(["admin"]))])
def reject_lawyer(lawyer_id: str, reason: str = Body(default=None, embed=True)):
    """
    Reject a lawyer application. Demotes them to 'client' and removes lawyer-specific data.
    """
    return admin_service.reject_lawyer(lawyer_id, reason)

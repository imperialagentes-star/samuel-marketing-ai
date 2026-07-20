from fastapi import APIRouter, HTTPException
from ..models import WorkflowCreate, WorkflowContinue, WorkflowRegenerate
from ..services.workflow_engine import (
    create_workflow,
    run_next_step,
    samuel_continues,
    regenerate_step,
    get_workflow_detail,
    list_workflows,
    list_pending_workflows,
)

router = APIRouter()


@router.post("/")
def create(req: WorkflowCreate):
    wf_id = create_workflow(
        client_id=req.client_id,
        name=req.name,
        focus=req.focus or "",
        event_type=req.event_type or "",
        event_description=req.event_description or "",
        event_date=req.event_date or "",
        timeline_type=req.timeline_type,
    )
    return {"id": wf_id, "status": "created"}


@router.get("/")
def list_all():
    return list_workflows()


@router.get("/pending")
def pending():
    return list_pending_workflows()


@router.get("/{workflow_id}")
def detail(workflow_id: int):
    wf = get_workflow_detail(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow no encontrado")
    return wf


@router.get("/{workflow_id}/timeline")
def timeline(workflow_id: int):
    wf = get_workflow_detail(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow no encontrado")
    return {
        "workflow_id": workflow_id,
        "name": wf["name"],
        "client_name": wf.get("client_name"),
        "event_date": wf.get("event_date"),
        "timeline_type": wf.get("timeline_type"),
        "steps": [
            {
                "step_order": s["step_order"],
                "step_type": s["step_type"],
                "planned_date": s["planned_date"],
                "priority": s["priority"],
                "status": s["status"],
            }
            for s in wf["steps"]
        ],
    }


@router.post("/{workflow_id}/start")
def start(workflow_id: int):
    result = run_next_step(workflow_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{workflow_id}/continue")
def continue_workflow(workflow_id: int, req: WorkflowContinue):
    wf = get_workflow_detail(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow no encontrado")

    waiting = [s for s in wf["steps"] if s["status"] == "waiting_samuel"]
    if not waiting:
        raise HTTPException(status_code=400, detail="No hay paso esperando aprobación")

    step_id = waiting[0]["id"]
    return samuel_continues(workflow_id, step_id, req.samuel_notes or "", req.samuel_choice)


@router.post("/{workflow_id}/regenerate/{step_id}")
def regenerate(workflow_id: int, step_id: int, req: WorkflowRegenerate):
    result = regenerate_step(workflow_id, step_id, req.samuel_notes)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

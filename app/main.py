import json
import os
import shutil
import uuid
from datetime import datetime
from typing import List
from typing import Optional

from fastapi import Depends
from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.config import APP_DIR
from app.config import GOOGLE_CLIENT_ID
from app.config import SAMPLE_DIR
from app.config import SECRET_KEY
from app.config import UPLOAD_DIR
from app.database import Base
from app.database import engine
from app.database import get_db
from app.models import AuthAccount
from app.models import CollectionCycle
from app.models import CycleBlueprint
from app.models import CycleBreakEdge
from app.models import CycleFocusNode
from app.models import CycleRun
from app.models import FocusCompletionRecord
from app.models import FocusTaskRecord
from app.models import Photo
from app.models import Quote
from app.models import RewardEntitlement
from app.models import User
from app.models import UserAssetOwnership
from app.models import UserCycleOwnership
from app.seed import ensure_user_defaults
from app.seed import get_or_create_demo_user
from app.seed import grant_asset_if_missing
from app.seed import seed_reference_data


templates = Jinja2Templates(directory=os.path.join(APP_DIR, "templates"))
app = FastAPI(title="Pure Focus")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory=os.path.join(APP_DIR, "static")), name="static")
app.mount("/sample", StaticFiles(directory=SAMPLE_DIR), name="sample")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


class GoogleLoginPayload(BaseModel):
    email: str
    provider_user_id: str
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None


class FocusNodeInput(BaseModel):
    focus_duration_seconds: int
    break_duration_seconds: Optional[int] = None
    photo_id: int
    quote_id: int


class CreateCyclePayload(BaseModel):
    name: str
    nodes: List[FocusNodeInput]


class CreateRunPayload(BaseModel):
    cycle_blueprint_id: int
    cycle_mode: str


class FocusCompletePayload(BaseModel):
    focus_order: int
    checked_todos: List[str]
    remaining_nottodos: List[str]


def initialize_app_state():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed_reference_data(db)
    finally:
        db.close()


@app.on_event("startup")
def startup():
    initialize_app_state()


initialize_app_state()


def get_user_from_session(request: Request, db: Session) -> Optional[User]:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_user_from_session(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def photo_url(photo: Photo) -> str:
    if photo.origin == "sample":
        return "/sample/{}".format(photo.storage_key)
    return "/uploads/{}".format(photo.storage_key)


def serialize_photo(photo: Photo) -> dict:
    return {
        "id": photo.id,
        "origin": photo.origin,
        "url": photo_url(photo),
        "sourceLabel": photo.source_label,
        "sourceUrl": photo.source_url,
    }


def serialize_quote(quote: Quote) -> dict:
    return {
        "id": quote.id,
        "origin": quote.origin,
        "text": quote.text,
        "authorName": quote.author_name,
        "category": quote.category,
    }


def serialize_blueprint(blueprint: CycleBlueprint, owned: bool, trial_available: bool) -> dict:
    return {
        "id": blueprint.id,
        "name": blueprint.name,
        "mode": "owned" if owned else "trial",
        "owned": owned,
        "trialAvailable": trial_available,
        "editable": owned or blueprint.mode == "custom",
        "focusNodes": [
            {
                "nodeOrder": node.node_order,
                "focusDurationSeconds": node.focus_duration_seconds,
                "photo": serialize_photo(node.photo),
                "quote": serialize_quote(node.quote),
            }
            for node in blueprint.focus_nodes
        ],
        "breakEdges": [
            {
                "fromNodeOrder": edge.from_node_order,
                "toNodeOrder": edge.to_node_order,
                "breakDurationSeconds": edge.break_duration_seconds,
            }
            for edge in blueprint.break_edges
        ],
    }


def parse_task_items(items: List[str]) -> List[str]:
    results = []
    for item in items:
        text = item.strip()
        if text and text not in results:
            results.append(text)
    return results


def get_owned_asset_ids(db: Session, user_id: int, asset_type: str) -> set:
    rows = db.query(UserAssetOwnership.asset_id).filter(
        UserAssetOwnership.user_id == user_id,
        UserAssetOwnership.asset_type == asset_type,
    ).all()
    return set([row[0] for row in rows])


def get_owned_cycle_ids(db: Session, user_id: int) -> set:
    rows = db.query(UserCycleOwnership.cycle_blueprint_id).filter(
        UserCycleOwnership.user_id == user_id
    ).all()
    return set([row[0] for row in rows])


def ensure_reward_entitlement(db: Session, run: CycleRun) -> RewardEntitlement:
    entitlement = db.query(RewardEntitlement).filter(RewardEntitlement.run_id == run.id).first()
    if entitlement:
        return entitlement
    entitlement = RewardEntitlement(
        run_id=run.id,
        user_id=run.user_id,
        status="pending",
        allowed_actions_json=json.dumps(["claim_cycle", "upload_photo", "add_quote"]),
    )
    db.add(entitlement)
    db.flush()
    return entitlement


def use_reward_entitlement(db: Session, run_id: int, user_id: int) -> RewardEntitlement:
    entitlement = db.query(RewardEntitlement).filter(
        RewardEntitlement.run_id == run_id,
        RewardEntitlement.user_id == user_id,
        RewardEntitlement.status == "pending",
    ).first()
    if not entitlement:
        raise HTTPException(status_code=404, detail="Pending reward not found")
    entitlement.status = "used"
    entitlement.used_at = datetime.utcnow()
    return entitlement


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "google_client_id": GOOGLE_CLIENT_ID},
    )


@app.post("/auth/demo-login")
def demo_login(request: Request, db: Session = Depends(get_db)):
    user = get_or_create_demo_user(db)
    request.session["user_id"] = user.id
    return {"ok": True, "user": {"id": user.id, "email": user.email, "nickname": user.nickname}}


@app.post("/auth/google/callback")
def google_callback(payload: GoogleLoginPayload, request: Request, db: Session = Depends(get_db)):
    account = db.query(AuthAccount).filter(
        AuthAccount.provider == "google",
        AuthAccount.provider_user_id == payload.provider_user_id,
    ).first()
    if account:
        user = db.query(User).filter(User.id == account.user_id).first()
    else:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user:
            user = User(
                email=payload.email,
                nickname=payload.nickname or payload.email.split("@")[0],
                profile_image_url=payload.profile_image_url,
            )
            db.add(user)
            db.flush()
        account = AuthAccount(
            user_id=user.id,
            provider="google",
            provider_user_id=payload.provider_user_id,
            provider_email=payload.email,
        )
        db.add(account)
    user.last_login_at = datetime.utcnow()
    ensure_user_defaults(db, user)
    db.commit()
    request.session["user_id"] = user.id
    return {"ok": True}


@app.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.get("/me")
def me(request: Request, db: Session = Depends(get_db)):
    user = get_user_from_session(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Authentication required"})
    ensure_user_defaults(db, user)
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "profileImageUrl": user.profile_image_url,
    }


@app.get("/assets/photos")
def get_photos(user: User = Depends(require_user), db: Session = Depends(get_db)):
    owned_ids = get_owned_asset_ids(db, user.id, "photo")
    photos = db.query(Photo).filter(Photo.id.in_(owned_ids)).all() if owned_ids else []
    return {"items": [serialize_photo(photo) for photo in photos]}


@app.get("/assets/quotes")
def get_quotes(user: User = Depends(require_user), db: Session = Depends(get_db)):
    owned_ids = get_owned_asset_ids(db, user.id, "quote")
    quotes = db.query(Quote).filter(Quote.id.in_(owned_ids)).all() if owned_ids else []
    return {"items": [serialize_quote(quote) for quote in quotes]}


@app.get("/cycles")
def get_cycles(user: User = Depends(require_user), db: Session = Depends(get_db)):
    ensure_user_defaults(db, user)
    owned_cycle_ids = get_owned_cycle_ids(db, user.id)
    blueprints = db.query(CycleBlueprint).order_by(CycleBlueprint.id).all()
    items = []
    for blueprint in blueprints:
        owned = blueprint.id in owned_cycle_ids or blueprint.owner_user_id == user.id
        trial_available = blueprint.is_trial_available and not owned
        if owned or trial_available:
            items.append(serialize_blueprint(blueprint, owned=owned, trial_available=trial_available))
    return {"items": items}


@app.post("/cycles/custom")
def create_custom_cycle(
    payload: CreateCyclePayload,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    if len(payload.nodes) < 1:
        raise HTTPException(status_code=400, detail="At least one focus node is required")
    owned_photo_ids = get_owned_asset_ids(db, user.id, "photo")
    owned_quote_ids = get_owned_asset_ids(db, user.id, "quote")
    for node in payload.nodes:
        if node.photo_id not in owned_photo_ids or node.quote_id not in owned_quote_ids:
            raise HTTPException(status_code=400, detail="Only owned assets can be used in custom cycles")
        if node.focus_duration_seconds < 1:
            raise HTTPException(status_code=400, detail="Focus duration must be positive")
        if node.break_duration_seconds is not None and node.break_duration_seconds < 1:
            raise HTTPException(status_code=400, detail="Break duration must be positive")
    blueprint = CycleBlueprint(
        name=payload.name.strip() or "Custom cycle",
        owner_user_id=user.id,
        mode="custom",
        is_owned_by_default=False,
        is_trial_available=False,
        is_editable_when_unowned=False,
    )
    db.add(blueprint)
    db.flush()
    for index, node in enumerate(payload.nodes, start=1):
        db.add(
            CycleFocusNode(
                cycle_blueprint_id=blueprint.id,
                node_order=index,
                focus_duration_seconds=node.focus_duration_seconds,
                photo_id=node.photo_id,
                quote_id=node.quote_id,
            )
        )
        if index < len(payload.nodes):
            db.add(
                CycleBreakEdge(
                    cycle_blueprint_id=blueprint.id,
                    from_node_order=index,
                    to_node_order=index + 1,
                    break_duration_seconds=payload.nodes[index - 1].break_duration_seconds or 5,
                )
            )
    db.flush()
    db.add(
        UserCycleOwnership(
            user_id=user.id,
            cycle_blueprint_id=blueprint.id,
            ownership_source="custom_cycle",
        )
    )
    db.commit()
    db.refresh(blueprint)
    return {"item": serialize_blueprint(blueprint, owned=True, trial_available=False)}


@app.post("/runs")
def create_run(
    payload: CreateRunPayload,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    blueprint = db.query(CycleBlueprint).filter(CycleBlueprint.id == payload.cycle_blueprint_id).first()
    if not blueprint:
        raise HTTPException(status_code=404, detail="Cycle not found")
    owned_cycle_ids = get_owned_cycle_ids(db, user.id)
    owned = blueprint.id in owned_cycle_ids or blueprint.owner_user_id == user.id
    if payload.cycle_mode == "owned" and not owned:
        raise HTTPException(status_code=400, detail="Cycle is not owned")
    if payload.cycle_mode == "trial" and (owned or not blueprint.is_trial_available):
        raise HTTPException(status_code=400, detail="Cycle is not available for trial")
    if payload.cycle_mode not in ("owned", "trial", "custom"):
        raise HTTPException(status_code=400, detail="Invalid cycle mode")
    active_runs = db.query(CycleRun).filter(
        CycleRun.user_id == user.id,
        CycleRun.status == "active",
    ).all()
    for run in active_runs:
        run.status = "stopped"
    run = CycleRun(
        user_id=user.id,
        cycle_blueprint_id=blueprint.id,
        cycle_mode=payload.cycle_mode,
        status="active",
        completed_focus_count=0,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return {"runId": run.id}


@app.post("/runs/{run_id}/focus-complete")
def complete_focus(
    run_id: int,
    payload: FocusCompletePayload,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    run = db.query(CycleRun).filter(CycleRun.id == run_id, CycleRun.user_id == user.id).first()
    if not run or run.status != "active":
        raise HTTPException(status_code=404, detail="Active run not found")
    blueprint = run.cycle_blueprint
    expected_order = run.completed_focus_count + 1
    if payload.focus_order != expected_order:
        raise HTTPException(status_code=400, detail="Unexpected focus order")
    node = [item for item in blueprint.focus_nodes if item.node_order == payload.focus_order]
    if not node:
        raise HTTPException(status_code=400, detail="Focus node not found")
    node = node[0]
    record = FocusCompletionRecord(
        run_id=run.id,
        focus_order=payload.focus_order,
        photo_id=node.photo_id,
        quote_id=node.quote_id,
        focus_duration_seconds=node.focus_duration_seconds,
    )
    db.add(record)
    db.flush()
    for item in parse_task_items(payload.checked_todos):
        db.add(FocusTaskRecord(focus_completion_record_id=record.id, task_type="todo", content=item))
    for item in parse_task_items(payload.remaining_nottodos):
        db.add(FocusTaskRecord(focus_completion_record_id=record.id, task_type="nottodo", content=item))
    run.completed_focus_count = payload.focus_order
    run.updated_at = datetime.utcnow()
    db.commit()
    return {"completedFocusCount": run.completed_focus_count}


@app.post("/runs/{run_id}/stop")
def stop_run(run_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    run = db.query(CycleRun).filter(CycleRun.id == run_id, CycleRun.user_id == user.id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run.status = "stopped"
    run.updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True}


@app.post("/runs/{run_id}/complete")
def complete_run(run_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    run = db.query(CycleRun).filter(CycleRun.id == run_id, CycleRun.user_id == user.id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    total_focus = len(run.cycle_blueprint.focus_nodes)
    if run.completed_focus_count != total_focus:
        raise HTTPException(status_code=400, detail="Run is not ready to complete")
    run.status = "completed"
    entitlement = ensure_reward_entitlement(db, run)
    db.commit()
    return {
        "ok": True,
        "reward": {
            "entitlementId": entitlement.id,
            "actions": json.loads(entitlement.allowed_actions_json),
        },
    }


@app.post("/rewards/{run_id}/claim-cycle")
def claim_cycle(run_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    run = db.query(CycleRun).filter(CycleRun.id == run_id, CycleRun.user_id == user.id).first()
    if not run or run.status != "completed":
        raise HTTPException(status_code=404, detail="Completed run not found")
    use_reward_entitlement(db, run_id, user.id)
    blueprint = run.cycle_blueprint
    existing = db.query(UserCycleOwnership).filter(
        UserCycleOwnership.user_id == user.id,
        UserCycleOwnership.cycle_blueprint_id == blueprint.id,
    ).first()
    if not existing:
        db.add(
            UserCycleOwnership(
                user_id=user.id,
                cycle_blueprint_id=blueprint.id,
                ownership_source="cycle_claim",
            )
        )
    for node in blueprint.focus_nodes:
        grant_asset_if_missing(db, user.id, "photo", node.photo_id, "cycle_claim")
        grant_asset_if_missing(db, user.id, "quote", node.quote_id, "cycle_claim")
    db.add(
        CollectionCycle(
            user_id=user.id,
            cycle_blueprint_id=blueprint.id,
            source_run_id=run.id,
        )
    )
    db.commit()
    return {"ok": True}


@app.post("/rewards/{run_id}/upload-photo")
def reward_upload_photo(
    run_id: int,
    file: UploadFile = File(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    use_reward_entitlement(db, run_id, user.id)
    extension = os.path.splitext(file.filename or "")[1] or ".jpg"
    filename = "{}{}".format(uuid.uuid4().hex, extension)
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as output:
        shutil.copyfileobj(file.file, output)
    photo = Photo(
        origin="user_upload",
        storage_key=filename,
        source_label=user.nickname,
        source_url=None,
    )
    db.add(photo)
    db.flush()
    grant_asset_if_missing(db, user.id, "photo", photo.id, "reward_upload")
    db.commit()
    return {"ok": True, "photo": serialize_photo(photo)}


@app.post("/rewards/{run_id}/add-quote")
def reward_add_quote(
    run_id: int,
    text: str = Form(...),
    author_name: str = Form(...),
    category: str = Form("custom"),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    use_reward_entitlement(db, run_id, user.id)
    if not text.strip() or not author_name.strip():
        raise HTTPException(status_code=400, detail="Quote text and author are required")
    quote = Quote(
        origin="user_input",
        text=text.strip(),
        author_name=author_name.strip(),
        category=category.strip() or "custom",
    )
    db.add(quote)
    db.flush()
    grant_asset_if_missing(db, user.id, "quote", quote.id, "reward_quote")
    db.commit()
    return {"ok": True, "quote": serialize_quote(quote)}


@app.get("/dashboard/summary")
def dashboard_summary(user: User = Depends(require_user), db: Session = Depends(get_db)):
    focus_count = db.query(func.count(FocusCompletionRecord.id)).join(
        CycleRun, FocusCompletionRecord.run_id == CycleRun.id
    ).filter(CycleRun.user_id == user.id).scalar()
    todo_count = db.query(func.count(FocusTaskRecord.id)).join(
        FocusCompletionRecord,
        FocusTaskRecord.focus_completion_record_id == FocusCompletionRecord.id,
    ).join(CycleRun, FocusCompletionRecord.run_id == CycleRun.id).filter(
        CycleRun.user_id == user.id,
        FocusTaskRecord.task_type == "todo",
    ).scalar()
    nottodo_count = db.query(func.count(FocusTaskRecord.id)).join(
        FocusCompletionRecord,
        FocusTaskRecord.focus_completion_record_id == FocusCompletionRecord.id,
    ).join(CycleRun, FocusCompletionRecord.run_id == CycleRun.id).filter(
        CycleRun.user_id == user.id,
        FocusTaskRecord.task_type == "nottodo",
    ).scalar()
    calendar_rows = db.query(
        func.date(FocusCompletionRecord.recorded_at),
        func.count(FocusCompletionRecord.id),
    ).join(CycleRun, FocusCompletionRecord.run_id == CycleRun.id).filter(
        CycleRun.user_id == user.id
    ).group_by(func.date(FocusCompletionRecord.recorded_at)).all()
    return {
        "focusCount": focus_count or 0,
        "todoCount": todo_count or 0,
        "nottodoCount": nottodo_count or 0,
        "focusCalendar": [
            {"date": row[0], "count": row[1]}
            for row in calendar_rows
        ],
    }


@app.get("/collection")
def collection(user: User = Depends(require_user), db: Session = Depends(get_db)):
    items = db.query(CollectionCycle).filter(CollectionCycle.user_id == user.id).order_by(
        CollectionCycle.collected_at.desc()
    ).all()
    payload = []
    for item in items:
        blueprint = db.query(CycleBlueprint).filter(CycleBlueprint.id == item.cycle_blueprint_id).first()
        payload.append(
            {
                "id": item.id,
                "name": blueprint.name,
                "collectedAt": item.collected_at.isoformat(),
                "focusNodes": [
                    {
                        "photo": serialize_photo(node.photo),
                        "quote": serialize_quote(node.quote),
                    }
                    for node in blueprint.focus_nodes
                ],
            }
        )
    return {"items": payload}

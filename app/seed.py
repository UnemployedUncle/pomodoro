import json
import os

from sqlalchemy.orm import Session

from app.config import DEMO_EMAIL
from app.config import DEMO_NAME
from app.config import SAMPLE_DIR
from app.models import CycleBlueprint
from app.models import CycleBreakEdge
from app.models import CycleFocusNode
from app.models import Photo
from app.models import Quote
from app.models import User
from app.models import UserAssetOwnership
from app.models import UserCycleOwnership


def photo_display_name(filename: str) -> str:
    base_name = os.path.splitext(filename)[0]
    if base_name.endswith("-unsplash"):
        base_name = base_name[: -len("-unsplash")]
    parts = [part for part in base_name.split("-") if part]
    cleaned_parts = []
    for part in parts:
        if any(character.isdigit() for character in part):
            break
        cleaned_parts.append(part.capitalize())
    if not cleaned_parts:
        cleaned_parts = [base_name.replace("-", " ").title()]
    return " ".join(cleaned_parts)


def seed_reference_data(db: Session):
    photo_filenames = sorted(
        [name for name in os.listdir(SAMPLE_DIR) if name.lower().endswith(".jpg")]
    )
    quote_path = os.path.join(SAMPLE_DIR, "quote.json")
    with open(quote_path, "r", encoding="utf-8") as handle:
        quote_payload = json.load(handle)

    photo_records = []
    for filename in photo_filenames:
        display_name = photo_display_name(filename)
        photo = db.query(Photo).filter(Photo.storage_key == filename).first()
        if not photo:
            photo = Photo(
                origin="sample",
                storage_key=filename,
                source_label=display_name,
                source_url="https://unsplash.com",
            )
            db.add(photo)
            db.flush()
        elif photo.source_label != display_name:
            photo.source_label = display_name
        photo_records.append(photo)

    quote_records = []
    for item in quote_payload.get("quotes", [])[:8]:
        quote = db.query(Quote).filter(
            Quote.origin == "sample",
            Quote.text == item["quote"],
            Quote.author_name == item["speaker"],
        ).first()
        if not quote:
            quote = Quote(
                origin="sample",
                text=item["quote"],
                author_name=item["speaker"],
                category=item.get("category"),
            )
            db.add(quote)
            db.flush()
        quote_records.append(quote)

    cycles = [
        ("sample cycle 1", photo_records[:4], quote_records[:4], True, False),
        ("sample cycle 2", photo_records[4:8], quote_records[4:8], False, True),
    ]

    for name, photos, quotes, owned_by_default, trial_available in cycles:
        blueprint = db.query(CycleBlueprint).filter(CycleBlueprint.name == name).first()
        if blueprint:
            continue
        blueprint = CycleBlueprint(
            name=name,
            mode="sample",
            is_owned_by_default=owned_by_default,
            is_trial_available=trial_available,
            is_editable_when_unowned=False,
        )
        db.add(blueprint)
        db.flush()
        for index, (photo, quote) in enumerate(zip(photos, quotes), start=1):
            db.add(
                CycleFocusNode(
                    cycle_blueprint_id=blueprint.id,
                    node_order=index,
                    focus_duration_seconds=25,
                    photo_id=photo.id,
                    quote_id=quote.id,
                )
            )
            if index < len(photos):
                db.add(
                    CycleBreakEdge(
                        cycle_blueprint_id=blueprint.id,
                        from_node_order=index,
                        to_node_order=index + 1,
                        break_duration_seconds=5,
                    )
                )
        db.flush()
    db.commit()


def ensure_user_defaults(db: Session, user: User):
    seed_reference_data(db)
    owned_cycle = db.query(CycleBlueprint).filter(CycleBlueprint.is_owned_by_default.is_(True)).all()
    for blueprint in owned_cycle:
        existing = db.query(UserCycleOwnership).filter(
            UserCycleOwnership.user_id == user.id,
            UserCycleOwnership.cycle_blueprint_id == blueprint.id,
        ).first()
        if not existing:
            db.add(
                UserCycleOwnership(
                    user_id=user.id,
                    cycle_blueprint_id=blueprint.id,
                    ownership_source="default_cycle",
                )
            )
        for node in blueprint.focus_nodes:
            grant_asset_if_missing(db, user.id, "photo", node.photo_id, "default_cycle")
            grant_asset_if_missing(db, user.id, "quote", node.quote_id, "default_cycle")
    db.commit()


def grant_asset_if_missing(db: Session, user_id: int, asset_type: str, asset_id: int, source: str):
    existing = db.query(UserAssetOwnership).filter(
        UserAssetOwnership.user_id == user_id,
        UserAssetOwnership.asset_type == asset_type,
        UserAssetOwnership.asset_id == asset_id,
    ).first()
    if not existing:
        db.add(
            UserAssetOwnership(
                user_id=user_id,
                asset_type=asset_type,
                asset_id=asset_id,
                ownership_source=source,
            )
        )


def get_or_create_demo_user(db: Session):
    user = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if user:
        ensure_user_defaults(db, user)
        return user
    user = User(email=DEMO_EMAIL, nickname=DEMO_NAME)
    db.add(user)
    db.flush()
    ensure_user_defaults(db, user)
    return user

from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow():
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    nickname = Column(String(255), nullable=False)
    profile_image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    last_login_at = Column(DateTime, default=utcnow, nullable=False)


class AuthAccount(Base):
    __tablename__ = "auth_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), unique=True, nullable=False)
    provider_email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    origin = Column(String(50), nullable=False)
    storage_key = Column(String(500), nullable=False)
    source_label = Column(String(255), nullable=False)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    origin = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    author_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)


class UserAssetOwnership(Base):
    __tablename__ = "user_asset_ownerships"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    asset_type = Column(String(50), nullable=False)
    asset_id = Column(Integer, nullable=False)
    ownership_source = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)


class UserCycleOwnership(Base):
    __tablename__ = "user_cycle_ownerships"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cycle_blueprint_id = Column(Integer, ForeignKey("cycle_blueprints.id"), nullable=False)
    ownership_source = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)


class CycleBlueprint(Base):
    __tablename__ = "cycle_blueprints"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    mode = Column(String(50), nullable=False)
    is_owned_by_default = Column(Boolean, default=False, nullable=False)
    is_trial_available = Column(Boolean, default=False, nullable=False)
    is_editable_when_unowned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    focus_nodes = relationship(
        "CycleFocusNode",
        back_populates="cycle_blueprint",
        cascade="all, delete-orphan",
        order_by="CycleFocusNode.node_order",
    )
    break_edges = relationship(
        "CycleBreakEdge",
        back_populates="cycle_blueprint",
        cascade="all, delete-orphan",
        order_by="CycleBreakEdge.from_node_order",
    )


class CycleFocusNode(Base):
    __tablename__ = "cycle_focus_nodes"

    id = Column(Integer, primary_key=True)
    cycle_blueprint_id = Column(Integer, ForeignKey("cycle_blueprints.id"), nullable=False)
    node_order = Column(Integer, nullable=False)
    focus_duration_seconds = Column(Integer, nullable=False)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)

    cycle_blueprint = relationship("CycleBlueprint", back_populates="focus_nodes")
    photo = relationship("Photo")
    quote = relationship("Quote")


class CycleBreakEdge(Base):
    __tablename__ = "cycle_break_edges"

    id = Column(Integer, primary_key=True)
    cycle_blueprint_id = Column(Integer, ForeignKey("cycle_blueprints.id"), nullable=False)
    from_node_order = Column(Integer, nullable=False)
    to_node_order = Column(Integer, nullable=False)
    break_duration_seconds = Column(Integer, nullable=False)

    cycle_blueprint = relationship("CycleBlueprint", back_populates="break_edges")


class CycleRun(Base):
    __tablename__ = "cycle_runs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cycle_blueprint_id = Column(Integer, ForeignKey("cycle_blueprints.id"), nullable=False)
    cycle_mode = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    completed_focus_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    cycle_blueprint = relationship("CycleBlueprint")


class FocusCompletionRecord(Base):
    __tablename__ = "focus_completion_records"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("cycle_runs.id"), nullable=False)
    focus_order = Column(Integer, nullable=False)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    focus_duration_seconds = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=utcnow, nullable=False)


class FocusTaskRecord(Base):
    __tablename__ = "focus_task_records"

    id = Column(Integer, primary_key=True)
    focus_completion_record_id = Column(Integer, ForeignKey("focus_completion_records.id"), nullable=False)
    task_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)


class RewardEntitlement(Base):
    __tablename__ = "reward_entitlements"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("cycle_runs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), nullable=False)
    allowed_actions_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    used_at = Column(DateTime, nullable=True)


class CollectionCycle(Base):
    __tablename__ = "collection_cycles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cycle_blueprint_id = Column(Integer, ForeignKey("cycle_blueprints.id"), nullable=False)
    source_run_id = Column(Integer, ForeignKey("cycle_runs.id"), nullable=False)
    collected_at = Column(DateTime, default=utcnow, nullable=False)

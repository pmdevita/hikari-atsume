"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}
add_models: dict[str, str] = ${repr(config.add_models if config.add_models else {})}
remove_models: dict[str, str] = ${repr(config.remove_models if config.remove_models else {})}
rename_models: dict[str, str] = ${repr(config.rename_models if config.rename_models else {})}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}

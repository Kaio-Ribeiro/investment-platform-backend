"""Fix null created_by values

Revision ID: c9f4163ff49a
Revises: 12ae86f2277c
Create Date: 2025-10-02 10:20:41.704031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9f4163ff49a'
down_revision: Union[str, Sequence[str], None] = '12ae86f2277c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update NULL created_by values to 'system'
    op.execute("UPDATE clients SET created_by = 'system' WHERE created_by IS NULL")
    
    # Update NULL status values to 'active'
    op.execute("UPDATE clients SET status = 'active' WHERE status IS NULL")
    
    # Update NULL investment_profile values to 'not_defined'
    op.execute("UPDATE clients SET investment_profile = 'not_defined' WHERE investment_profile IS NULL")
    
    # Update NULL investment_experience values to 'beginner'
    op.execute("UPDATE clients SET investment_experience = 'beginner' WHERE investment_experience IS NULL")
    
    # Update NULL country values to 'Brasil'
    op.execute("UPDATE clients SET country = 'Brasil' WHERE country IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # No need to revert these fixes
    pass

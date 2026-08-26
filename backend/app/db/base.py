# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base
from app.models.domain.user import User
from app.models.domain.farm import Farm
from app.models.domain.field import Field
from app.models.domain.crop_cycle import CropCycle
from app.models.domain.observation import Observation
from app.models.domain.prediction import Prediction
from app.models.domain.recommendation import Recommendation
from app.models.domain.simulation import Simulation
from app.models.domain.agent_run import AgentRun

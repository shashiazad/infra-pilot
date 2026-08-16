import uuid

from app.llm.groq import create_groq_model
from app.llm.prompts import INVESTIGATION_PROMPT
from app.repositories.incident_repository import IncidentRepository
from app.schemas.investigation import InvestigationResult


class InvestigationService:
    async def investigate(
        self,
        incident_id: uuid.UUID,
        repository: IncidentRepository,
    ) -> InvestigationResult | None:

        incident = await repository.get_by_id(incident_id)

        if incident is None:
            return None

        prompt = INVESTIGATION_PROMPT.format(
            title=incident.title,
            description=incident.description,
            service=incident.service,
            severity=incident.severity,
            status=incident.status,
        )

        model = create_groq_model()

        result = await model.ainvoke(prompt)

        return result

from enum import Enum

from pydantic import BaseModel, Field


class Reaction(Enum):
    REPLAN = "replan"
    MAINTAIN_PLANS = "maintain_plans"


class LLMReactionResponse(BaseModel):
    reaction: Reaction = Field(
        description="The reaction to the message. Must be either 'replan' or 'maintain_plans'. Do not provide anything else."
    )

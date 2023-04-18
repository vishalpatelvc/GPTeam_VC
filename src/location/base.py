import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


# from ..agent.base import Agent
from ..utils.database import supabase
from ..utils.parameters import DEFAULT_WORLD_ID
from ..world.base import Event

class ActionType(Enum):
    MOVE = "move"
    MESSAGE = "message"


# class AgentAction(BaseModel):
#     type: ActionType
#     agent: Agent
#     step: int
#     location: Optional["Location"] = None

#     def __init__(self, agent: Agent, step: int, location: Optional["Location"] = None):
#         super().__init__(agent=agent, step=step, location=location)


class Location(BaseModel):
    id: UUID
    name: str
    description: str
    channel_id: str
    allowed_agent_ids: list[UUID] = []
    world_id: UUID = None

    def __init__(
        self,
        name: str,
        description: str,
        channel_id: int,
        allowed_agent_ids: list[UUID] = None,
        id: Optional[UUID] = None,
        world_id: UUID = None,
    ):
        if id is None:
            id = uuid4()

        if world_id is None:
            world_id = DEFAULT_WORLD_ID

        if allowed_agent_ids is None:
            allowed_agent_ids = []

        super().__init__(
            id=id,
            world_id=world_id,
            name=name,
            description=description,
            channel_id=channel_id,
            allowed_agent_ids=allowed_agent_ids,
        )

    def db_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "channel_id": self.channel_id,
            "allowed_agent_ids": [str(agent_id) for agent_id in self.allowed_agent_ids],
            "world_id": str(self.world_id),
        }

    @classmethod
    def from_id(cls, id: UUID):
        data, count = (
            supabase.table("Locations").select("*").eq("id", str(id)).execute()
        )
        return cls(**data[1][0])

    @classmethod
    def from_name(cls, name: str):
        data, count = supabase.table("Locations").select("*").eq("name", name).execute()
        return cls(**data[1][0])

    @property
    def local_agent_ids(self) -> list[UUID]:
        """Get IDs of agents who are currently in this location."""
        data, count = (
            supabase.table("Agents").select("id").eq("location_id", self.id).execute()
        )
        print(data)
        return [agent["id"] for agent in data[1]]

    @property
    def current_step(self) -> int:
        """Get the current step in this location."""
        data, count = (
            supabase.table("Worlds")
            .select("current_step")
            .eq("id", str(self.world_id))
            .execute()
        )
        return data[1][0]["current_step"]

    def pull_events(self) -> list[Event]:
        """Get current step events from the events table that have happened in this location."""
        data, count = (
            supabase.table("Events")
            .select("*")
            .eq("location_id", str(self.id))
            .eq("step", self.current_step)
            .execute()
        )
        return [Event(**event) for event in data[1]]


class EventType(Enum):
    NON_MESSAGE = "non_message"
    MESSAGE = "message"


class DiscordMessage(BaseModel):
    content: str
    location: Location
    timestamp: datetime.datetime


class Event(BaseModel):
    id: UUID
    timestamp: Optional[datetime.datetime] = None
    step: int
    type: EventType
    description: str
    location_id: UUID
    witness_ids: list[UUID]

    def __init__(
        self,
        type: EventType,
        description: str,
        location_id: UUID,
        witness_ids: list[UUID],
        timestamp: Optional[datetime.datetime] = None,
        step: Optional[int] = None,
        id: Optional[UUID] = None,
    ):
        if id is None:
            id = uuid4()

        if timestamp is None and step is None:
            raise ValueError("Either timestamp or step must be provided")

        if timestamp:
            # calculate step from timestamp
            pass

        super().__init__(
            id=id,
            type=type,
            description=description,
            timestamp=timestamp,
            step=step,
            location_id=location_id,
            witness_ids=witness_ids,
        )

    def db_dict(self):
        return {
            "id": str(self.id),
            "timestamp": str(self.timestamp),
            "step": self.step,
            "type": self.type.value,
            "description": self.description,
            "location_id": str(self.location_id),
            "witness_ids": [str(witness_id) for witness_id in self.witness_ids],
        }

    @staticmethod
    def from_discord_message(message: DiscordMessage, witnesses: list[UUID]) -> "Event":
        # parse user provided message into an event
        # witnesses are all agents who were in the same location as the message
        pass

    # @staticmethod
    # def from_agent_action(action: AgentAction, witnesses: list[UUID]) -> "Event":
    #     # parse agent action into an event
    #     pass
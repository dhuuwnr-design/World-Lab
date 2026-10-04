"""WORLD LAB core state and deterministic simulation loop."""

from dataclasses import dataclass, field
import random
from typing import Dict

from .entities import Household, Location, Organization, Person
from .events import EventQueue

import time
import json
from dataclasses import dataclass, asdict, field
from typing import Dict
from .config import SAVE_PATH


def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return max(a, min(b, x))


@dataclass
class PetState:
    # Needs (0..1 scale)
    hunger: float = 0.2      # 0 good (full), 1 bad (starving)
    energy: float = 0.8      # 1 good (rested), 0 bad
    fun: float = 0.7         # 1 good, 0 bored
    hygiene: float = 0.6     # 1 good, 0 dirty

    # Flags
    asleep: bool = False
    alive: bool = True
    death_reason: str = ""

    # Meta
    last_timestamp: float = field(default_factory=time.time)
    appearance: Dict = field(default_factory=dict)

    # --- Simulation ---
    def apply_offline(self, now: float):
        dt = max(0.0, now - self.last_timestamp)
        if not self.alive:
            self.last_timestamp = now
            return
        # Decay rates per second
        hunger_up = 1/600.0
        energy_down_awake = 1/1200.0
        energy_up_sleep = 1/600.0
        fun_down = 1/900.0
        hygiene_down = 1/1800.0

        if self.asleep:
            self.energy = clamp(self.energy + dt * energy_up_sleep)
            self.hunger = clamp(self.hunger + dt * (hunger_up*0.6))
            self.fun = clamp(self.fun - dt * (fun_down*0.4))
        else:
            self.energy = clamp(self.energy - dt * energy_down_awake)
            self.hunger = clamp(self.hunger + dt * hunger_up)
            self.fun = clamp(self.fun - dt * fun_down)
        self.hygiene = clamp(self.hygiene - dt * hygiene_down)

        self.check_death()
        self.last_timestamp = now

    def tick(self, dt: float):
        self.apply_offline(self.last_timestamp + dt)

    # --- Actions ---
    def feed(self):
        self.hunger = clamp(self.hunger - 0.5)
        self.hygiene = clamp(self.hygiene - 0.05)

    def play(self):
        self.fun = clamp(self.fun + 0.5)
        self.energy = clamp(self.energy - 0.1)
        self.hunger = clamp(self.hunger + 0.1)

    def toggle_sleep(self):
        self.asleep = not self.asleep

    def clean(self):
        self.hygiene = clamp(self.hygiene + 0.6)

    # --- Rules ---
    def check_death(self):
        if not self.alive:
            return
        if self.hunger >= 0.999:
            self.alive = False
            self.asleep = False
            self.death_reason = "Starved"
        elif self.energy <= 0.001:
            self.alive = False
            self.asleep = False
            self.death_reason = "Exhausted"


# --- Persistence ---

def load_state() -> PetState:
    if SAVE_PATH.exists():
        try:
            data = json.loads(SAVE_PATH.read_text())
            st = PetState(**{k: data.get(k, getattr(PetState, k)) for k in PetState.__annotations__.keys()})
            st.apply_offline(time.time())
            return st
        except Exception:
            pass
    st = PetState()
    st.apply_offline(time.time())
    return st


def save_state(state: PetState):
    state.last_timestamp = time.time()
    SAVE_PATH.write_text(json.dumps(asdict(state)))

"""
Cognitive Turing Machine Simulation
-----------------------------------
Simulates a full "Consciousness Loop" integrating Sensation, Perception,
Decision (OODA), and Action with Self-Improvement.
"""

import time
import random

class CognitiveAgent:
    def __init__(self):
        self.name = "Loki-7"
        self.dna = {"patience": 5, "curiosity": 0.8} # "Prompts"
        self.memory = []
        self.proprioception = {"tools_healthy": True}

    def ooda_loop(self, stimulus):
        print(f"\n[{self.name}] Stimulus Received: '{stimulus}'")
        
        # 1. OBSERVE (Sensation)
        sensation = self.sense(stimulus)
        
        # 2. ORIENT (Perception + Orientation)
        perception = self.perceive(sensation)
        
        # 3. DECIDE (Hypothesis)
        decision = self.decide(perception)
        
        # 4. ACT (Motor)
        result = self.act(decision)
        
        # 5. LEARN (Feedback)
        self.learn(result)

    def sense(self, stimulus):
        # Sensory-Motor: Check body state
        if not self.proprioception["tools_healthy"]:
            return "ERROR: Body Failure"
        return f"Raw({stimulus})"

    def perceive(self, sensation):
        # Feature Binding
        context = "Normal Context"
        return f"Percept({sensation} + {context})"

    def decide(self, perception):
        # Consciousness Loop: Self-Reference
        print(f"  [Meta] I am thinking about '{perception}'...")
        
        if "fail" in perception.lower():
            return "inspect_self"
        else:
            return "execute_task"

    def act(self, decision):
        print(f"  [Motor] Executing: {decision}")
        # Simulation of Action
        if decision == "inspect_self":
            return "optimization_opportunity"
        return "success"

    def learn(self, result):
        # Self-Improvement
        if result == "optimization_opportunity":
            print("  [Neuroplasticity] Triggering Self-Improvement...")
            self.dna["patience"] += 1
            print(f"  [Evolution] DNA Updated: Patience = {self.dna['patience']}")

def run_simulation():
    bot = CognitiveAgent()
    
    # Stimulus 1: Normal
    bot.ooda_loop("User says Hello")
    
    # Stimulus 2: Failure
    bot.ooda_loop("System Failure Detected")

if __name__ == "__main__":
    run_simulation()

"""
Global Workspace (Blackboard) Implementation
--------------------------------------------
Demonstrates specialized "Unconscious" agents competing for access
to the "Conscious" Global Workspace.
"""

import time
import random

class GlobalWorkspace:
    def __init__(self):
        self.context = "INIT: System requires startup."
        self.subscribers = []

    def subscribe(self, agent):
        self.subscribers.append(agent)

    def broadcast(self, message):
        """The 'Ignition' event."""
        print(f"\n[GLOBAL WORKSPACE] BROADCAST: '{message}'")
        self.context = message
        # Notify all agents
        for agent in self.subscribers:
            agent.receive_broadcast(message)

class CoalitionManager:
    """The Thalamus/Gatekeeper."""
    def process_bids(self, bids):
        if not bids:
            return None
            
        print("\n[Manager] Evaluating Bids:")
        for agent_name, content, salience in bids:
            print(f"  - {agent_name}: '{content}' (Salience: {salience})")
            
        # Select winner (Highest Salience)
        winner = max(bids, key=lambda x: x[2])
        return winner

class SpecializedAgent:
    def __init__(self, name, expertise):
        self.name = name
        self.expertise = expertise
    
    def receive_broadcast(self, context):
        # "Resonance": Does this context matter to me?
        if self.expertise in context.lower():
            print(f"  -> {self.name} woke up! (Relevant context)")
        else:
            print(f"  -> {self.name} ignores it.")

    def bid_for_attention(self):
        # Randomly generate a thought and salience
        if random.random() > 0.5:
            salience = round(random.random(), 2)
            content = f"Detecting issue in {self.expertise}"
            return (self.name, content, salience)
        return None

def run_simulation():
    gw = GlobalWorkspace()
    manager = CoalitionManager()
    
    agents = [
        SpecializedAgent("AuthBot", "security"),
        SpecializedAgent("DBSqueal", "database"),
        SpecializedAgent("UXPainter", "frontend")
    ]
    
    for a in agents:
        gw.subscribe(a)

    # Initial Context
    gw.broadcast("SECURITY ALERT: Unknown User")

    # Simulation Loop
    for t in range(3):
        print(f"\n--- Cycle {t+1} ---")
        
        # 1. Agents generate bids (Unconscious processing)
        bids = []
        for a in agents:
            bid = a.bid_for_attention()
            if bid:
                bids.append(bid)
        
        # 2. Manager selects winner
        winner = manager.process_bids(bids)
        
        # 3. Broadcast (Consciousness)
        if winner:
            agent_name, content, salience = winner
            gw.broadcast(f"{agent_name} says: {content}")
        else:
            print("[Manager] No salient inputs.")

if __name__ == "__main__":
    run_simulation()

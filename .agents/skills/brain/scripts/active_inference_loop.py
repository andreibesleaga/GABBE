"""
Active Inference Agent Loop Implementation
------------------------------------------
This script demonstrates a minimal working example of an Active Inference
agent that minimizes prediction error (Surprise).

Concepts:
- Generative Model: Predicts the next state.
- Surprise: Divergence between Prediction and Observation.
- Active Inference: Action to change the world to match prediction.
"""

import random

class Environment:
    """A simple environment that returns a state (0-10)."""
    def __init__(self):
        self.state = 5
    
    def step(self, action):
        # Action adjusts state
        if action == "increase":
            self.state += 1
        elif action == "decrease":
            self.state -= 1
        
        # Add some random noise (uncertainty)
        noise = random.choice([-1, 0, 1])
        return self.state + noise

class ActiveInferenceAgent:
    def __init__(self, target_state=5):
        self.target_state = target_state
        self.internal_model_state = target_state # Expectation matches goal initially
    
    def predict(self):
        """Generative Model: Predicts what we SHOULD see."""
        return self.internal_model_state

    def compare(self, observation):
        """Calculate Surprise (Prediction Error)."""
        return abs(self.predict() - observation)

    def resolve(self, surprise, observation):
        """Minimize Free Energy."""
        print(f"  Surprise: {surprise}")
        
        if surprise == 0:
            return "wait" # No action needed
        
        # In this simple model, we assume the World is wrong (Active Inference)
        # We act to force the world state towards our prediction/target.
        if observation < self.predict():
            return "increase"
        else:
            return "decrease"

def run_simulation():
    env = Environment()
    agent = ActiveInferenceAgent(target_state=7) # Agent wants state to be 7

    print(f"Goal: Agent wants state {agent.target_state}")
    
    for t in range(5):
        print(f"\n--- Step {t+1} ---")
        
        # 1. Predict
        expectation = agent.predict()
        print(f"Expectation: {expectation}")
        
        # 2. Observe (Initial look)
        observation = env.step("wait") # Just looking
        print(f"Observation: {observation}")
        
        # 3. Compare
        surprise = agent.compare(observation)
        
        # 4. Resolve (Active Inference)
        action = agent.resolve(surprise, observation)
        print(f"Action: {action}")
        
        # Apply action for next step
        if action != "wait":
            env.step(action)

if __name__ == "__main__":
    run_simulation()

1. Phase 1: Real-World Data & Dynamic Graph Routing (~30–40 hours)
OSM Parsing & Coordinate Projection: Translating raw GPS coordinates from OpenStreetMap into a clean 2D Pygame rendering grid and building a graph network (osmnx/networkx) is tricky. Dealing with road curvatures, intersections, and multi-lane mapping takes about 15–20 hours.

Dynamic Congestion Routing (A):* Upgrading static shortest-path to a live, density-aware routing algorithm where cars continuously recalculate optimal paths based on traffic jams takes 15–20 hours.

2. Phase 2: AI & Reinforcement Learning Signals (~40–50 hours)
RL Environment Wrapper (Gymnasium): Structuring your traffic simulation into a standard ML environment (defining precise State spaces, Action spaces, and Reward functions) takes 15–20 hours.

Training & Tuning the Agent (DQN / PPO): Writing the training loop (using PyTorch or Stable-Baselines3), letting the agent train over thousands of simulated episodes, and debugging why your traffic signals are initially causing massive gridlock takes 25–30 hours.

3. Phase 3: Research Dashboard & Empirical Whitepaper (~30–50 hours)
Live Analytics & Visualization Panel: Building real-time graph rendering (throughput over time, carbon emission estimates, queue delay heatmaps) takes 15–20 hours.

Experimentation & Documentation: Running benchmark tests (comparing fixed timers vs. your RL agent across 10 different traffic scenarios) and writing a formal technical whitepaper or documentation takes 15–30 hours.
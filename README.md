📦 Inventory Restocking Optimization using Dynamic Programming

This project is a smart inventory management system that determines the optimal restocking strategy using Dynamic Programming (DP). It helps businesses minimize total costs by balancing two critical factors: frequent restocking (which increases ordering costs) and infrequent restocking (which may lead to stockouts and lost sales).

🚀 Overview

Efficient inventory management is essential for any business dealing with physical goods. This project models the restocking problem as an optimization task and applies Dynamic Programming to find the most cost-effective strategy over a given time period.

The application is built using Python and features an interactive user interface developed with the Streamlit library, making it easy to visualize and experiment with different inventory scenarios.

🧠 Key Features
📊 Dynamic Programming-based optimization to minimize total cost
📦 Handles inventory holding costs, ordering costs, and shortage costs
⚡ Allows users to input demand patterns and cost parameters
📈 Provides clear output of optimal restocking decisions
🖥️ Interactive UI built with Streamlit for real-time simulation
🛠️ Tech Stack
Language: Python
Frontend/UI: Streamlit
Core Concept: Dynamic Programming
📌 Problem Statement

The goal is to determine when and how much inventory to restock over a fixed time horizon such that the total cost is minimized.

The cost includes:

Ordering Cost (placing orders frequently)
Holding Cost (storing excess inventory)
Shortage Cost (running out of stock)

Dynamic Programming is used to break this problem into smaller subproblems and compute the optimal solution efficiently.

💡 How It Works
The user inputs:
Demand for each time period
Ordering cost
Holding cost
Shortage/penalty cost
The system:
Evaluates all possible restocking decisions
Uses DP to store intermediate results
Finds the minimum-cost strategy
The output:
Optimal restocking schedule
Minimum total cost
🎯 Use Cases
Retail inventory management
Warehouse optimization
Supply chain planning
Small business stock management
📷 Demo

You can run the Streamlit app locally:

streamlit run app.py
📚 Learning Outcomes
Understanding of Dynamic Programming in real-world problems
Optimization techniques for cost minimization
Building interactive data-driven apps using Streamlit

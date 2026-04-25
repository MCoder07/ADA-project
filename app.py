"""
app.py  — Main Entry Point
Run with:  streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd

from utils.styles    import CUSTOM_CSS
from utils.dp_solver import (run_dp, reconstruct_plan,
                              naive_greedy_cost, build_full_day_table)
from components.sidebar       import render_sidebar
from components.ui_components import hero_banner, metric_cards, restock_timeline

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Inventory DP Optimizer",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
inputs = render_sidebar()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(hero_banner(), unsafe_allow_html=True)

# ── BEFORE CALCULATE ──────────────────────────────────────────────────────────
if not inputs["calculate"]:
    st.info(
        "  **Fill in the sidebar inputs**, then click "
        "**\"Calculate Optimal Restock Plan\"** to get your results.",
        icon="📦",
    )
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.markdown("####  What This Solves")
        st.markdown(
            "Given daily product demand over **N days**, find the cheapest "
            "restocking schedule — deciding **when** to order and **how much** "
            "each time to minimize total cost."
        )
    with col2:
        st.markdown("####  Cost Components")
        st.markdown(
            "- **Ordering Cost** — fixed fee every time you restock  \n"
            "- **Holding Cost** — per unit, per day stored  \n"
            "- **Goal** — minimize their combined total"
        )
    with col3:
        st.markdown("####  Algorithm")
        st.markdown(
            "**Dynamic Programming (Tabulation)**  \n"
            "- `dp[i]` = min cost from day i → end  \n"
            "- Time complexity: **O(N²)**  \n"
            "- Guarantees global optimum"
        )

# ── AFTER CALCULATE ───────────────────────────────────────────────────────────
else:
    if inputs["error"]:
        st.error(inputs["error"])
        st.stop()

    demands       = inputs["demands"]
    ordering_cost = inputs["ordering_cost"]
    holding_cost  = inputs["holding_cost"]
    n_days        = inputs["n_days"]

    # Run DP
    dp, next_order, table_rows = run_dp(demands, ordering_cost, holding_cost)
    plan             = reconstruct_plan(demands, next_order)
    naive            = naive_greedy_cost(demands, ordering_cost)
    dp_cost          = round(dp[0], 2)
    savings          = round(naive - dp_cost, 2)
    savings_pct      = round((savings / naive) * 100, 1) if naive > 0 else 0
    restock_days_set = {p["Order Day"] for p in plan}

    # ── A. Sweet Spot Total Cost ───────────────────────────────────────────────
    st.markdown(metric_cards(dp_cost, naive, savings, len(plan)),
                unsafe_allow_html=True)

    # ── B. Order Schedule ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("###  B.  Order Schedule")
    st.caption("Exactly when to buy and how much — day by day.")

    # Narrative bullets (e.g. "Day 1: Order 35 units (for Days 1–3)")
    for p in plan:
        st.markdown(
            f"🔵 **Day {p['Order Day']}** — Order **{p['Order Qty (units)']} units**"
            f"&nbsp;&nbsp;*(covers {p['Covers Days']})*"
        )

    st.markdown("")

    # Full per-day table  (Planning Day | Demand | Action | Order Qty | Inventory)
    day_rows = build_full_day_table(demands, next_order)
    df_days  = pd.DataFrame(day_rows)

    # Style: highlight ORDER rows in the Action column
    def highlight_action(val):
        if val == "ORDER":
            return "background-color: rgba(88,166,255,0.18); color: #58a6ff; font-weight: bold;"
        return "color: #8b949e;"

    styled = (
        df_days.style
        .applymap(highlight_action, subset=["Action"])
        .format({"Order Quantity": lambda v: str(v) if v > 0 else "—",
                 "Inventory (End)": "{}"})
        .set_properties(**{"text-align": "center"})
        .set_table_styles([
            {"selector": "th", "props": [("text-align", "center"),
                                          ("background-color", "#1c2130"),
                                          ("color", "#58a6ff")]}
        ])
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── C. Greedy vs DP Comparison ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### C.  Greedy vs DP — Cost Comparison")

    col_g, col_dp, col_save = st.columns(3, gap="large")

    with col_g:
        st.markdown(
            f"""
            <div style='background:rgba(210,153,34,.1);border:1px solid rgba(210,153,34,.4);
                        border-radius:10px;padding:1rem 1.2rem;'>
                <div style='font-size:.75rem;color:#d29922;text-transform:uppercase;
                            letter-spacing:.06em;margin-bottom:.4rem;font-family:Space Mono;'>
                    🐢 Greedy Approach
                </div>
                <div style='font-family:Space Mono;font-size:1.6rem;
                            font-weight:700;color:#d29922;'>₹{naive}</div>
                <div style='font-size:.82rem;color:#8b949e;margin-top:.5rem;'>
                    Orders every single day ({n_days} orders)<br>
                    No holding cost, maximum ordering cost
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_dp:
        st.markdown(
            f"""
            <div style='background:rgba(63,185,80,.1);border:1px solid rgba(63,185,80,.4);
                        border-radius:10px;padding:1rem 1.2rem;'>
                <div style='font-size:.75rem;color:#3fb950;text-transform:uppercase;
                            letter-spacing:.06em;margin-bottom:.4rem;font-family:Space Mono;'>
                    DP Optimized
                </div>
                <div style='font-family:Space Mono;font-size:1.6rem;
                            font-weight:700;color:#3fb950;'>₹{dp_cost}</div>
                <div style='font-size:.82rem;color:#8b949e;margin-top:.5rem;'>
                    {len(plan)} smart orders<br>
                    Balances ordering + holding cost
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_save:
        st.markdown(
            f"""
            <div style='background:rgba(88,166,255,.1);border:1px solid rgba(88,166,255,.4);
                        border-radius:10px;padding:1rem 1.2rem;'>
                <div style='font-size:.75rem;color:#58a6ff;text-transform:uppercase;
                            letter-spacing:.06em;margin-bottom:.4rem;font-family:Space Mono;'>
                     You Save
                </div>
                <div style='font-family:Space Mono;font-size:1.6rem;
                            font-weight:700;color:#58a6ff;'>₹{savings}</div>
                <div style='font-size:.82rem;color:#8b949e;margin-top:.5rem;'>
                    <b style='color:#58a6ff;'>{savings_pct}% cheaper</b> with DP<br>
                    vs naive greedy strategy
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Comparison bar
    st.markdown("<br>", unsafe_allow_html=True)
    if naive > 0:
        dp_pct    = int((dp_cost / naive) * 100)
        naive_pct = 100
        st.markdown(
            f"""
            <div style='margin-top:.5rem;'>
                <div style='font-size:.78rem;color:#8b949e;margin-bottom:.3rem;'>
                    Cost comparison (relative bar)
                </div>
                <div style='display:flex;align-items:center;gap:.6rem;margin-bottom:.4rem;'>
                    <span style='font-size:.78rem;color:#d29922;width:55px;'>Greedy</span>
                    <div style='flex:1;background:#21262d;border-radius:4px;height:20px;'>
                        <div style='width:{naive_pct}%;background:#d29922;height:100%;
                                    border-radius:4px;'></div>
                    </div>
                    <span style='font-size:.78rem;color:#d29922;'>₹{naive}</span>
                </div>
                <div style='display:flex;align-items:center;gap:.6rem;'>
                    <span style='font-size:.78rem;color:#3fb950;width:55px;'>DP</span>
                    <div style='flex:1;background:#21262d;border-radius:4px;height:20px;'>
                        <div style='width:{dp_pct}%;background:#3fb950;height:100%;
                                    border-radius:4px;'></div>
                    </div>
                    <span style='font-size:.78rem;color:#3fb950;'>₹{dp_cost}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Timeline ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(restock_timeline(n_days, restock_days_set), unsafe_allow_html=True)

    # ── DP computation table (optional) ───────────────────────────────────────
    with st.expander(" View Full DP Computation Table"):
        st.caption(
            "Every (i, j) pair evaluated. For each starting day i, "
            "all possible next-restock days j are tried and the cheapest is kept."
        )
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;color:#30363d;font-size:0.74rem;"
    "font-family:Space Mono;margin-top:2.5rem;padding-top:1rem;"
    "border-top:1px solid #21262d;'>"
    "Cost-Optimized Inventory Management · Dynamic Programming · Python 3 + Streamlit"
    "</div>",
    unsafe_allow_html=True,
)

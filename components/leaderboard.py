"""Leaderboard component."""

import streamlit as st
from utils.helpers import get_level_for_xp


def render_leaderboard(data: list[dict], show_team: bool = False):
    """Render leaderboard table."""
    if not data:
        st.info("Zatiaľ žiadne dáta pre leaderboard.")
        return

    st.markdown("""
    <style>
    .lb-table { width: 100%; border-collapse: collapse; }
    .lb-table th { background: #1E293B; color: #94A3B8; font-size: 0.75rem; text-transform: uppercase;
                   padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #334155; }
    .lb-table td { padding: 0.75rem 1rem; color: #E2E8F0; border-bottom: 1px solid #1E293B;
                   font-size: 0.85rem; }
    .lb-row:hover { background: #1E293B; }
    .lb-rank { font-weight: 700; font-size: 1rem; }
    .lb-rank-1 { color: #FFD700; }
    .lb-rank-2 { color: #C0C0C0; }
    .lb-rank-3 { color: #CD7F32; }
    </style>
    """, unsafe_allow_html=True)

    header = "<tr><th>#</th><th>Agent</th><th>Level</th><th>XP</th><th>Avg. skóre</th><th>Sessions</th></tr>"

    rows = ""
    for i, entry in enumerate(data[:10]):
        rank = i + 1
        rank_class = f"lb-rank-{rank}" if rank <= 3 else ""
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        rank_display = medals.get(rank, str(rank))

        _, level_name = get_level_for_xp(entry.get("xp", 0))

        rows += f"""
        <tr class="lb-row">
            <td class="lb-rank {rank_class}">{rank_display}</td>
            <td style="font-weight: 600;">{entry.get('name', '')}</td>
            <td><span style="background: #334155; padding: 0.15rem 0.5rem; border-radius: 12px;
                           font-size: 0.75rem;">Lv.{entry.get('level', 1)} {level_name}</span></td>
            <td>{entry.get('xp', 0):,}</td>
            <td>{entry.get('avg_score', 0):.0f}%</td>
            <td>{entry.get('total_sessions', 0)}</td>
        </tr>
        """

    st.markdown(f'<table class="lb-table">{header}{rows}</table>', unsafe_allow_html=True)

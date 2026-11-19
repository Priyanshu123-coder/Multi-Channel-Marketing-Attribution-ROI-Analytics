"""
Automated PowerPoint Deck Generator for Grito Labs
Generates Marketing_Attribution_Findings.pptx with python-pptx
"""

import os
import json
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECK_DIR = os.path.join(BASE_DIR, "deck")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DECK_DIR, exist_ok=True)

# Corporate Color Palette (Modern Executive Navy / Slate / Emerald)
NAVY_PRIMARY = RGBColor(15, 23, 42)      # #0f172a
BLUE_ACCENT  = RGBColor(37, 99, 235)     # #2563eb
EMERALD_GREEN= RGBColor(16, 185, 129)    # #10b981
SLATE_GRAY   = RGBColor(100, 116, 139)   # #64748b
LIGHT_BG     = RGBColor(248, 250, 252)   # #f8fafc
WHITE        = RGBColor(255, 255, 255)
CARD_BG      = RGBColor(241, 245, 249)   # #f1f5f9
BORDER_COLOR = RGBColor(203, 213, 225)   # #cbd5e1

def add_header(slide, title_text, category_text="GRITO LABS MARKETING ANALYTICS"):
    """Adds a standard executive header to a slide."""
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    # Category / Super-title
    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = BLUE_ACCENT
    
    # Main Slide Title
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = NAVY_PRIMARY

def add_card(slide, left, top, width, height, title, value, subtext="", accent_color=BLUE_ACCENT):
    """Draws a clean metric card."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = CARD_BG
    shape.line.color.rgb = BORDER_COLOR
    shape.line.width = Pt(1)
    
    # Accent bar on top of the card
    accent_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = accent_color
    accent_bar.line.fill.background()
    
    tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), height - Inches(0.25))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_title = tf.paragraphs[0]
    p_title.text = title.upper()
    p_title.font.size = Pt(9)
    p_title.font.bold = True
    p_title.font.color.rgb = SLATE_GRAY
    
    p_val = tf.add_paragraph()
    p_val.text = value
    p_val.font.size = Pt(22)
    p_val.font.bold = True
    p_val.font.color.rgb = NAVY_PRIMARY
    
    if subtext:
        p_sub = tf.add_paragraph()
        p_sub.text = subtext
        p_sub.font.size = Pt(10)
        p_sub.font.color.rgb = EMERALD_GREEN if "+" in subtext or "x" in subtext else SLATE_GRAY

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 Widescreen standard
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide
    
    # Load summary metrics
    with open(os.path.join(DATA_DIR, "summary_metrics.json"), "r") as f:
        metrics = json.load(f)
        
    df_attr = pd.read_csv(os.path.join(DATA_DIR, "attribution_comparison.csv"))
    df_camp = pd.read_csv(os.path.join(DATA_DIR, "campaign_rankings.csv"))
    df_scen = pd.read_csv(os.path.join(DATA_DIR, "budget_scenarios.csv"))
    
    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY_PRIMARY
    bg1.line.fill.background()
    
    tb1 = s1.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(11.0), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "GRITO LABS | MARKETING ANALYTICS ASSESSMENT"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN
    
    p = tf1.add_paragraph()
    p.text = "Multi-Channel Marketing Analytics &\nAttribution Framework"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = WHITE
    
    p = tf1.add_paragraph()
    p.text = "Evaluating Heuristic & Markov Removal Models, Campaign Efficiencies, and Quantitative Budget Optimization"
    p.font.size = Pt(15)
    p.font.color.rgb = SLATE_GRAY
    
    p = tf1.add_paragraph()
    p.text = "Analyst Deliverable | Timeframe: Jan 1 – Sep 30, 2026 | Prepared for Executive Leadership"
    p.font.size = Pt(12)
    p.font.color.rgb = BORDER_COLOR
    
    # =========================================================================
    # SLIDE 2: EXECUTIVE SUMMARY
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Executive Summary: Findings & Commercial Impact", "Strategic Overview")
    
    add_card(s2, Inches(0.8), Inches(1.6), Inches(2.7), Inches(1.5), "Total Ad Spend", f"${metrics['total_spend']:,.0f}", "6 Marketing Channels")
    add_card(s2, Inches(3.8), Inches(1.6), Inches(2.7), Inches(1.5), "Attributed Revenue", f"${metrics['total_revenue']:,.0f}", "4,879 Course Purchases", EMERALD_GREEN)
    add_card(s2, Inches(6.8), Inches(1.6), Inches(2.7), Inches(1.5), "Blended ROAS", f"{metrics['blended_roas']:.2f}x", "Target: 3.0x (+91%)", EMERALD_GREEN)
    add_card(s2, Inches(9.8), Inches(1.6), Inches(2.7), Inches(1.5), "Blended CAC", f"${metrics['blended_cac']:.2f}", "CLV:CAC = 5.37x", BLUE_ACCENT)
    
    # 3 Bullet Key Findings Cards
    findings = [
        ("Misleading Heuristics", "Last-touch attribution allocates $1.54M (36%) to Email and over-credits bottom-funnel touchpoints, while completely masking Organic Social ($864k first-touch discovery) and Display ($575k awareness)."),
        ("Markov Removal Reality", "Absorbing Markov chain modeling reveals Paid Search (0.476 removal effect) and Email (0.451 removal effect) as non-negotiable core pillars, while Organic Social acts as the primary uncredited catalyst."),
        ("Budget Shift Impact", "Reallocating 20% budget away from low-efficiency Display (-30%) and Paid Social (-15%) to Email (+40%) and Paid Search (+10%) delivers +$267k to +$383k in incremental revenue (+6.3% to +9.0% lift).")
    ]
    
    for idx, (f_title, f_desc) in enumerate(findings):
        box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.4 + idx * 1.25), Inches(11.7), Inches(1.1))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = BORDER_COLOR
        
        tb = s2.shapes.add_textbox(Inches(1.0), Inches(3.45 + idx * 1.25), Inches(11.3), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_t = tf.paragraphs[0]
        p_t.text = f"0{idx+1}. {f_title}"
        p_t.font.bold = True
        p_t.font.size = Pt(13)
        p_t.font.color.rgb = NAVY_PRIMARY
        
        p_d = tf.add_paragraph()
        p_d.text = f_desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = SLATE_GRAY

    # =========================================================================
    # SLIDE 3: PROBLEM STATEMENT & DATA ENGINE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Business Problem & Analytical Data Infrastructure", "Context & Methodology")
    
    # Left column: The Business Problem
    box_p = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    box_p.fill.solid()
    box_p.fill.fore_color.rgb = WHITE
    box_p.line.color.rgb = BORDER_COLOR
    
    tbp = s3.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.8))
    tfp = tbp.text_frame
    tfp.word_wrap = True
    
    p = tfp.paragraphs[0]
    p.text = "THE ATTRIBUTION DILEMMA IN EDTECH"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    
    bullets_p = [
        "High-Consideration Cycle: EdTech purchases ($299 to $1,299) are rarely impulse buys. Average customer journeys involve 2 to 6 interactions across 8-15 days.",
        "Last-Touch Fallacy: Standard CRM platforms credit the final link clicked (often an automated promotional email), starving top-of-funnel channels of budget.",
        "Siloed Channel Measurement: Channel managers report platform-reported ROAS independently, resulting in double-counting and inflated performance claims.",
        "Goal: Build a unified, SQL-first attribution framework comparing heuristic models against a probabilistic Markov model to direct budget scientifically."
    ]
    for b in bullets_p:
        p_b = tfp.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = NAVY_PRIMARY
        
    # Right column: The Data Infrastructure
    box_d = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.3))
    box_d.fill.solid()
    box_d.fill.fore_color.rgb = WHITE
    box_d.line.color.rgb = BORDER_COLOR
    
    tbd = s3.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.0), Inches(4.8))
    tfd = tbd.text_frame
    tfd.word_wrap = True
    
    p = tfd.paragraphs[0]
    p.text = "ENTERPRISE DATA ENGINE (SQLITE & PYTHON)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = EMERALD_GREEN
    
    bullets_d = [
        "Dataset Scale: 25,000 unique prospective students, 59,940 touchpoints, 16 campaigns, and 4,879 verified course conversions.",
        "Referential Integrity: 100% foreign key consistency, zero orphan touchpoints, and zero post-conversion leakage (validated via 01_data_quality.sql).",
        "Deterministic Seed: Fully reproducible Python generator (seed=42) capturing realistic edtech seasonal peaks (New Year, Spring, Back-to-School).",
        "Modularity: Standalone SQL queries (01 to 07) coupled with an object-oriented Python mathematical engine ensuring complete portability."
    ]
    for b in bullets_d:
        p_b = tfd.add_paragraph()
        p_b.text = "• " + b
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = NAVY_PRIMARY

    # =========================================================================
    # SLIDE 4: CORE MARKETING KPIS & UNIT ECONOMICS
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Marketing Performance Scorecard & Unit Economics", "KPI Diagnostics")
    
    # 6 KPI Cards
    add_card(s4, Inches(0.8), Inches(1.6), Inches(3.6), Inches(1.4), "Conversion Rate (CR)", "19.52%", "4,879 Conversions / 25k Users", BLUE_ACCENT)
    add_card(s4, Inches(4.8), Inches(1.6), Inches(3.6), Inches(1.4), "Click-Through Rate (CTR)", "3.85%", "Total Clicks / Impressions", BLUE_ACCENT)
    add_card(s4, Inches(8.8), Inches(1.6), Inches(3.6), Inches(1.4), "Cost Per Click (CPC)", "$2.24", "Blended across paid channels", BLUE_ACCENT)
    
    add_card(s4, Inches(0.8), Inches(3.3), Inches(3.6), Inches(1.4), "Customer Acq. Cost (CAC)", f"${metrics['blended_cac']:.2f}", "Total Ad Spend / Buyers", EMERALD_GREEN)
    add_card(s4, Inches(4.8), Inches(3.3), Inches(3.6), Inches(1.4), "Average Order Value (AOV)", f"${metrics['average_order_value']:.2f}", "Flagship Bootcamp: $1,299", EMERALD_GREEN)
    add_card(s4, Inches(8.8), Inches(3.3), Inches(3.6), Inches(1.4), "12-Mo Projected CLV", f"${metrics['projected_clv']:.2f}", "AOV * 1.25 Repeat * 75% Margin", EMERALD_GREEN)
    
    # Bottom callout banner
    banner = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.0), Inches(11.7), Inches(1.8))
    banner.fill.solid()
    banner.fill.fore_color.rgb = NAVY_PRIMARY
    banner.line.fill.background()
    
    tb_b = s4.shapes.add_textbox(Inches(1.1), Inches(5.15), Inches(11.1), Inches(1.5))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    
    p = tf_b.paragraphs[0]
    p.text = "EXECUTIVE TAKEAWAY ON UNIT ECONOMICS:"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = EMERALD_GREEN
    
    p2 = tf_b.add_paragraph()
    p2.text = (
        f"Grito Labs exhibits outstanding unit economic health. With a Blended CAC of ${metrics['blended_cac']:.2f} "
        f"and an AOV of ${metrics['average_order_value']:.2f}, marketing costs are recouped on day 1 with an immediate "
        f"first-purchase ROAS of 5.73x. The 12-month CLV-to-CAC ratio stands at 5.37x (exceeding the 3.0x SaaS standard), "
        "validating that Grito Labs has substantial headroom to aggressively scale acquisition spend."
    )
    p2.font.size = Pt(11)
    p2.font.color.rgb = WHITE

    # =========================================================================
    # SLIDE 5: ATTRIBUTION MODEL COMPARISON
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Cross-Model Attribution Comparison: Revenue Allocation", "Attribution Analysis")
    
    # Table of models by channel
    rows, cols = 7, 7
    table_shape = s5.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.2))
    table = table_shape.table
    
    headers = ["Channel", "Spend ($)", "First-Touch", "Last-Touch", "Linear", "Time-Decay", "Markov Chain"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER if col_idx > 0 else PP_ALIGN.LEFT
            
    channel_order = ["Email", "Paid Search", "Paid Social", "Organic Social", "Display", "Referral"]
    for r_idx, ch in enumerate(channel_order, start=1):
        row_data = df_attr[df_attr['channel'] == ch].iloc[0]
        vals = [
            ch,
            f"${row_data['total_spend']:,.0f}",
            f"${row_data['First-Touch_revenue']:,.0f}",
            f"${row_data['Last-Touch_revenue']:,.0f}",
            f"${row_data['Linear_revenue']:,.0f}",
            f"${row_data['Time-Decay_revenue']:,.0f}",
            f"${row_data['markov_revenue']:,.0f}"
        ]
        for c_idx, val in enumerate(vals):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 1 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = NAVY_PRIMARY
                if c_idx == 0:
                    p.font.bold = True
                    p.alignment = PP_ALIGN.LEFT
                else:
                    p.alignment = PP_ALIGN.RIGHT

    # =========================================================================
    # SLIDE 6: THE MARKOV REMOVAL EFFECT
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Data-Driven Markov Chain Attribution: Removal Effects", "Algorithmic Discovery")
    
    # 2 Cards on top
    add_card(s6, Inches(0.8), Inches(1.6), Inches(5.6), Inches(1.4), "Baseline Conversion Probability", f"{metrics['markov_baseline_conversion_rate']:.2f}%", "P(Conversion | All Channels Active)", BLUE_ACCENT)
    add_card(s6, Inches(6.9), Inches(1.6), Inches(5.6), Inches(1.4), "Attribution Conservation", "100.00% Conserved", "Zero conversions or dollars lost ($4.26M accounted)", EMERALD_GREEN)
    
    # Table of Removal Effects
    rows, cols = 7, 5
    t_shape = s6.shapes.add_table(rows, cols, Inches(0.8), Inches(3.3), Inches(11.7), Inches(3.6))
    t_m = t_shape.table
    
    m_headers = ["Marketing Channel", "Removal Effect", "Markov Weight", "Attributed Revenue ($)", "Strategic Interpretation"]
    for c_idx, h in enumerate(m_headers):
        cell = t_m.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = WHITE
            
    m_data = [
        ("Paid Search", "0.4757", "24.81%", "$1,056,711", "Highest standalone impact; removing it causes a 47.6% drop in overall sales."),
        ("Email Nurturing", "0.4507", "23.51%", "$1,001,269", "Crucial mid-funnel closer; essential bridge across consideration lag."),
        ("Paid Social", "0.3673", "19.16%", "$815,894", "Key discovery engine; high assist volume across multi-touch paths."),
        ("Organic Social", "0.2887", "15.06%", "$641,298", "Zero direct ad cost but drives 15% of business value via thought leadership."),
        ("Display Advertising", "0.2082", "10.86%", "$462,607", "Moderate removal effect; low direct conversions, high awareness assist."),
        ("Referral Network", "0.1264", "6.59%", "$280,842", "High conversion rate but constrained inventory; acts as high-trust amplifier.")
    ]
    
    for r_idx, row in enumerate(m_data, start=1):
        for c_idx, val in enumerate(row):
            cell = t_m.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 1 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = NAVY_PRIMARY
                if c_idx == 0:
                    p.font.bold = True

    # =========================================================================
    # SLIDE 7: CUSTOMER JOURNEY INSIGHTS
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Customer Journey Analysis & Conversion Funnels", "Behavioral Dynamics")
    
    # 3 Summary metric pills
    add_card(s7, Inches(0.8), Inches(1.6), Inches(3.6), Inches(1.3), "Median Conversion Lag", "2.4 Days", "Multi-touch journeys range 2 to 6 touches", BLUE_ACCENT)
    add_card(s7, Inches(4.8), Inches(1.6), Inches(3.6), Inches(1.3), "Multi-Touch Share", "88.2%", "Only 11.8% of users convert on 1st touch", BLUE_ACCENT)
    add_card(s7, Inches(8.8), Inches(1.6), Inches(3.6), Inches(1.3), "Dominant Nurture Step", "Email Flow", "Present in 68% of multi-touch conversions", EMERALD_GREEN)
    
    # Table of Top Conversion Paths
    rows, cols = 6, 5
    t_path_shape = s7.shapes.add_table(rows, cols, Inches(0.8), Inches(3.2), Inches(11.7), Inches(3.7))
    t_p = t_path_shape.table
    
    p_headers = ["Top Customer Path Sequences", "Touchpoints", "Conversions", "Revenue ($)", "Avg Lag (Days)"]
    for c_idx, h in enumerate(p_headers):
        cell = t_p.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = WHITE
            
    top_paths = [
        ("Paid Search > Conversion (High Intent Direct)", "1", "144", "$127,656", "1.1"),
        ("Paid Social > Conversion (Direct Impulsive)", "1", "123", "$107,777", "1.0"),
        ("Paid Search > Email > Conversion (Search & Nurture)", "2", "115", "$102,185", "2.4"),
        ("Organic Social > Conversion (High Trust Organic)", "1", "103", "$88,397", "1.0"),
        ("Paid Social > Email > Conversion (Social Acquisition Nurture)", "2", "98", "$87,302", "2.3")
    ]
    for r_idx, row in enumerate(top_paths, start=1):
        for c_idx, val in enumerate(row):
            cell = t_p.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 1 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = NAVY_PRIMARY
                if c_idx == 0:
                    p.font.bold = True

    # =========================================================================
    # SLIDE 8: CAMPAIGN EFFICIENCY CLASSIFICATION
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Campaign Efficiency Ranking: Scaling vs. Trimming", "Portfolio Optimization")
    
    # 3 Tier Summary Boxes
    tiers = [
        ("TIER 1: HIGH PERFORMERS (SCALE UP)", "ROAS >= 3.0x | CAC <= $200", [
            "CMP-EM-01/02/03 (Email Nurturing & Promo): 26x - 50x ROAS. Exceptional unit economics.",
            "CMP-PS-01 (Brand Search Core): 5.57x ROAS, $157 CAC. Uncapped high-intent capture.",
            "CMP-RF-01 (Alumni Ambassador): 5.22x ROAS, $176 CAC. High referral credibility.",
            "CMP-OS-01/02 (Organic Video & Founder): Infinity ROAS (Zero ad spend), drives $600k+ revenue."
        ], EMERALD_GREEN),
        ("TIER 2: PROFITABLE (MAINTAIN / OPTIMIZE)", "1.5x <= ROAS < 3.0x", [
            "CMP-PS-02 (NonBrand Analytics): 3.20x ROAS. Profitable top-of-funnel capture; tighten negative keywords.",
            "CMP-SO-02 (Meta Retargeting): 4.70x ROAS. Solid conversion closer; refresh creative assets bi-weekly.",
            "CMP-RF-02 (Partner Affiliate): 3.10x ROAS. Scale commission-based deals."
        ], BLUE_ACCENT),
        ("TIER 3: UNDERPERFORMERS (REDUCE / REALLOCATE)", "ROAS < 1.5x or Low Marginal Efficiency", [
            "CMP-DP-01 (GDN Prospecting Banners): 2.80x ROAS, high CPC relative to low intent.",
            "CMP-SO-03 (LinkedIn B2B Lead Gen): $6.50 CPC leads to high CAC ($320+). Reallocate into Brand Search.",
            "Action: Trim Display spend by 30% and LinkedIn prospecting by 15% to fund Email and Brand Search."
        ], RGBColor(239, 68, 68))
    ]
    
    for idx, (t_title, t_sub, t_items, color) in enumerate(tiers):
        t_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 3.95), Inches(1.6), Inches(3.8), Inches(5.3))
        t_box.fill.solid()
        t_box.fill.fore_color.rgb = WHITE
        t_box.line.color.rgb = BORDER_COLOR
        
        # Header bar
        bar = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + idx * 3.95), Inches(1.6), Inches(3.8), Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = color
        bar.line.fill.background()
        
        tb = s8.shapes.add_textbox(Inches(1.0 + idx * 3.95), Inches(1.85), Inches(3.4), Inches(4.8))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = t_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = color
        
        p_sub = tf.add_paragraph()
        p_sub.text = t_sub
        p_sub.font.size = Pt(9)
        p_sub.font.color.rgb = SLATE_GRAY
        
        for item in t_items:
            p_i = tf.add_paragraph()
            p_i.text = "• " + item
            p_i.font.size = Pt(10)
            p_i.font.color.rgb = NAVY_PRIMARY

    # =========================================================================
    # SLIDE 9: QUANTITATIVE BUDGET REALLOCATION SCENARIOS
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Projected Commercial Impact: Budget Reallocation Scenarios", "Growth Strategy")
    
    # Left Card: Conservative Case
    c_res = metrics['budget_scenario_results']
    box_c = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.6), Inches(2.2))
    box_c.fill.solid()
    box_c.fill.fore_color.rgb = WHITE
    box_c.line.color.rgb = BORDER_COLOR
    
    tbc = s9.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(1.8))
    tfc = tbc.text_frame
    tfc.word_wrap = True
    
    p = tfc.paragraphs[0]
    p.text = "CONSERVATIVE SCENARIO (85% Marginal ROAS)"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = BLUE_ACCENT
    
    p2 = tfc.add_paragraph()
    p2.text = f"Projected Revenue: ${c_res['conservative_projected_revenue']:,.0f}"
    p2.font.bold = True
    p2.font.size = Pt(20)
    p2.font.color.rgb = NAVY_PRIMARY
    
    p3 = tfc.add_paragraph()
    p3.text = f"Incremental Revenue Lift: +${c_res['conservative_revenue_lift']:,.0f} (+6.3% Lift)\nProjected ROAS: {c_res['conservative_projected_roas']:.2f}x (up from 5.73x)"
    p3.font.size = Pt(11)
    p3.font.color.rgb = EMERALD_GREEN
    
    # Right Card: Optimistic Case
    box_o = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.6), Inches(5.6), Inches(2.2))
    box_o.fill.solid()
    box_o.fill.fore_color.rgb = WHITE
    box_o.line.color.rgb = BORDER_COLOR
    
    tbo = s9.shapes.add_textbox(Inches(7.2), Inches(1.8), Inches(5.0), Inches(1.8))
    tfo = tbo.text_frame
    tfo.word_wrap = True
    
    p = tfo.paragraphs[0]
    p.text = "OPTIMISTIC SCENARIO (100% Retained ROAS)"
    p.font.bold = True
    p.font.size = Pt(11)
    p.font.color.rgb = EMERALD_GREEN
    
    p2 = tfo.add_paragraph()
    p2.text = f"Projected Revenue: ${c_res['optimistic_projected_revenue']:,.0f}"
    p2.font.bold = True
    p2.font.size = Pt(20)
    p2.font.color.rgb = NAVY_PRIMARY
    
    p3 = tfo.add_paragraph()
    p3.text = f"Incremental Revenue Lift: +${c_res['optimistic_revenue_lift']:,.0f} (+9.0% Lift)\nProjected ROAS: {c_res['optimistic_projected_roas']:.2f}x (up from 5.73x)"
    p3.font.size = Pt(11)
    p3.font.color.rgb = EMERALD_GREEN

    # Bottom Table: Shift Breakdown
    rows, cols = 6, 6
    t_shift_shape = s9.shapes.add_table(rows, cols, Inches(0.8), Inches(4.1), Inches(11.7), Inches(2.9))
    t_s = t_shift_shape.table
    
    s_headers = ["Channel", "Current Spend ($)", "Shift (%)", "New Spend ($)", "Current Revenue ($)", "Conservative Projected ($)"]
    for c_idx, h in enumerate(s_headers):
        cell = t_s.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = WHITE
            
    shift_table_data = [
        ("Display", "$139,353", "-30.0%", "$97,547", "$419,689", "$293,782"),
        ("Paid Social", "$256,411", "-15.0%", "$217,949", "$811,222", "$689,539"),
        ("Email Nurturing", "$30,980", "+40.0%", "$43,372", "$1,083,832", "$1,452,335"),
        ("Paid Search", "$254,078", "+10.0%", "$279,486", "$1,082,524", "$1,174,272"),
        ("Referral Network", "$62,083", "+25.0%", "$77,604", "$256,950", "$311,544")
    ]
    for r_idx, row in enumerate(shift_table_data, start=1):
        for c_idx, val in enumerate(row):
            cell = t_s.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG if r_idx % 2 == 1 else WHITE
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.font.color.rgb = NAVY_PRIMARY
                if c_idx == 0:
                    p.font.bold = True

    # =========================================================================
    # SLIDE 10: STRATEGIC RECOMMENDATIONS & ROADMAP
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Strategic Action Plan & Analytical Roadmap", "Executive Roadmap")
    
    pillars = [
        ("1. Immediate Budget Reallocation (Q4 2026)", [
            "Execute the recommended 20% budget shift away from Display and low-converting LinkedIn prospecting.",
            "Infuse $12.4k into Email infrastructure and $25.4k into high-intent Google Search campaigns.",
            "Target: Realize an estimated +$267,500 in additional bootcamp enrollments without expanding gross budget."
        ]),
        ("2. Shift from Last-Touch to Markov Attribution", [
            "Deprecate single-touch reporting in executive KPI dashboards.",
            "Adopt the Markov removal effect model as the primary source of truth for channel CAC & ROAS.",
            "Ensures Organic Social and top-of-funnel awareness efforts maintain appropriate executive support."
        ]),
        ("3. Creative & Audience Refresh Protocol", [
            "Mitigate ad fatigue in Paid Social by implementing a 14-day creative rotation cycle for video testimonials.",
            "Implement negative audience exclusions: immediately suppress converted users from paid prospecting."
        ]),
        ("4. Advanced Analytics & Infrastructure Next Steps", [
            "Implement Marketing Mix Modeling (MMM via LightweightMMM or Meridian) to measure offline impact.",
            "Integrate server-side Conversion API (CAPI) for Meta and Enhanced Conversions for Google Ads.",
            "Develop student LTV expansion models: upsell bootcamp alumni to advanced AI/ML Master Tracks."
        ])
    ]
    
    for idx, (p_title, p_points) in enumerate(pillars):
        top_offset = Inches(1.6 + (idx // 2) * 2.7)
        left_offset = Inches(0.8 + (idx % 2) * 5.95)
        
        box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_offset, top_offset, Inches(5.7), Inches(2.5))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = BORDER_COLOR
        
        tb = s10.shapes.add_textbox(left_offset + Inches(0.2), top_offset + Inches(0.15), Inches(5.3), Inches(2.2))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = p_title
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = BLUE_ACCENT
        
        for pt in p_points:
            p_pt = tf.add_paragraph()
            p_pt.text = "• " + pt
            p_pt.font.size = Pt(10)
            p_pt.font.color.rgb = NAVY_PRIMARY

    # Save presentation
    output_path = os.path.join(DECK_DIR, "Marketing_Attribution_Findings.pptx")
    prs.save(output_path)
    print(f"--> Successfully created executive presentation: {output_path}")

if __name__ == "__main__":
    build_presentation()

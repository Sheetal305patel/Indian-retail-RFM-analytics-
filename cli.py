"""
Command-Line Interface for Customer Value and Lifecycle Segmentation
Powered by Click and Rich for enterprise terminal workflows.
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import json
import sys

# Ensure current folder is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.data_generator import generate_enterprise_dataset
from src.identity_resolution import run_identity_resolution
from src.etl_pipeline import run_etl_pipeline
from src.rfm_engine import calculate_rfm_table
from src.validation import run_comprehensive_validation
from src.campaign_engine import export_all_default_audiences, export_campaign_audience
from src.pilot_measurement import simulate_and_measure_pilot
from src.predictive_models import train_and_score_predictive_models
from src.streaming_pipeline import stream_engine, generate_simulated_stream_event
import time

console = Console(legacy_windows=False)

@click.group()
def cli():
    """Customer Value and Lifecycle Segmentation (RFM Engine) CLI"""
    pass

@cli.command("generate-data")
@click.option("--customers", default=3000, help="Number of customer entities to generate.")
@click.option("--orders", default=15000, help="Number of orders to generate.")
@click.option("--as-of", default="2026-11-20", help="As-of snapshot date (YYYY-MM-DD).")
def generate_data(customers, orders, as_of):
    """Generates synthetic omnichannel enterprise retail dataset."""
    console.print(Panel(f"[bold cyan]Generating {customers:,} customers & {orders:,} orders as of {as_of}...[/bold cyan]"))
    generate_enterprise_dataset(num_customers=customers, num_orders=orders, as_of_date=as_of)
    console.print("[bold green][OK] Data generation finished successfully.[/bold green]")

@cli.command("resolve-identity")
def resolve_identity():
    """Stitches cross-channel identifiers and generates identity coverage report."""
    console.print(Panel("[bold cyan]Executing Customer Identity Resolution & Deduplication...[/bold cyan]"))
    res = run_identity_resolution()
    
    table = Table(title="Omnichannel Identity Coverage Summary")
    table.add_column("Metric", style="bold yellow")
    table.add_column("Value", style="bold green")
    table.add_row("Total Orders", f"{res['total_orders']:,}")
    table.add_row("Identified Orders", f"{res['identified_orders']:,}")
    table.add_row("Anonymous POS Orders", f"{res['anonymous_orders']:,}")
    table.add_row("Identified Revenue Coverage", f"{res['revenue_coverage_pct']}%")
    table.add_row("Anonymous Net Sales (Excluded)", f"₹{res['anonymous_net_sales_usd']:,.2f}")
    console.print(table)

@cli.command("run-etl")
@click.option("--as-of", default="2026-11-20", help="As-of snapshot date (YYYY-MM-DD).")
def run_etl(as_of):
    """Executes order curation, return subtractions, and window boundaries."""
    console.print(Panel(f"[bold cyan]Running ETL Order Curation as of {as_of}...[/bold cyan]"))
    res = run_etl_pipeline(as_of_date=as_of)
    console.print(f"[bold green][OK] Curated {res['qualifying_orders_count']:,} qualifying orders (₹{res['qualifying_net_sales_usd']:,.2f} INR).[/bold green]")

@cli.command("score-rfm")
@click.option("--as-of", default="2026-11-20", help="As-of snapshot date (YYYY-MM-DD).")
def score_rfm(as_of):
    """Calculates RFM metrics, 1-5 quantile scores, and 8 lifecycle segments."""
    console.print(Panel(f"[bold cyan]Computing RFM Scoring and Segment Assignment as of {as_of}...[/bold cyan]"))
    df = calculate_rfm_table(as_of_date=as_of)
    
    table = Table(title="RFM Lifecycle Segment Distribution (Indian Market)")
    table.add_column("Segment", style="bold white")
    table.add_column("Customer Count", justify="right", style="cyan")
    table.add_column("Share (%)", justify="right", style="yellow")
    table.add_column("Net Sales (INR ₹)", justify="right", style="green")

    counts = df["segment"].value_counts()
    for seg, cnt in counts.items():
        pct = (cnt / len(df)) * 100
        rev = df[df["segment"] == seg]["net_sales_usd"].sum()
        table.add_row(seg, f"{cnt:,}", f"{pct:.1f}%", f"₹{rev:,.2f}")

    console.print(table)
    console.print(f"[bold green][OK] Scored {len(df):,} customers and persisted to SQLite/CSV.[/bold green]")

@cli.command("validate")
@click.option("--as-of", default="2026-11-20", help="As-of snapshot date (YYYY-MM-DD).")
def validate(as_of):
    """Runs automated 10-point audit checklist and reconciliation."""
    console.print(Panel(f"[bold cyan]Executing Comprehensive Audit & Acceptance Checks as of {as_of}...[/bold cyan]"))
    report = run_comprehensive_validation(as_of_date=as_of)

    table = Table(title=f"Reconciliation & Audit Checklist ({report['scorecard']})")
    table.add_column("Check ID", style="dim")
    table.add_column("Requirement", style="bold white")
    table.add_column("Status", justify="center")
    table.add_column("Actual Result", style="italic")

    for c in report["checklist"]:
        status_str = "[bold green]PASS[/bold green]" if c["passed"] else "[bold red]FAIL[/bold red]"
        table.add_row(c["check_id"], c["name"], status_str, str(c["actual"]))

    console.print(table)
    if report["overall_status"] == "PASSED":
        console.print("[bold green][OK] All audit checks passed! Dataset signed off for commercial activation.[/bold green]")
    else:
        console.print("[bold red][FAILED] Audit failed on one or more critical checks.[/bold red]")

@cli.command("export-audiences")
def export_audiences():
    """Generates privacy-compliant marketing campaign audience files with holdouts."""
    console.print(Panel("[bold cyan]Exporting Campaign Audiences with Privacy & Holdout Splits...[/bold cyan]"))
    export_all_default_audiences()
    console.print("[bold green][OK] Default audience lists exported to data/exports/.[/bold green]")

@cli.command("run-pilot")
def run_pilot():
    """Measures Treatment vs Holdout pilot performance and incremental margin."""
    console.print(Panel("[bold cyan]Simulating & Measuring A/B Campaign Lift...[/bold cyan]"))
    res = simulate_and_measure_pilot()

    table = Table(title=f"Campaign Pilot Lift Measurement: {res['campaign_name']}")
    table.add_column("Metric", style="bold yellow")
    table.add_column("Treatment", justify="right", style="cyan")
    table.add_column("Holdout Control", justify="right", style="magenta")
    table.add_column("Lift / Delta", justify="right", style="bold green")

    table.add_row("Sample Size", f"{res['treatment_sample_size']:,}", f"{res['control_sample_size']:,}", "-")
    table.add_row("Conversion Rate", f"{res['treatment_conversion_rate']}%", f"{res['control_conversion_rate']}%", f"+{res['conversion_lift_points']}%")
    table.add_row("Revenue / Contact", f"₹{res['treatment_revenue_per_contact']:.2f}", f"₹{res['control_revenue_per_contact']:.2f}", f"+₹{res['incremental_revenue_per_contact']:.2f}")
    table.add_row("Margin / Contact", "-", "-", f"+₹{res['incremental_contribution_margin_per_contact']:.2f}")
    table.add_row("Total Incr. Margin", "-", "-", f"₹{res['total_campaign_incremental_contribution_margin']:,.2f}")

    console.print(table)
    console.print(f"[bold green][OK] Pilot analysis complete. Statistically Significant: {res['statistically_significant']} (z={res['z_score']}).[/bold green]")

@cli.command("train-ml")
@click.option("--as-of", default="2026-11-20", help="As-of snapshot date (YYYY-MM-DD).")
def train_ml(as_of):
    """Trains PyTorch Neural Churn Classifier & forward 12-Month pLTV model."""
    console.print(Panel(f"[bold cyan]Training ML Predictive Models (Churn & pLTV) as of {as_of}...[/bold cyan]"))
    res = train_and_score_predictive_models(as_of_date=as_of)
    df = res["df_scored"]

    table = Table(title="Predictive Churn Risk & Strategic Value Matrix")
    table.add_column("Strategic Quadrant", style="bold white")
    table.add_column("Customer Count", justify="right", style="cyan")
    table.add_column("Share (%)", justify="right", style="yellow")
    table.add_column("12M Forecast Spend (INR ₹)", justify="right", style="green")

    quads = df["strategic_quadrant"].value_counts()
    for q_name, cnt in quads.items():
        pct = (cnt / len(df)) * 100
        spend = df[df["strategic_quadrant"] == q_name]["predicted_12m_net_sales"].sum()
        table.add_row(q_name, f"{cnt:,}", f"{pct:.1f}%", f"₹{spend:,.2f}")

    console.print(table)
    console.print(f"[bold green][OK] Trained PyTorch churn model. Total 12M Predicted Spend: ₹{res['total_predicted_revenue']:,.2f}[/bold green]")

@cli.command("stream-events")
@click.option("--events", default=10, help="Number of real-time events to stream.")
@click.option("--interval", default=0.3, help="Seconds between live events.")
def stream_events(events, interval):
    """Simulates real-time event bus stream with online state recalculations."""
    console.print(Panel(f"[bold cyan]Streaming {events} live retail events with dynamic RFM & segment updates...[/bold cyan]"))
    
    table = Table(title="Real-Time Event Processing Stream")
    table.add_column("Time", style="dim")
    table.add_column("Customer ID", style="bold cyan")
    table.add_column("Amount (INR)", justify="right", style="green")
    table.add_column("RFM Code", justify="center", style="yellow")
    table.add_column("Live Segment", style="white")
    table.add_column("Promotion Alert", style="bold magenta")

    for i in range(events):
        evt = generate_simulated_stream_event()
        res = stream_engine.process_order_event(evt)
        promo = f"[bold green]PROMOTED: {res['old_segment']} -> {res['new_segment']}[/bold green]" if res["segment_transition"] else "-"
        table.add_row(
            res["timestamp"].split(" ")[1],
            res["customer_id"],
            f"₹{res['amount']:.2f}",
            f"{res['old_rfm']} -> {res['new_rfm']}",
            res["new_segment"],
            promo
        )
        time.sleep(interval)

    console.print(table)
    console.print(f"[bold green][OK] Processed {events} live stream events. Total live revenue: ₹{stream_engine.live_revenue_added:,.2f}[/bold green]")

@cli.command("run-all")
@click.option("--as-of", default="2026-11-20", help="As-of snapshot date (YYYY-MM-DD).")
def run_all(as_of):
    """Executes the entire end-to-end pipeline from data generation to validation and ML."""
    console.print(Panel.fit("[bold green]Executing Full End-to-End Customer RFM & Predictive ML Pipeline[/bold green]"))
    generate_enterprise_dataset(as_of_date=as_of)
    run_identity_resolution()
    run_etl_pipeline(as_of_date=as_of)
    calculate_rfm_table(as_of_date=as_of)
    train_and_score_predictive_models(as_of_date=as_of)
    run_comprehensive_validation(as_of_date=as_of)
    export_all_default_audiences()
    simulate_and_measure_pilot()
    console.print(Panel("[bold green][OK] Complete End-to-End Execution Successful![/bold green]"))

@cli.command("serve")
@click.option("--port", default=5000, help="Port to run web dashboard on.")
def serve(port):
    """Starts the Flask interactive dashboard web application."""
    from web.app import app
    console.print(Panel(f"[bold cyan]Launching Interactive RFM Dashboard at http://127.0.0.1:{port}...[/bold cyan]"))
    app.run(host="127.0.0.1", port=port, debug=False)

if __name__ == "__main__":
    cli()

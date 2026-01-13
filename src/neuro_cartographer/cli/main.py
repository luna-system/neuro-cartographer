import click
from neuro_cartographer import __version__

@click.group()
@click.version_option(version=__version__)
def cli():
    """Neuro-Cartographer: Exploring the shape of thought."""
    pass

@cli.command()
@click.option("--model", required=True, help="Path or HuggingFace ID of the model")
@click.option("--dataset", required=True, help="Path to JSONL dataset of concepts")
@click.option("--output", default="galaxy_map.json", help="Output file for map data")
def map(model, dataset, output):
    """Scan a model and generate a semantic map."""
    click.echo(f"🔭 Scanning model: {model}")
    click.echo(f"📄 Dataset: {dataset}")
    # TODO: Connect to Scanner
    click.echo("... (Scanner implementation pending) ...")

@cli.command()
@click.argument("map_file")
@click.option("--port", default=8000, help="Port to serve the Orrery on")
def serve(map_file, port):
    """Serve the 3D Orrery visualization."""
    click.echo(f"🌌 Launching Orrery for {map_file} on http://localhost:{port}")
    # TODO: Connect to Visualizer
    
if __name__ == "__main__":
    cli()

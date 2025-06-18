import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from app.models.snort import SnortAlert
from app.services.ai import analyze_alert
from datetime import datetime

console = Console()

def create_alert_from_text(text: str) -> SnortAlert:
    """Create a SnortAlert object from user input text."""
    # For general questions, create a generic alert with the question as the message
    return SnortAlert(
        alert_type="GENERAL_QUERY",
        priority=3,  # Medium priority for general queries
        message=text,
        source_ip="0.0.0.0",
        source_port=0,
        destination_ip="0.0.0.0",
        destination_port=0,
        protocol="N/A",
        timestamp=datetime.now().isoformat(),
        classification="General Query",
        signature_id="0:0:0",
        raw_alert=text
    )

@click.command()
@click.option('--model', default='gpt-4', help='OpenAI model to use')
def chat(model: str):
    """Interactive CLI for discussing Snort issues with AI."""
    console.print(Panel.fit(
        "[bold blue]SnortAI Chat Interface[/bold blue]\n"
        "Ask questions about Snort alerts, configurations, or security issues.\n"
        "Type 'exit' or 'quit' to end the session.",
        title="Welcome"
    ))
    
    while True:
        query = Prompt.ask("\n[bold green]You[/bold green]")
        
        if query.lower() in ['exit', 'quit']:
            console.print("\n[bold blue]Goodbye![/bold blue]")
            break
            
        try:
            # Create an alert object from the query
            alert = create_alert_from_text(query)
            
            # Get AI analysis
            analysis = analyze_alert(alert, model)
            
            # Display the response
            console.print("\n[bold blue]AI Response:[/bold blue]")
            console.print(Markdown(analysis.analysis))
            
            if analysis.recommendations:
                console.print("\n[bold yellow]Recommendations:[/bold yellow]")
                console.print(Markdown(analysis.recommendations))
            
            console.print(f"\n[bold cyan]Confidence Score:[/bold cyan] {analysis.confidence_score}%")
            
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

if __name__ == '__main__':
    chat() 
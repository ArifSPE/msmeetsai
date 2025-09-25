"""
Main entry point for the Agentic Business Rules POC

This module provides a unified interface to initialize and run the system.
"""
import asyncio
import logging
import argparse
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from src.api.main import app
from examples.demo_scenarios import BusinessRulesDemoRunner


def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=settings.log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('agentic_poc.log')
        ]
    )


async def run_demo():
    """Run the demo scenarios"""
    demo = BusinessRulesDemoRunner()
    await demo.run_all_demos()


async def run_interactive_demo():
    """Run the interactive demo"""
    demo = BusinessRulesDemoRunner()
    await demo.run_interactive_demo()


def run_api_server():
    """Run the FastAPI server"""
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Agentic Business Rules POC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode demo          # Run all demo scenarios
  python main.py --mode interactive   # Run interactive demo
  python main.py --mode api           # Start API server
  python main.py --mode api --port 9000  # Start API on custom port
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["demo", "interactive", "api"],
        default="demo",
        help="Mode to run the POC (default: demo)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.api_port,
        help=f"Port for API server (default: {settings.api_port})"
    )
    
    parser.add_argument(
        "--host",
        default=settings.api_host,
        help=f"Host for API server (default: {settings.api_host})"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=settings.log_level,
        help=f"Log level (default: {settings.log_level})"
    )
    
    args = parser.parse_args()
    
    # Update settings if provided
    if args.port != settings.api_port:
        settings.api_port = args.port
    if args.host != settings.api_host:
        settings.api_host = args.host
    if args.log_level != settings.log_level:
        settings.log_level = args.log_level
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Agentic Business Rules POC in {args.mode} mode")
    
    try:
        if args.mode == "demo":
            asyncio.run(run_demo())
        elif args.mode == "interactive":
            asyncio.run(run_interactive_demo())
        elif args.mode == "api":
            logger.info(f"Starting API server on {args.host}:{args.port}")
            run_api_server()
    
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error running POC: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
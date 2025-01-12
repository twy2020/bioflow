import argparse
import os
from colorama import Fore, Back, Style, init

def parse_args():
    """
    Parse and return command-line arguments for the program.

    Returns:
        args (argparse.Namespace): Parsed arguments with default values if not provided.
    """
    parser = argparse.ArgumentParser(
        description="Parameter management for external argument passing."
    )
    
    # Define arguments
    parser.add_argument(
        '-w', '--workspace_path',
        type=str,
        default=os.getcwd(),
        help='Path to the workspace directory. Default is the program start directory.'
    )
    parser.add_argument(
        '-j', '--jobs',
        type=int,
        default=4,
        help='Maximum number of jobs for multiprocessing. Default is 4.'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    return args

def display_args(args):
    """
    Display parsed command-line arguments in a formatted way.

    Args:
        args (argparse.Namespace): Parsed arguments to display.
    """
    print("\n")
    print(f"{Fore.YELLOW}Use Arguments:{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}-w Workspace Path:{Style.RESET_ALL} {args.workspace_path}")
    print(f"  {Fore.CYAN}-j Multiprocess Max Jobs:{Style.RESET_ALL} {args.jobs}")
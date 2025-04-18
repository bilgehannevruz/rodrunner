"""
Data ingest workflows.
"""
from typing import Dict, List, Optional, Union, Any
import os

from prefect import flow, task, get_run_logger
from prefect.context import get_run_context

from rodrunner.models.config import AppConfig
from rodrunner.tasks.filesystem import find_sequencer_runs_task
from rodrunner.tasks.parsing import parse_sequencer_run
from rodrunner.sequencers.miseq import MiSeqWorkflow
from rodrunner.sequencers.novaseq import NovaSeqWorkflow


@flow(name="Ingest Sequencer Runs")
def ingest_sequencer_runs(
    config: AppConfig,
    sequencer_type: str,
    root_dir: Optional[str] = None,
    completion_indicator: str = "RTAComplete.txt"
) -> List[Dict[str, Any]]:
    """
    Ingest all completed sequencer runs of a specific type.
    
    Args:
        config: Application configuration
        sequencer_type: Type of sequencer (miseq, nextseq, etc.)
        root_dir: Root directory to search for sequencer runs (defaults to config.sequencer.base_dir)
        completion_indicator: Filename that indicates a completed run
        
    Returns:
        List of dictionaries with the results of the ingestion
    """
    logger = get_run_logger()
    
    # Use default root directory if not provided
    if root_dir is None:
        root_dir = config.sequencer.base_dir
    
    # Find completed sequencer runs
    logger.info(f"Finding {sequencer_type} runs in {root_dir}")
    run_dirs = find_sequencer_runs_task(
        root_dir=root_dir,
        sequencer_type=sequencer_type,
        completion_indicator=completion_indicator
    )
    
    logger.info(f"Found {len(run_dirs)} {sequencer_type} runs")
    
    # Create workflow instance based on sequencer type
    if sequencer_type == 'miseq':
        workflow = MiSeqWorkflow(config)
    elif sequencer_type == 'novaseq':
        workflow = NovaSeqWorkflow(config)
    else:
        raise ValueError(f"Unsupported sequencer type: {sequencer_type}")
    
    # Process each run
    results = []
    for run_dir in run_dirs:
        logger.info(f"Processing run: {run_dir}")
        
        try:
            result = workflow.process_run(run_dir)
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing run {run_dir}: {str(e)}")
            results.append({
                'success': False,
                'run_dir': run_dir,
                'error': str(e)
            })
    
    return results


@flow(name="Ingest All Sequencer Runs")
def ingest_all_sequencer_runs(
    config: AppConfig,
    root_dir: Optional[str] = None,
    completion_indicator: str = "RTAComplete.txt"
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Ingest all completed sequencer runs of all supported types.
    
    Args:
        config: Application configuration
        root_dir: Root directory to search for sequencer runs (defaults to config.sequencer.base_dir)
        completion_indicator: Filename that indicates a completed run
        
    Returns:
        Dictionary mapping sequencer types to lists of ingestion results
    """
    logger = get_run_logger()
    
    # Use default root directory if not provided
    if root_dir is None:
        root_dir = config.sequencer.base_dir
    
    # Supported sequencer types
    sequencer_types = ['miseq', 'novaseq']
    
    # Process each sequencer type
    results = {}
    for sequencer_type in sequencer_types:
        logger.info(f"Processing {sequencer_type} runs")
        
        try:
            type_results = ingest_sequencer_runs(
                config=config,
                sequencer_type=sequencer_type,
                root_dir=root_dir,
                completion_indicator=completion_indicator
            )
            results[sequencer_type] = type_results
        except Exception as e:
            logger.error(f"Error processing {sequencer_type} runs: {str(e)}")
            results[sequencer_type] = [{
                'success': False,
                'error': str(e)
            }]
    
    return results

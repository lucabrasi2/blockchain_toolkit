"""
Universal Blockchain Platform (UBP)
Module: TRON Controller
Purpose: Coordinates TRON blockchain operations
Author: UBP Engineering Team
Version: 2.0.0
"""
from typing import Dict, Any, Optional, List
from core.logger import get_logger
from services.tron.wallet_service import TronWalletService
from services.tron.contract_service import TronContractService
from services.tron.token_service import TronTokenService
from services.tron.block_service import TronBlockService
from services.tron.transaction_service import TronTransactionService
from exceptions.blockchain_exceptions import UBPException

logger = get_logger(__name__)


class TronController:
    """
    Controller responsible for TRON blockchain operations.
    """
    
    def __init__(self):
        """Initialize the TRON Controller."""
        self.wallet_service = TronWalletService()
        self.contract_service = TronContractService()
        self.token_service = TronTokenService()
        self.block_service = TronBlockService()
        self.transaction_service = TronTransactionService()
        logger.info("TronController initialized.")
    
    # ================================================================
    # WALLET OPERATIONS
    # ================================================================
    
    def wallet_inspector(self, address: str) -> Dict[str, Any]:
        """
        Inspect a TRON wallet.
        
        Parameters
        ----------
        address : str
            TRON wallet address.
            
        Returns
        -------
        Dict[str, Any]
            Wallet inspection report.
        """
        try:
            logger.info(f"Inspecting TRON wallet: {address}")
            report = self.wallet_service.get_wallet_report(address)
            logger.info("TRON wallet inspection completed successfully.")
            return report
        except Exception as e:
            logger.error(f"TRON wallet inspection failed: {e}")
            raise
    
    # ================================================================
    # CONTRACT OPERATIONS
    # ================================================================
    
    def contract_inspector(self, address: str) -> Dict[str, Any]:
        """
        Inspect a TRON contract.
        
        Parameters
        ----------
        address : str
            TRON contract address.
            
        Returns
        -------
        Dict[str, Any]
            Contract inspection report.
        """
        try:
            logger.info(f"Inspecting TRON contract: {address}")
            report = self.contract_service.get_contract_report(address)
            logger.info("TRON contract inspection completed successfully.")
            return report
        except Exception as e:
            logger.error(f"TRON contract inspection failed: {e}")
            raise
    
    # ================================================================
    # TOKEN OPERATIONS
    # ================================================================
    
    def token_inspector(self, address: str) -> Dict[str, Any]:
        """
        Inspect a TRON token.
        
        Parameters
        ----------
        address : str
            TRON token address.
            
        Returns
        -------
        Dict[str, Any]
            Token inspection report.
        """
        try:
            logger.info(f"Inspecting TRON token: {address}")
            report = self.token_service.get_token_report(address)
            logger.info("TRON token inspection completed successfully.")
            return report
        except Exception as e:
            logger.error(f"TRON token inspection failed: {e}")
            raise
    
    # ================================================================
    # BLOCK OPERATIONS
    # ================================================================
    
    def block_explorer(self, block_identifier: Any) -> Dict[str, Any]:
        """
        Explore a TRON block.
        
        Parameters
        ----------
        block_identifier : int or str
            Block number or 'latest'.
            
        Returns
        -------
        Dict[str, Any]
            Block exploration report.
        """
        try:
            logger.info(f"Exploring TRON block: {block_identifier}")
            report = self.block_service.get_block_report(block_identifier)
            logger.info("TRON block exploration completed successfully.")
            return report
        except Exception as e:
            logger.error(f"TRON block exploration failed: {e}")
            raise
    
    # ================================================================
    # TRANSACTION OPERATIONS
    # ================================================================
    
    def transaction_analyzer(self, tx_hash: str) -> Dict[str, Any]:
        """
        Analyze a TRON transaction.
        
        Parameters
        ----------
        tx_hash : str
            TRON transaction hash.
            
        Returns
        -------
        Dict[str, Any]
            Transaction analysis report.
        """
        try:
            logger.info(f"Analyzing TRON transaction: {tx_hash}")
            report = self.transaction_service.get_transaction_report(tx_hash)
            logger.info("TRON transaction analysis completed successfully.")
            return report
        except Exception as e:
            logger.error(f"TRON transaction analysis failed: {e}")
            raise
    
    # ================================================================
    # NODE OPERATIONS
    # ================================================================
    
    def node_validator(self, rpc_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate a TRON node.
        
        Parameters
        ----------
        rpc_url : str, optional
            RPC URL to validate. If None, validates the default node.
            
        Returns
        -------
        Dict[str, Any]
            Node validation report.
        """
        try:
            logger.info(f"Validating TRON node: {rpc_url or 'default'}")
            
            # Import here to avoid circular imports
            from tron.node_validator import validate_node
            
            report = validate_node(rpc_url)
            logger.info("TRON node validation completed successfully.")
            return report
        except Exception as e:
            logger.error(f"TRON node validation failed: {e}")
            raise
    
    def compare_nodes(self, node_urls: List[str]) -> Dict[str, Any]:
        """
        Compare multiple TRON nodes.
        
        Parameters
        ----------
        node_urls : List[str]
            List of RPC URLs to compare.
            
        Returns
        -------
        Dict[str, Any]
            Node comparison report.
        """
        try:
            logger.info(f"Comparing {len(node_urls)} TRON nodes")
            
            # Import here to avoid circular imports
            from tron.node_validator import compare_nodes
            
            report = compare_nodes(node_urls)
            logger.info("TRON node comparison completed successfully.")
            return report
        except Exception as e:
            logger.error(f"TRON node comparison failed: {e}")
            raise
    
    # ================================================================
    # ENERGY OPERATIONS
    # ================================================================
    
    def energy_optimizer(self) -> Dict[str, Any]:
        """
        Get TRON energy price.
        
        Returns
        -------
        Dict[str, Any]
            Energy price information.
        """
        try:
            logger.info("Getting TRON energy price")
            
            # Import here to avoid circular imports
            from tron.gas import get_energy_optimizer
            
            optimizer = get_energy_optimizer()
            report = optimizer.get_energy_price()
            logger.info("TRON energy price retrieved successfully.")
            return report
        except Exception as e:
            logger.error(f"TRON energy optimization failed: {e}")
            raise
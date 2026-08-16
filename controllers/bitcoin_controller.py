"""
Universal Blockchain Platform (UBP)
Module: Bitcoin Controller
Purpose: Coordinates Bitcoin blockchain operations
Author: UBP Engineering Team
Version: 2.0.0
"""
from typing import Dict, Any, Optional, List
from core.logger import get_logger
from services.bitcoin.wallet_service import BitcoinWalletService
from services.bitcoin.block_service import BitcoinBlockService
from services.bitcoin.transaction_service import BitcoinTransactionService
from exceptions.blockchain_exceptions import UBPException

logger = get_logger(__name__)


class BitcoinController:
    """
    Controller responsible for Bitcoin blockchain operations.
    """
    
    def __init__(self):
        """Initialize the Bitcoin Controller."""
        self.wallet_service = BitcoinWalletService()
        self.block_service = BitcoinBlockService()
        self.transaction_service = BitcoinTransactionService()
        logger.info("BitcoinController initialized.")
    
    # ================================================================
    # WALLET OPERATIONS
    # ================================================================
    
    def wallet_inspector(self, address: str) -> Dict[str, Any]:
        """
        Inspect a Bitcoin wallet.
        
        Parameters
        ----------
        address : str
            Bitcoin wallet address.
            
        Returns
        -------
        Dict[str, Any]
            Wallet inspection report.
        """
        try:
            logger.info(f"Inspecting Bitcoin wallet: {address}")
            report = self.wallet_service.get_wallet_report(address)
            logger.info("Bitcoin wallet inspection completed successfully.")
            return report
        except Exception as e:
            logger.error(f"Bitcoin wallet inspection failed: {e}")
            raise
    
    # ================================================================
    # BLOCK OPERATIONS
    # ================================================================
    
    def block_explorer(self, block_identifier: Any) -> Dict[str, Any]:
        """
        Explore a Bitcoin block.
        
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
            logger.info(f"Exploring Bitcoin block: {block_identifier}")
            report = self.block_service.get_block_report(block_identifier)
            logger.info("Bitcoin block exploration completed successfully.")
            return report
        except Exception as e:
            logger.error(f"Bitcoin block exploration failed: {e}")
            raise
    
    # ================================================================
    # TRANSACTION OPERATIONS
    # ================================================================
    
    def transaction_analyzer(self, tx_hash: str) -> Dict[str, Any]:
        """
        Analyze a Bitcoin transaction.
        
        Parameters
        ----------
        tx_hash : str
            Bitcoin transaction hash.
            
        Returns
        -------
        Dict[str, Any]
            Transaction analysis report.
        """
        try:
            logger.info(f"Analyzing Bitcoin transaction: {tx_hash}")
            report = self.transaction_service.get_transaction_report(tx_hash)
            logger.info("Bitcoin transaction analysis completed successfully.")
            return report
        except Exception as e:
            logger.error(f"Bitcoin transaction analysis failed: {e}")
            raise
    
    # ================================================================
    # NODE OPERATIONS
    # ================================================================
    
    def node_validator(self, rpc_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate a Bitcoin node.
        
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
            logger.info(f"Validating Bitcoin node: {rpc_url or 'default'}")
            
            # Import here to avoid circular imports
            from bitcoin.node_validator import validate_node
            
            report = validate_node(rpc_url)
            logger.info("Bitcoin node validation completed successfully.")
            return report
        except Exception as e:
            logger.error(f"Bitcoin node validation failed: {e}")
            raise
    
    def compare_nodes(self, node_urls: List[str]) -> Dict[str, Any]:
        """
        Compare multiple Bitcoin nodes.
        
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
            logger.info(f"Comparing {len(node_urls)} Bitcoin nodes")
            
            # Import here to avoid circular imports
            from bitcoin.node_validator import compare_nodes
            
            report = compare_nodes(node_urls)
            logger.info("Bitcoin node comparison completed successfully.")
            return report
        except Exception as e:
            logger.error(f"Bitcoin node comparison failed: {e}")
            raise
    
    # ================================================================
    # FEE OPERATIONS
    # ================================================================
    
    def fee_optimizer(self) -> Dict[str, Any]:
        """
        Get Bitcoin fee estimates.
        
        Returns
        -------
        Dict[str, Any]
            Fee estimates (slow, standard, fast).
        """
        try:
            logger.info("Getting Bitcoin fee estimates")
            
            # Import here to avoid circular imports
            from bitcoin.gas import get_fee_optimizer
            
            optimizer = get_fee_optimizer()
            report = optimizer.get_fee_estimate()
            logger.info("Bitcoin fee estimates retrieved successfully.")
            return report
        except Exception as e:
            logger.error(f"Bitcoin fee optimization failed: {e}")
            raise
    
    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get Bitcoin connection status.
        
        Returns
        -------
        Dict[str, Any]
            Connection status information.
        """
        try:
            from bitcoin.connection import get_connection
            
            client = get_connection()
            return {
                "connected": True,
                "blockchain": "bitcoin",
                "network": "mainnet"
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }
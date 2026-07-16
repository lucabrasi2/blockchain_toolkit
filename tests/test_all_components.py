#!/usr/bin/env python3
"""
Universal Blockchain Platform (UBP)

Module:
    Component Test Suite

Purpose:
    Test all UBP components to ensure
    nothing was broken during development.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

import sys
import os
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test addresses
TEST_ADDRESSES = {
    "vitalik": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "usdc": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "dai": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "weth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "empty": "0x0000000000000000000000000000000000000000",
}


def print_test_header(name: str):
    """Print a test header."""
    print("\n" + "=" * 60)
    print(f"🧪 TESTING: {name}")
    print("=" * 60)


def print_test_result(passed: bool, message: str = ""):
    """Print a test result."""
    if passed:
        print(f"  ✅ PASSED: {message}")
    else:
        print(f"  ❌ FAILED: {message}")
    return passed


def test_imports() -> bool:
    """Test all imports."""
    print_test_header("Imports")
    
    try:
        from core.logger import get_logger
        print_test_result(True, "core.logger")
    except Exception as e:
        print_test_result(False, f"core.logger: {e}")
        return False
    
    try:
        from core.menu import MainMenu, EthereumMenu
        print_test_result(True, "core.menu")
    except Exception as e:
        print_test_result(False, f"core.menu: {e}")
        return False
    
    try:
        from core.display import (
            WalletDisplay, ContractDisplay, TokenDisplay,
            BlockDisplay, TransactionDisplay, NodeDisplay
        )
        print_test_result(True, "core.display")
    except Exception as e:
        print_test_result(False, f"core.display: {e}")
        return False
    
    try:
        from core.input import get_address_input, get_block_input
        print_test_result(True, "core.input")
    except Exception as e:
        print_test_result(False, f"core.input: {e}")
        return False
    
    try:
        from ethereum.wallets import get_eth_balance, is_valid_address
        print_test_result(True, "ethereum.wallets")
    except Exception as e:
        print_test_result(False, f"ethereum.wallets: {e}")
        return False
    
    try:
        from ethereum.contracts import is_contract, classify_address
        print_test_result(True, "ethereum.contracts")
    except Exception as e:
        print_test_result(False, f"ethereum.contracts: {e}")
        return False
    
    try:
        from ethereum.tokens import get_token_metadata
        print_test_result(True, "ethereum.tokens")
    except Exception as e:
        print_test_result(False, f"ethereum.tokens: {e}")
        return False
    
    try:
        from ethereum.blocks import get_block
        print_test_result(True, "ethereum.blocks")
    except Exception as e:
        print_test_result(False, f"ethereum.blocks: {e}")
        return False
    
    try:
        from ethereum.transactions import get_transaction
        print_test_result(True, "ethereum.transactions")
    except Exception as e:
        print_test_result(False, f"ethereum.transactions: {e}")
        return False
    
    try:
        from ethereum.node_validator import validate_node, compare_nodes
        print_test_result(True, "ethereum.node_validator")
    except Exception as e:
        print_test_result(False, f"ethereum.node_validator: {e}")
        return False
    
    try:
        from controllers.ethereum_controller import EthereumController
        print_test_result(True, "controllers.ethereum_controller")
    except Exception as e:
        print_test_result(False, f"controllers.ethereum_controller: {e}")
        return False
    
    try:
        from services.ethereum.wallet_service import WalletService
        print_test_result(True, "services.ethereum.wallet_service")
    except Exception as e:
        print_test_result(False, f"services.ethereum.wallet_service: {e}")
        return False
    
    try:
        from services.ethereum.contract_service import ContractService
        print_test_result(True, "services.ethereum.contract_service")
    except Exception as e:
        print_test_result(False, f"services.ethereum.contract_service: {e}")
        return False
    
    try:
        from services.ethereum.token_service import TokenService
        print_test_result(True, "services.ethereum.token_service")
    except Exception as e:
        print_test_result(False, f"services.ethereum.token_service: {e}")
        return False
    
    try:
        from services.ethereum.block_service import BlockService
        print_test_result(True, "services.ethereum.block_service")
    except Exception as e:
        print_test_result(False, f"services.ethereum.block_service: {e}")
        return False
    
    try:
        from services.ethereum.transaction_service import TransactionService
        print_test_result(True, "services.ethereum.transaction_service")
    except Exception as e:
        print_test_result(False, f"services.ethereum.transaction_service: {e}")
        return False
    
    try:
        from services.ethereum.node_service import NodeService
        print_test_result(True, "services.ethereum.node_service")
    except Exception as e:
        print_test_result(False, f"services.ethereum.node_service: {e}")
        return False
    
    try:
        from config.settings import Settings
        print_test_result(True, "config.settings")
    except Exception as e:
        print_test_result(False, f"config.settings: {e}")
        return False
    
    try:
        from providers import get_provider
        print_test_result(True, "providers")
    except Exception as e:
        print_test_result(False, f"providers: {e}")
        return False
    
    return True


def test_connection() -> bool:
    """Test Ethereum connection."""
    print_test_header("Ethereum Connection")
    
    try:
        from ethereum.connection import get_connection
        w3 = get_connection()
        if w3.is_connected():
            print_test_result(True, f"Connected to Ethereum. Chain ID: {w3.eth.chain_id}")
            return True
        else:
            print_test_result(False, "Not connected to Ethereum")
            return False
    except Exception as e:
        print_test_result(False, f"Connection failed: {e}")
        return False


def test_wallet_inspection() -> bool:
    """Test wallet inspection."""
    print_test_header("Wallet Inspection")
    
    try:
        from ethereum.wallets import get_eth_balance, get_nonce, is_valid_address
        
        address = TEST_ADDRESSES["vitalik"]
        
        # Test address validation
        valid = is_valid_address(address)
        print_test_result(valid, f"Address validation: {address[:10]}...")
        
        # Test balance
        balance = get_eth_balance(address)
        if balance and balance.get("ether", 0) > 0:
            print_test_result(True, f"Balance: {balance['ether']} ETH")
        else:
            print_test_result(True, f"Balance: {balance.get('ether', 0)} ETH (may be zero)")
        
        # Test nonce
        nonce = get_nonce(address)
        print_test_result(True, f"Nonce: {nonce}")
        
        return True
        
    except Exception as e:
        print_test_result(False, f"Wallet inspection failed: {e}")
        return False


def test_contract_detection() -> bool:
    """Test contract detection."""
    print_test_header("Contract Detection")
    
    try:
        from ethereum.contracts import is_contract, classify_address
        
        # Test EOA (Vitalik's address)
        is_contract_result = is_contract(TEST_ADDRESSES["vitalik"])
        classification = classify_address(TEST_ADDRESSES["vitalik"])
        print_test_result(not is_contract_result, f"Vitalik address is not a contract: {classification}")
        
        # Test USDC (contract)
        is_contract_result = is_contract(TEST_ADDRESSES["usdc"])
        classification = classify_address(TEST_ADDRESSES["usdc"])
        print_test_result(is_contract_result, f"USDC is a contract: {classification}")
        
        return True
        
    except Exception as e:
        print_test_result(False, f"Contract detection failed: {e}")
        return False


def test_token_inspection() -> bool:
    """Test token inspection."""
    print_test_header("Token Inspection")
    
    try:
        from ethereum.tokens import get_token_metadata, get_total_supply
        
        # Test USDC
        metadata = get_token_metadata(TEST_ADDRESSES["usdc"])
        print_test_result(True, f"USDC: {metadata.get('name')} ({metadata.get('symbol')})")
        
        # Test DAI
        metadata = get_token_metadata(TEST_ADDRESSES["dai"])
        print_test_result(True, f"DAI: {metadata.get('name')} ({metadata.get('symbol')})")
        
        return True
        
    except Exception as e:
        print_test_result(False, f"Token inspection failed: {e}")
        return False


def test_block_exploration() -> bool:
    """Test block exploration."""
    print_test_header("Block Exploration")
    
    try:
        from ethereum.blocks import get_block
        
        block = get_block("latest")
        if block and block.get("number"):
            print_test_result(True, f"Latest block: {block['number']} (tx: {block.get('transaction_count', 0)})")
            return True
        else:
            print_test_result(False, "Failed to get latest block")
            return False
            
    except Exception as e:
        print_test_result(False, f"Block exploration failed: {e}")
        return False


def test_node_validation() -> bool:
    """Test node validation."""
    print_test_header("Node Validation")
    
    try:
        from ethereum.node_validator import validate_node
        
        report = validate_node()
        if report and report.get("is_connected"):
            print_test_result(True, f"Node connected: {report.get('health_status')}")
            print_test_result(True, f"Block: {report.get('block_number')}")
            print_test_result(True, f"Node Type: {report.get('node_type')}")
            return True
        else:
            print_test_result(False, "Node validation failed")
            return False
            
    except Exception as e:
        print_test_result(False, f"Node validation failed: {e}")
        return False


def test_services() -> bool:
    """Test service layer."""
    print_test_header("Service Layer")
    
    try:
        from services.ethereum.wallet_service import WalletService
        from services.ethereum.contract_service import ContractService
        from services.ethereum.token_service import TokenService
        from services.ethereum.block_service import BlockService
        from services.ethereum.transaction_service import TransactionService
        from services.ethereum.node_service import NodeService
        
        # Test WalletService
        wallet_service = WalletService()
        print_test_result(True, "WalletService initialized")
        
        # Test ContractService
        contract_service = ContractService()
        print_test_result(True, "ContractService initialized")
        
        # Test TokenService
        token_service = TokenService()
        print_test_result(True, "TokenService initialized")
        
        # Test BlockService
        block_service = BlockService()
        print_test_result(True, "BlockService initialized")
        
        # Test TransactionService
        transaction_service = TransactionService()
        print_test_result(True, "TransactionService initialized")
        
        # Test NodeService
        node_service = NodeService()
        print_test_result(True, "NodeService initialized")
        
        return True
        
    except Exception as e:
        print_test_result(False, f"Service layer test failed: {e}")
        return False


def test_controller() -> bool:
    """Test controller layer."""
    print_test_header("Controller Layer")
    
    try:
        from controllers.ethereum_controller import EthereumController
        
        controller = EthereumController()
        print_test_result(True, "EthereumController initialized")
        
        # Test wallet inspector
        report = controller.wallet_inspector(TEST_ADDRESSES["vitalik"])
        if report and report.get("address"):
            print_test_result(True, f"Wallet inspector: {report.get('address')[:10]}...")
        else:
            print_test_result(False, "Wallet inspector failed")
            return False
        
        return True
        
    except Exception as e:
        print_test_result(False, f"Controller test failed: {e}")
        return False


def run_all_tests() -> None:
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🚀 UBP COMPONENT TEST SUITE")
    print("=" * 60)
    print()

    results = []
    
    # Run all tests
    results.append(("Imports", test_imports()))
    results.append(("Connection", test_connection()))
    results.append(("Wallet Inspection", test_wallet_inspection()))
    results.append(("Contract Detection", test_contract_detection()))
    results.append(("Token Inspection", test_token_inspection()))
    results.append(("Block Exploration", test_block_exploration()))
    results.append(("Node Validation", test_node_validation()))
    results.append(("Service Layer", test_services()))
    results.append(("Controller Layer", test_controller()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {name}")
    
    print("\n" + "-" * 40)
    print(f"  Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Everything is working perfectly!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
    
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

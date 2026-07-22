"""
Universal Blockchain Platform (UBP)

Module:
    API Models

Purpose:
    Pydantic models for API requests and responses.

Author: Jaramogi Diddy
Project: Universal Blockchain Platform (UBP)
Version: 2.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime


# ============ Request Models ============

class AddressRequest(BaseModel):
    """Request model for address-based operations."""
    address: str = Field(..., description="Blockchain address")
    chain_id: Optional[int] = Field(1, description="Chain ID (1 for Ethereum mainnet)")


class BlockRequest(BaseModel):
    """Request model for block operations."""
    block_identifier: Any = Field(..., description="Block number, hash, or 'latest'")
    chain_id: Optional[int] = Field(1, description="Chain ID")


class TransactionRequest(BaseModel):
    """Request model for transaction operations."""
    tx_hash: str = Field(..., description="Transaction hash")
    chain_id: Optional[int] = Field(1, description="Chain ID")


class CompareNodesRequest(BaseModel):
    """Request model for node comparison."""
    node_urls: List[str] = Field(..., description="List of node RPC URLs to compare")


class GasEstimateRequest(BaseModel):
    """Request model for gas estimation."""
    gas_limit: Optional[int] = Field(21000, description="Gas limit for the transaction")
    gas_price_gwei: Optional[float] = Field(None, description="Gas price in Gwei (optional)")


# ============ Response Models ============

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Overall status (healthy/degraded/unhealthy)")
    timestamp: str = Field(..., description="Current timestamp")
    database: str = Field(..., description="Database status (healthy/unhealthy)")
    blockchain: str = Field(..., description="Blockchain network")
    chain_id: int = Field(..., description="Chain ID")


class WalletResponse(BaseModel):
    """Wallet inspection response."""
    address: str = Field(..., description="Wallet address")
    balance_eth: float = Field(0.0, description="Balance in ETH")
    balance_wei: int = Field(0, description="Balance in Wei")
    nonce: int = Field(0, description="Transaction nonce")
    is_contract: bool = Field(False, description="Whether address is a contract")
    classification: str = Field("Unknown", description="Address classification (EOA/CONTRACT/ERC20/etc)")
    transaction_count: Optional[int] = Field(0, description="Total transaction count")
    token_balances: Optional[List[Dict[str, Any]]] = Field([], description="List of token balances")


class ContractResponse(BaseModel):
    """Contract inspection response."""
    address: str = Field(..., description="Contract address")
    is_contract: bool = Field(..., description="Whether address is a contract")
    classification: str = Field(..., description="Contract classification")
    contract_type: str = Field(..., description="Contract type (ERC20, ERC721, etc)")
    name: Optional[str] = Field(None, description="Contract name")
    symbol: Optional[str] = Field(None, description="Contract symbol")
    decimals: Optional[int] = Field(None, description="Token decimals")
    total_supply: Optional[str] = Field(None, description="Total supply")
    owner: Optional[str] = Field(None, description="Contract owner address")
    standard: Optional[str] = Field(None, description="Token standard")
    bytecode_size: int = Field(0, description="Bytecode size in bytes")
    balance_eth: float = Field(0.0, description="Contract balance in ETH")


class TokenResponse(BaseModel):
    """Token inspection response."""
    address: str = Field(..., description="Token address")
    name: str = Field(..., description="Token name")
    symbol: str = Field(..., description="Token symbol")
    decimals: int = Field(18, description="Token decimals")
    total_supply: Optional[str] = Field(None, description="Total supply")
    is_token: bool = Field(..., description="Whether it's a valid token")


class BlockResponse(BaseModel):
    """Block exploration response."""
    number: Optional[int] = Field(None, description="Block number")
    hash: Optional[str] = Field(None, description="Block hash")
    parent_hash: Optional[str] = Field(None, description="Parent block hash")
    timestamp: Optional[int] = Field(None, description="Block timestamp")
    miner: Optional[str] = Field(None, description="Block miner/validator")
    difficulty: Optional[int] = Field(None, description="Block difficulty")
    gas_used: Optional[int] = Field(None, description="Gas used")
    gas_limit: Optional[int] = Field(None, description="Gas limit")
    transaction_count: int = Field(0, description="Number of transactions")
    transactions: List[Any] = Field([], description="List of transaction hashes")


class TransactionResponse(BaseModel):
    """Transaction analysis response."""
    hash: Optional[str] = Field(None, description="Transaction hash")
    block_number: Optional[int] = Field(None, description="Block number")
    from_address: Optional[str] = Field(None, description="Sender address")
    to_address: Optional[str] = Field(None, description="Receiver address")
    value_eth: float = Field(0.0, description="Transaction value in ETH")
    gas_used: Optional[int] = Field(None, description="Gas used")
    gas_price: Optional[int] = Field(None, description="Gas price")
    status: bool = Field(..., description="Transaction status (success/failed)")
    logs: List[Any] = Field([], description="Transaction logs")


class GasPriceResponse(BaseModel):
    """Gas price response."""
    wei: int = Field(..., description="Gas price in Wei")
    gwei: float = Field(..., description="Gas price in Gwei")
    eth: float = Field(..., description="Gas price in ETH")


class GasEstimateResponse(BaseModel):
    """Gas estimate response."""
    gas_limit: int = Field(..., description="Gas limit")
    gas_price_gwei: float = Field(..., description="Gas price in Gwei")
    total_cost_wei: int = Field(..., description="Total cost in Wei")
    total_cost_eth: float = Field(..., description="Total cost in ETH")
    total_cost_usd: float = Field(..., description="Total cost in USD (approximate)")


class NodeValidationResponse(BaseModel):
    """Node validation response."""
    is_connected: bool = Field(..., description="Whether node is connected")
    is_syncing: bool = Field(..., description="Whether node is syncing")
    node_type: str = Field(..., description="Node type (Full/Archive/Light)")
    chain_id: int = Field(..., description="Chain ID")
    block_number: int = Field(..., description="Current block number")
    peer_count: int = Field(..., description="Number of peers")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    health_status: str = Field(..., description="Health status (Healthy/Degraded/Unhealthy)")
    issues: List[str] = Field([], description="List of issues found")


class WebSocketMessage(BaseModel):
    """WebSocket message structure."""
    type: str = Field(..., description="Message type")
    data: Any = Field(..., description="Message data")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Timestamp")
    channel: str = Field("global", description="Channel name")


class ProviderInfoResponse(BaseModel):
    """Provider information response."""
    name: str = Field(..., description="Provider name")
    http_url: str = Field(..., description="HTTP RPC URL")
    ws_url: Optional[str] = Field(None, description="WebSocket URL")
    available: bool = Field(..., description="Whether provider is available")
    config: Dict[str, Any] = Field(..., description="Provider configuration")


class BlockchainInfoResponse(BaseModel):
    """Blockchain information response."""
    name: str = Field(..., description="Blockchain name")
    chain_id: int = Field(..., description="Chain ID")
    network: str = Field(..., description="Network name")
    current_block: int = Field(..., description="Current block number")
    connected: bool = Field(..., description="Connection status")
    provider: str = Field(..., description="Active provider")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    code: Optional[int] = Field(None, description="Error code")
    details: Optional[Any] = Field(None, description="Additional error details")


# ============ WebSocket Models ============

class WebSocketSubscribeRequest(BaseModel):
    """WebSocket subscription request."""
    type: str = Field("subscribe", description="Message type")
    channel: str = Field(..., description="Channel to subscribe to")


class WebSocketUnsubscribeRequest(BaseModel):
    """WebSocket unsubscription request."""
    type: str = Field("unsubscribe", description="Message type")
    channel: str = Field(..., description="Channel to unsubscribe from")


class WebSocketPingRequest(BaseModel):
    """WebSocket ping request."""
    type: str = Field("ping", description="Message type")
    timestamp: Optional[str] = Field(None, description="Ping timestamp")


class WebSocketPongResponse(BaseModel):
    """WebSocket pong response."""
    type: str = Field("pong", description="Message type")
    data: Dict[str, str] = Field(..., description="Pong data")


class WebSocketErrorResponse(BaseModel):
    """WebSocket error response."""
    type: str = Field("error", description="Message type")
    data: str = Field(..., description="Error message")


# ============ Bitcoin Specific Models ============

class BitcoinWalletResponse(BaseModel):
    """Bitcoin wallet inspection response."""
    address: str = Field(..., description="Bitcoin address")
    balance_btc: float = Field(0.0, description="Balance in BTC")
    balance_satoshis: int = Field(0, description="Balance in satoshis")
    is_valid: bool = Field(..., description="Whether address is valid")
    is_script: bool = Field(False, description="Whether it's a script address")
    is_witness: bool = Field(False, description="Whether it's a witness address")
    script_type: str = Field("Legacy", description="Script type")
    classification: str = Field("Bitcoin Address", description="Address classification")
    transaction_count: Optional[int] = Field(0, description="Transaction count")


class BitcoinBlockResponse(BaseModel):
    """Bitcoin block exploration response."""
    number: Optional[int] = Field(None, description="Block height")
    hash: Optional[str] = Field(None, description="Block hash")
    previous_hash: Optional[str] = Field(None, description="Previous block hash")
    next_hash: Optional[str] = Field(None, description="Next block hash")
    timestamp: Optional[int] = Field(None, description="Block timestamp")
    transaction_count: int = Field(0, description="Number of transactions")
    size: Optional[int] = Field(None, description="Block size in bytes")
    weight: Optional[int] = Field(None, description="Block weight")
    difficulty: Optional[float] = Field(None, description="Block difficulty")
    transactions: List[str] = Field([], description="List of transaction hashes")


# ============ TRON Specific Models ============

class TronWalletResponse(BaseModel):
    """TRON wallet inspection response."""
    address: str = Field(..., description="TRON address")
    balance_trx: float = Field(0.0, description="Balance in TRX")
    balance_sun: int = Field(0, description="Balance in SUN")
    is_contract: bool = Field(False, description="Whether address is a contract")
    classification: str = Field("Unknown", description="Address classification")
    energy: Optional[int] = Field(0, description="Energy balance")
    bandwidth: Optional[int] = Field(0, description="Bandwidth balance")


class TronContractResponse(BaseModel):
    """TRON contract inspection response."""
    address: str = Field(..., description="Contract address")
    is_contract: bool = Field(..., description="Whether address is a contract")
    classification: str = Field(..., description="Contract classification")
    name: Optional[str] = Field(None, description="Contract name")
    symbol: Optional[str] = Field(None, description="Contract symbol")
    decimals: Optional[int] = Field(None, description="Token decimals")
    total_supply: Optional[str] = Field(None, description="Total supply")


# ============ Response Envelopes ============

class ApiResponse(BaseModel):
    """Generic API response wrapper."""
    success: bool = Field(..., description="Whether request was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Response timestamp")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(1, description="Current page")
    per_page: int = Field(20, description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

"""
===============================================================================
Universal Blockchain Platform (UBP)

Module
------
services.wallet_service

Purpose
-------
Multi-chain wallet management service for users.

Author
------
Jaramogi Diddy

Project
-------
Universal Blockchain Platform (UBP)

Version
-------
2.0 Enterprise
===============================================================================
"""

import uuid
import secrets
import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.database import get_db_manager
from database.models import User, Wallet, UserTransaction
from core.logger import get_logger

logger = get_logger(__name__)


class WalletService:
    """Multi-chain wallet management service."""

    def __init__(self):
        self.db = get_db_manager()
        self._init_providers()

    def _init_providers(self):
        """Initialize blockchain providers."""
        try:
            from providers import get_provider
            self.eth_provider = get_provider("alchemy")
        except:
            try:
                from providers import get_provider
                self.eth_provider = get_provider("public")
            except:
                self.eth_provider = None
                logger.warning("Ethereum provider not available")

        try:
            from providers.tron import TronProvider
            from providers.config import ProviderConfig
            self.tron_provider = TronProvider(
                ProviderConfig(provider="tron", network="mainnet")
            )
        except Exception as e:
            self.tron_provider = None
            logger.warning(f"TRON provider not available: {e}")

        try:
            from providers.bitcoin import BitcoinProvider
            from providers.config import ProviderConfig
            self.btc_provider = BitcoinProvider(
                ProviderConfig(provider="bitcoin", network="mainnet")
            )
        except Exception as e:
            self.btc_provider = None
            logger.warning(f"Bitcoin provider not available: {e}")

    def generate_seed_phrase(self, strength: int = 256) -> str:
        """
        Generate a BIP-39 seed phrase.

        Parameters
        ----------
        strength : int
            Entropy strength (128, 160, 192, 224, or 256).

        Returns
        -------
        str
            Space-separated mnemonic phrase.
        """
        try:
            from wallets.crypto.mnemonic import Bip39Mnemonic
            return Bip39Mnemonic.generate(strength)
        except ImportError:
            # Fallback: generate a simple random phrase
            logger.warning("BIP-39 not available, using fallback")
            words = ["abandon", "ability", "able", "about", "above", "absent",
                     "absorb", "abstract", "absurd", "abuse", "access", "accident"]
            return " ".join(secrets.choice(words) for _ in range(12))

    def _derive_private_key_from_mnemonic(self, mnemonic: str) -> bytes:
        """Derive private key from mnemonic (simplified)."""
        # In production, use proper BIP-44 derivation
        # This is a placeholder for testing
        return hashlib.sha256(mnemonic.encode()).digest()[:32]

    def _derive_public_key(self, private_key: bytes) -> bytes:
        """Derive public key from private key (simplified)."""
        # In production, use proper secp256k1
        # This is a placeholder for testing
        return hashlib.sha256(private_key).digest()

    def _derive_address(self, blockchain: str, private_key: bytes) -> Optional[str]:
        """Derive blockchain-specific address from private key."""
        try:
            public_key = self._derive_public_key(private_key)

            if blockchain == "ethereum":
                from eth_account import Account
                Account.enable_unaudited_hdwallet_features()
                account = Account.from_key(private_key)
                return account.address

            elif blockchain == "bitcoin":
                import base58
                # Simplified Bitcoin address derivation
                public_key_hash = hashlib.sha256(public_key).digest()
                ripemd160 = hashlib.new('ripemd160')
                ripemd160.update(public_key_hash)
                hashed = ripemd160.digest()
                network_byte = b'\x00' + hashed
                checksum = hashlib.sha256(hashlib.sha256(network_byte).digest()).digest()[:4]
                return base58.b58encode(network_byte + checksum).decode()

            elif blockchain == "tron":
                import base58
                public_key_hash = hashlib.sha256(public_key).digest()
                network_byte = b'\x41' + public_key_hash[:20]
                checksum = hashlib.sha256(hashlib.sha256(network_byte).digest()).digest()[:4]
                return base58.b58encode(network_byte + checksum).decode()

            else:
                logger.error(f"Unsupported blockchain: {blockchain}")
                return None

        except Exception as e:
            logger.error(f"Error deriving address: {e}")
            return None

    def _get_encryption_key(self, user_id: str) -> str:
        """Get encryption key for a user."""
        return f"user_{user_id}_encryption_key"

    def create_wallet(self, user_id: uuid.UUID, blockchain: str, label: str = None) -> Optional[Dict[str, Any]]:
        """
        Create a new wallet for a user.

        Parameters
        ----------
        user_id : uuid.UUID
            User ID.
        blockchain : str
            Blockchain name (ethereum, bitcoin, tron).
        label : str, optional
            Wallet label.

        Returns
        -------
        Optional[Dict[str, Any]]
            Wallet information or None if failed.
        """
        try:
            # Generate seed phrase
            mnemonic = self.generate_seed_phrase()

            # Derive private key
            private_key = self._derive_private_key_from_mnemonic(mnemonic)

            # Derive address
            address = self._derive_address(blockchain, private_key)

            if not address:
                logger.error(f"Failed to derive address for {blockchain}")
                return None

            wallet_id = f"{blockchain}_{secrets.token_hex(8)}"

            with self.db.get_session() as session:
                # Convert user_id to UUID if it's a string
                if isinstance(user_id, str):
                    user_id = uuid.UUID(user_id)
                
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    logger.error(f"User not found: {user_id}")
                    return None

                # Check if user already has a wallet for this blockchain
                existing = session.query(Wallet).filter(
                    Wallet.user_id == user_id,
                    Wallet.blockchain == blockchain,
                    Wallet.is_active == True
                ).first()

                if existing:
                    logger.warning(f"User already has a {blockchain} wallet")
                    session.expunge(existing)
                    return self._wallet_to_dict(existing)

                # Create wallet
                wallet = Wallet(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    wallet_id=wallet_id,
                    blockchain=blockchain,
                    network="mainnet",
                    address=address,
                    public_key=private_key.hex()[:64],  # Simplified
                    encrypted_private_key=private_key.hex(),  # In production, encrypt this
                    encrypted_seed=mnemonic,  # In production, encrypt this
                    wallet_type="hd",
                    custody_type="non_custodial",
                    is_active=True,
                    label=label or f"{blockchain.capitalize()} Wallet",
                    created_at=datetime.utcnow(),
                )

                session.add(wallet)
                session.flush()
                session.refresh(wallet)
                session.expunge(wallet)

                logger.info(f"Wallet created: {wallet_id} for user {user_id} on {blockchain}")

                return self._wallet_to_dict(wallet)

        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            return None

    def get_user_wallets(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get all wallets for a user."""
        try:
            with self.db.get_session() as session:
                if isinstance(user_id, str):
                    user_id = uuid.UUID(user_id)
                    
                wallets = session.query(Wallet).filter(
                    Wallet.user_id == user_id,
                    Wallet.is_active == True
                ).all()

                result = []
                for wallet in wallets:
                    session.expunge(wallet)
                    result.append(self._wallet_to_dict(wallet))

                return result

        except Exception as e:
            logger.error(f"Error getting user wallets: {e}")
            return []

    def get_wallet_by_id(self, wallet_id: str) -> Optional[Dict[str, Any]]:
        """Get wallet by wallet_id."""
        try:
            with self.db.get_session() as session:
                wallet = session.query(Wallet).filter(
                    Wallet.wallet_id == wallet_id,
                    Wallet.is_active == True
                ).first()

                if wallet:
                    session.expunge(wallet)
                    return self._wallet_to_dict(wallet)

                return None

        except Exception as e:
            logger.error(f"Error getting wallet: {e}")
            return None

    def get_wallet_by_address(self, address: str, blockchain: str) -> Optional[Dict[str, Any]]:
        """Get wallet by address and blockchain."""
        try:
            with self.db.get_session() as session:
                wallet = session.query(Wallet).filter(
                    Wallet.address == address,
                    Wallet.blockchain == blockchain,
                    Wallet.is_active == True
                ).first()

                if wallet:
                    session.expunge(wallet)
                    return self._wallet_to_dict(wallet)

                return None

        except Exception as e:
            logger.error(f"Error getting wallet by address: {e}")
            return None

    def _wallet_to_dict(self, wallet: Wallet) -> Dict[str, Any]:
        """Convert Wallet object to dictionary."""
        return {
            "id": str(wallet.id),
            "wallet_id": wallet.wallet_id,
            "blockchain": wallet.blockchain,
            "network": wallet.network,
            "address": wallet.address,
            "label": wallet.label,
            "wallet_type": wallet.wallet_type,
            "custody_type": wallet.custody_type,
            "is_default": wallet.is_default,
            "is_active": wallet.is_active,
            "created_at": wallet.created_at.isoformat() if wallet.created_at else None,
            "last_used": wallet.last_used.isoformat() if wallet.last_used else None,
        }

    def get_wallet_balance(self, wallet_id: str) -> Dict[str, Any]:
        """Get balance for a wallet."""
        try:
            wallet_info = self.get_wallet_by_id(wallet_id)
            if not wallet_info:
                return {"error": "Wallet not found"}

            blockchain = wallet_info["blockchain"]
            address = wallet_info["address"]

            if blockchain == "ethereum" and self.eth_provider:
                w3 = self.eth_provider.web3
                balance_wei = w3.eth.get_balance(address)
                balance_eth = w3.from_wei(balance_wei, "ether")
                return {
                    "balance": float(balance_eth),
                    "symbol": "ETH",
                    "decimals": 18,
                    "address": address,
                }
            elif blockchain == "bitcoin":
                # Use blockchain.info public API for balance
                import requests
                try:
                    response = requests.get(
                        f"https://blockchain.info/q/addressbalance/{address}",
                        timeout=10
                    )
                    if response.status_code == 200:
                        balance_satoshis = int(response.text)
                        balance_btc = balance_satoshis / 100_000_000
                        return {
                            "balance": balance_btc,
                            "symbol": "BTC",
                            "decimals": 8,
                            "address": address,
                            "satoshis": balance_satoshis,
                        }
                    else:
                        return {"error": f"API returned status {response.status_code}"}
                except Exception as e:
                    logger.error(f"Error getting BTC balance from blockchain.info: {e}")
                    return {"error": str(e)}

            elif blockchain == "tron" and self.tron_provider:
                account = self.tron_provider.get_account(address)
                balance_sun = account.get("balance", 0)
                return {
                    "balance": balance_sun / 1_000_000,
                    "symbol": "TRX",
                    "decimals": 6,
                    "address": address,
                }

            return {"error": f"Provider not available for {blockchain}"}

        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {"error": str(e)}

    def get_wallet_report(self, wallet_id: str) -> Dict[str, Any]:
        """
        Get detailed wallet report including token holdings.

        Parameters
        ----------
        wallet_id : str
            UBP wallet identifier.

        Returns
        -------
        Dict[str, Any]
            Wallet report with balance, token holdings, and metadata.
        """
        try:
            # Get wallet from database
            wallet_info = self.get_wallet_by_id(wallet_id)
            if not wallet_info:
                return {"error": "Wallet not found"}

            blockchain = wallet_info.get("blockchain", "ethereum")
            address = wallet_info.get("address")

            # Start with basic wallet info
            result = {
                "address": address,
                "blockchain": blockchain,
                "network": wallet_info.get("network", "mainnet"),
                "label": wallet_info.get("label"),
                "wallet_id": wallet_id,
                "token_balances": [],
            }

            # Get balance
            balance = self.get_wallet_balance(wallet_id)
            if "error" not in balance:
                result.update({
                    "balance": balance.get("balance", 0),
                    "asset": balance.get("symbol", "ETH"),
                    "decimals": balance.get("decimals", 18),
                })

            # Get additional blockchain-specific info
            if blockchain == "ethereum" and self.eth_provider:
                try:
                    w3 = self.eth_provider.web3
                    result["nonce"] = w3.eth.get_transaction_count(address)
                    code = w3.eth.get_code(address)
                    result["is_contract"] = len(code) > 0
                    result["classification"] = "Contract" if result["is_contract"] else "EOA"
                    result["transaction_count"] = result.get("nonce", 0)
                except Exception as e:
                    logger.warning(f"Could not fetch Ethereum details: {e}")

            elif blockchain == "bitcoin":
                try:
                    import requests
                    response = requests.get(
                        f"https://blockchain.info/q/addressbalance/{address}",
                        timeout=10
                    )
                    if response.status_code == 200:
                        balance_satoshis = int(response.text)
                        result["transaction_count"] = 0
                    result["is_contract"] = False
                    result["classification"] = "Bitcoin Address"
                    result["nonce"] = 0
                except Exception as e:
                    logger.warning(f"Could not fetch Bitcoin details: {e}")

            elif blockchain == "tron" and self.tron_provider:
                try:
                    account = self.tron_provider.get_account(address)
                    result["energy"] = account.get("energy", 0)
                    result["bandwidth"] = account.get("bandwidth", 0)
                    result["is_contract"] = False
                    result["classification"] = "EOA"
                    result["nonce"] = 0
                    result["transaction_count"] = 0
                except Exception as e:
                    logger.warning(f"Could not fetch TRON details: {e}")

            # For token balances - would need to query token contracts
            # This is a placeholder for future implementation
            result["token_balances"] = []

            return result

        except Exception as e:
            logger.error(f"Error getting wallet report: {e}")
            return {"error": str(e)}

    @staticmethod
    def _normalize_transaction_status(status: Optional[str]) -> str:
        """Normalize database transaction states to the public history states."""
        normalized = (status or "pending").strip().lower()

        if normalized in {
            "confirmed",
            "complete",
            "completed",
            "success",
            "successful",
            "succeeded",
            "finalized",
            "finalised",
        }:
            return "confirmed"

        if normalized in {
            "failed",
            "failure",
            "error",
            "reverted",
            "rejected",
            "cancelled",
            "canceled",
        }:
            return "failed"

        return "pending"

    @staticmethod
    def _get_transaction_direction(
        wallet_address: Optional[str],
        from_address: Optional[str],
        to_address: Optional[str],
    ) -> str:
        """Classify a transaction as incoming, outgoing, or unknown."""
        wallet = (wallet_address or "").strip().lower()
        sender = (from_address or "").strip().lower()
        recipient = (to_address or "").strip().lower()

        if wallet and sender == wallet:
            return "outgoing"

        if wallet and recipient == wallet:
            return "incoming"

        return "unknown"

    @staticmethod
    def _serialize_datetime(value: Optional[datetime]) -> Optional[str]:
        """Serialize a datetime without changing the stored timezone semantics."""
        return value.isoformat() if value else None
    
    def get_transaction_history(
        self,
        wallet_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get normalized transaction history for a wallet.

        Each transaction exposes a stable presentation model containing:

        - ``status``: pending, confirmed, or failed
        - ``direction``: incoming, outgoing, or unknown
        - ``amount`` and ``asset``
        - ``fee`` and ``fee_asset``
        - ``confirmations``
        - ``created_at``
        - ``confirmed_at``
        - ``timestamp``

        The existing pagination contract is preserved for API/mobile callers.

        No blockchain state is inferred here. This method normalizes the
        transaction data already persisted by the wallet service.
        """

        try:

            # =================================================================
            # Validate Pagination
            # =================================================================

            if limit <= 0:

                return {
                    "error": "Limit must be greater than 0"
                }

            if offset < 0:

                return {
                    "error": "Offset cannot be negative"
                }

            # =================================================================
            # Retrieve Wallet
            # =================================================================

            wallet_info = self.get_wallet_by_id(
                wallet_id
            )

            if not wallet_info:

                return {
                    "error": "Wallet not found"
                }

            wallet_address = wallet_info.get(
                "address"
            )

            wallet_blockchain = wallet_info.get(
                "blockchain",
                "ethereum",
            )

            native_asset = self._get_native_asset(
                wallet_blockchain
            )

            # =================================================================
            # Query Transactions
            # =================================================================

            with self.db.get_session() as session:

                wallet = (
                    session
                    .query(Wallet)
                    .filter(
                        Wallet.wallet_id == wallet_id,
                        Wallet.is_active == True,
                    )
                    .first()
                )

                if not wallet:

                    return {
                        "error": "Wallet not found in database"
                    }

                query = (
                    session
                    .query(UserTransaction)
                    .filter(
                        UserTransaction.wallet_id == wallet.id
                    )
                )

                total = query.count()

                transactions = (
                    query
                    .order_by(
                        desc(
                            UserTransaction.created_at
                        )
                    )
                    .limit(limit)
                    .offset(offset)
                    .all()
                )

                # =============================================================
                # Normalize Transactions
                # =============================================================

                result = []

                for tx in transactions:

                    # ---------------------------------------------------------
                    # Status
                    # ---------------------------------------------------------

                    status = (
                        self
                        ._normalize_transaction_status(
                            tx.status
                        )
                    )

                    # ---------------------------------------------------------
                    # Direction
                    # ---------------------------------------------------------

                    direction = (
                        self
                        ._get_transaction_direction(
                            wallet_address,
                            tx.from_address,
                            tx.to_address,
                        )
                    )

                    # ---------------------------------------------------------
                    # Amount
                    # ---------------------------------------------------------

                    amount = (
                        float(tx.amount)
                        if tx.amount is not None
                        else 0
                    )

                    # ---------------------------------------------------------
                    # Fee
                    # ---------------------------------------------------------

                    fee = (
                        float(tx.fee)
                        if tx.fee is not None
                        else None
                    )

                    fee_asset = (
                        tx.fee_asset
                        or native_asset
                    )

                    # ---------------------------------------------------------
                    # Confirmations
                    # ---------------------------------------------------------

                    confirmations = int(
                        tx.confirmations or 0
                    )

                    # ---------------------------------------------------------
                    # Asset
                    # ---------------------------------------------------------

                    asset = (
                        tx.asset
                        or native_asset
                    )

                    # ---------------------------------------------------------
                    # Timestamps
                    # ---------------------------------------------------------

                    created_at = (
                        self._serialize_datetime(
                            tx.created_at
                        )
                    )

                    confirmed_at = (
                        self._serialize_datetime(
                            tx.confirmed_at
                        )
                    )

                    # ``timestamp`` remains an API-friendly alias for the
                    # transaction creation timestamp.
                    timestamp = created_at

                    # =========================================================
                    # Transaction Record
                    # =========================================================

                    result.append(
                        {
                            "id": str(tx.id),

                            "tx_hash": tx.tx_hash,

                            "blockchain": (
                                tx.blockchain
                                or wallet_blockchain
                            ),

                            "from_address": (
                                tx.from_address
                            ),

                            "to_address": (
                                tx.to_address
                            ),

                            "amount": amount,

                            "asset": asset,

                            # Status:
                            # pending / confirmed / failed
                            "status": status,

                            # Direction:
                            # incoming / outgoing / unknown
                            "direction": direction,

                            "is_incoming": (
                                direction == "incoming"
                            ),

                            "is_outgoing": (
                                direction == "outgoing"
                            ),

                            # Confirmation information
                            "confirmations": confirmations,

                            # Fee information
                            "fee": fee,

                            "fee_asset": fee_asset,

                            # Timestamp information
                            "created_at": created_at,

                            "confirmed_at": confirmed_at,

                            "timestamp": timestamp,
                        }
                    )

                # =============================================================
                # Pagination
                # =============================================================

                total_pages = (
                    (total + limit - 1) // limit
                    if total > 0
                    else 1
                )

                # =============================================================
                # Final Response
                # =============================================================

                return {
                    "transactions": result,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "total_pages": total_pages,
                }

        except Exception as e:

            logger.exception(
                "Error getting transaction history for wallet %s: %s",
                wallet_id,
                e,
            )

            return {
                "error": str(e)
            }
    def get_token_holdings(self, wallet_id: str) -> Dict[str, Any]:
        """
        Get token holdings for a wallet.

        Parameters
        ----------
        wallet_id : str
            UBP wallet identifier.

        Returns
        -------
        Dict[str, Any]
            Token holdings list.
        """
        try:
            # Get wallet from database
            wallet_info = self.get_wallet_by_id(wallet_id)
            if not wallet_info:
                return {"error": "Wallet not found"}

            blockchain = wallet_info.get("blockchain", "ethereum")
            address = wallet_info.get("address")

            tokens = []

            # For Ethereum, we could query ERC-20 tokens
            # This is a placeholder - in production, you'd:
            # 1. Get all token contracts the address has interacted with
            # 2. Query each contract for balance
            # 3. Get token metadata (name, symbol, decimals)
            if blockchain == "ethereum" and self.eth_provider:
                # Placeholder: Return known tokens with 0 balance
                # In production, you'd query the blockchain for actual token holdings
                known_tokens = [
                    {
                        "contract_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                        "name": "USD Coin",
                        "symbol": "USDC",
                        "decimals": 6,
                        "logo_url": "https://assets.coingecko.com/coins/images/6319/small/USD_Coin_icon.png",
                    },
                    {
                        "contract_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                        "name": "Dai Stablecoin",
                        "symbol": "DAI",
                        "decimals": 18,
                        "logo_url": "https://assets.coingecko.com/coins/images/9956/small/4943.png",
                    },
                    {
                        "contract_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                        "name": "Wrapped Ether",
                        "symbol": "WETH",
                        "decimals": 18,
                        "logo_url": "https://assets.coingecko.com/coins/images/2518/small/weth.png",
                    },
                ]

                # For each token, try to get balance
                for token in known_tokens:
                    try:
                        from ethereum.tokens import get_token_balance
                        balance = get_token_balance(token["contract_address"], address)
                        tokens.append({
                            "contract_address": token["contract_address"],
                            "name": token["name"],
                            "symbol": token["symbol"],
                            "decimals": token["decimals"],
                            "balance": balance if balance is not None else 0,
                            "balance_formatted": (balance / (10 ** token["decimals"])) if balance is not None else 0,
                            "logo_url": token.get("logo_url"),
                        })
                    except Exception as e:
                        logger.warning(f"Could not fetch balance for token {token['symbol']}: {e}")
                        tokens.append({
                            "contract_address": token["contract_address"],
                            "name": token["name"],
                            "symbol": token["symbol"],
                            "decimals": token["decimals"],
                            "balance": 0,
                            "balance_formatted": 0,
                            "logo_url": token.get("logo_url"),
                            "error": str(e),
                        })

            elif blockchain == "tron" and self.tron_provider:
                # Placeholder for TRC-20 tokens
                known_tokens = [
                    {
                        "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
                        "name": "Tether USD",
                        "symbol": "USDT",
                        "decimals": 6,
                        "logo_url": "https://assets.coingecko.com/coins/images/325/small/Tether.png",
                    },
                ]

                for token in known_tokens:
                    try:
                        from tron.contracts import get_trc20_balance
                        balance = get_trc20_balance(token["contract_address"], address)
                        tokens.append({
                            "contract_address": token["contract_address"],
                            "name": token["name"],
                            "symbol": token["symbol"],
                            "decimals": token["decimals"],
                            "balance": balance if balance is not None else 0,
                            "balance_formatted": (balance / (10 ** token["decimals"])) if balance is not None else 0,
                            "logo_url": token.get("logo_url"),
                        })
                    except Exception as e:
                        logger.warning(f"Could not fetch balance for token {token['symbol']}: {e}")
                        tokens.append({
                            "contract_address": token["contract_address"],
                            "name": token["name"],
                            "symbol": token["symbol"],
                            "decimals": token["decimals"],
                            "balance": 0,
                            "balance_formatted": 0,
                            "logo_url": token.get("logo_url"),
                            "error": str(e),
                        })

            elif blockchain == "bitcoin":
                # Bitcoin doesn't have tokens
                return {
                    "tokens": [],
                    "blockchain": "bitcoin",
                    "message": "Bitcoin does not support tokens",
                }

            return {
                "tokens": tokens,
                "blockchain": blockchain,
                "address": address,
                "total_tokens": len(tokens),
            }

        except Exception as e:
            logger.error(f"Error getting token holdings: {e}")
            return {"error": str(e)}

    def send_transaction(self, wallet_id: str, to_address: str, amount: float, asset: str = None) -> Dict[str, Any]:
        """
        Send a transaction from a wallet.

        Parameters
        ----------
        wallet_id : str
            Wallet ID.
        to_address : str
            Recipient address.
        amount : float
            Amount to send.
        asset : str, optional
            Asset symbol (ETH, BTC, TRX).

        Returns
        -------
        Dict[str, Any]
            Transaction result with tx_hash.
        """
        try:
            wallet_info = self.get_wallet_by_id(wallet_id)
            if not wallet_info:
                return {"error": "Wallet not found"}

            blockchain = wallet_info["blockchain"]
            address = wallet_info["address"]

            # Get the wallet from database
            with self.db.get_session() as session:
                wallet = session.query(Wallet).filter(
                    Wallet.wallet_id == wallet_id,
                    Wallet.is_active == True
                ).first()

                if not wallet:
                    return {"error": "Wallet not found in database"}

                # Decrypt private key (simplified for now)
                private_key_hex = wallet.encrypted_private_key
                if not private_key_hex:
                    return {"error": "Private key not available"}

                private_key = bytes.fromhex(private_key_hex)

            # Send based on blockchain
            if blockchain == "ethereum":
                result = self._send_eth_transaction(address, to_address, amount, private_key)
            elif blockchain == "bitcoin":
                result = self._send_btc_transaction(address, to_address, amount, private_key)
            elif blockchain == "tron":
                result = self._send_trx_transaction(address, to_address, amount, private_key)
            else:
                return {"error": f"Unsupported blockchain: {blockchain}"}

            if "error" in result:
                return result

            # Save transaction to database
            with self.db.get_session() as session:
                wallet = session.query(Wallet).filter(
                    Wallet.wallet_id == wallet_id
                ).first()

                tx = UserTransaction(
                    id=uuid.uuid4(),
                    wallet_id=wallet.id,
                    user_id=wallet.user_id,
                    tx_hash=result.get("tx_hash"),
                    blockchain=blockchain,
                    from_address=address,
                    to_address=to_address,
                    amount=amount,
                    asset=asset or self._get_native_asset(blockchain),
                    status="pending",
                    fee=result.get("fee"),
                    created_at=datetime.utcnow(),
                )
                session.add(tx)
                session.flush()

            result["transaction_id"] = str(tx.id)
            result["status"] = "pending"
            return result

        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            return {"error": str(e)}

    def _send_eth_transaction(self, from_address: str, to_address: str, amount: float, private_key: bytes) -> Dict[str, Any]:
        """
        Send an Ethereum transaction.
        """
        try:
            from eth_account import Account
            from web3 import Web3

            if not self.eth_provider:
                return {"error": "Ethereum provider not available"}

            w3 = self.eth_provider.web3

            # Validate addresses
            if not Web3.is_address(to_address):
                return {"error": "Invalid Ethereum recipient address"}

            # Get nonce
            nonce = w3.eth.get_transaction_count(from_address)

            # Get gas price
            gas_price = w3.eth.gas_price

            # Convert amount to Wei
            amount_wei = w3.to_wei(amount, 'ether')

            # Build transaction
            tx = {
                'from': from_address,
                'to': Web3.to_checksum_address(to_address),
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': w3.eth.chain_id
            }

            # Estimate gas
            try:
                gas_estimate = w3.eth.estimate_gas(tx)
                tx['gas'] = gas_estimate
            except:
                # Use default gas limit if estimation fails
                pass

            # Sign transaction
            account = Account.from_key(private_key)
            signed_tx = account.sign_transaction(tx)

            # Send transaction
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            fee = w3.from_wei(tx['gas'] * tx['gasPrice'], 'ether')

            return {
                "tx_hash": tx_hash.hex(),
                "from": from_address,
                "to": to_address,
                "amount": amount,
                "asset": "ETH",
                "fee": float(fee),
                "raw_transaction": signed_tx.raw_transaction.hex(),
            }

        except Exception as e:
            logger.error(f"Error sending ETH transaction: {e}")
            return {"error": str(e)}

    def _send_btc_transaction(self, from_address: str, to_address: str, amount: float, private_key: bytes) -> Dict[str, Any]:
        """
        Send a Bitcoin transaction using UTXO management.
        Uses blockchain.info API when no local node is available.
        """
        try:
            import requests
            from wallets.blockchain.bitcoin.signer import BitcoinTransactionSigner

            # Step 1: Get UTXOs for the address from blockchain.info
            try:
                # Try blockchain.info API for UTXOs
                response = requests.get(
                    f"https://blockchain.info/unspent?active={from_address}",
                    timeout=15
                )
                
                if response.status_code != 200:
                    return {"error": f"Failed to get UTXOs: {response.status_code}"}
                
                data = response.json()
                utxos = data.get('unspent_outputs', [])
                
                if not utxos:
                    return {"error": "No UTXOs found for this address. Wallet has 0 balance."}
                
                logger.info(f"Found {len(utxos)} UTXOs for {from_address}")
                
            except requests.exceptions.ConnectionError:
                # Fallback to local Bitcoin node
                if self.btc_provider:
                    try:
                        self.btc_provider.connect()
                        utxos = self.btc_provider.get_address_utxos(from_address)
                    except:
                        return {"error": "No Bitcoin node available and blockchain.info API failed"}
                else:
                    return {"error": "No Bitcoin provider available"}

            # Step 2: Calculate total balance and select UTXOs
            total_utxo_btc = 0
            selected_utxos = []
            
            # Convert UTXO format from blockchain.info
            for utxo in utxos:
                # blockchain.info format
                if 'tx_hash' in utxo:
                    utxo_data = {
                        'txid': utxo.get('tx_hash_big_endian') or utxo.get('tx_hash'),
                        'vout': utxo.get('tx_output_n', 0),
                        'amount': utxo.get('value', 0) / 100_000_000,
                        'scriptPubKey': {'hex': utxo.get('script', '')}
                    }
                    utxo_amount = utxo_data['amount']
                else:
                    # Local node format
                    utxo_data = utxo
                    utxo_amount = utxo.get('amount', 0)
                
                total_utxo_btc += utxo_amount
                selected_utxos.append(utxo_data)
                
                # If we have enough to cover the amount + fee, stop
                if total_utxo_btc >= amount + 0.0001:
                    break

            if total_utxo_btc < amount:
                return {"error": f"Insufficient balance. Have {total_utxo_btc:.8f} BTC, need {amount:.8f} BTC"}

            # Step 3: Create transaction inputs
            inputs = []
            total_input_sats = 0
            
            for utxo in selected_utxos:
                txid = utxo.get('txid')
                vout = utxo.get('vout')
                utxo_amount = utxo.get('amount', 0)
                
                if txid and vout is not None:
                    inputs.append({
                        'txid': txid,
                        'vout': vout
                    })
                    total_input_sats += int(utxo_amount * 100_000_000)

            # Step 4: Calculate fee (simplified)
            fee_sats = len(inputs) * 1000 + 1000
            fee_btc = fee_sats / 100_000_000
            
            # Step 5: Calculate output amounts
            amount_sats = int(amount * 100_000_000)
            change_sats = total_input_sats - amount_sats - fee_sats
            
            # Step 6: Create outputs
            outputs = {
                to_address: amount_sats / 100_000_000
            }
            
            if change_sats > 1000:
                outputs[from_address] = change_sats / 100_000_000

            # Step 7: Create raw transaction (use local node if available)
            if self.btc_provider:
                try:
                    raw_tx = self.btc_provider.create_raw_transaction(inputs, outputs)
                except:
                    raw_tx = self._create_raw_transaction_manual(inputs, outputs)
            else:
                raw_tx = self._create_raw_transaction_manual(inputs, outputs)
            
            if not raw_tx:
                return {"error": "Failed to create raw transaction"}

            # Step 8: Sign the transaction
            signer = BitcoinTransactionSigner()
            
            previous_outputs = {}
            for utxo in selected_utxos:
                txid = utxo.get('txid')
                vout = utxo.get('vout')
                script = utxo.get('scriptPubKey', {}).get('hex', '')
                
                if txid and vout is not None:
                    key = (txid, vout)
                    previous_outputs[key] = {
                        'scriptPubKey': {'hex': script}
                    }

            signed_tx = signer.sign(raw_tx, private_key, previous_outputs)
            
            if not signed_tx:
                return {"error": "Failed to sign transaction"}

            # Step 9: Broadcast the transaction
            if self.btc_provider:
                try:
                    tx_hash = self.btc_provider.send_raw_transaction(signed_tx)
                except:
                    tx_hash = self._send_raw_transaction_manual(signed_tx)
            else:
                tx_hash = self._send_raw_transaction_manual(signed_tx)

            if not tx_hash:
                return {"error": "Failed to broadcast transaction"}

            return {
                "tx_hash": tx_hash,
                "from": from_address,
                "to": to_address,
                "amount": amount,
                "asset": "BTC",
                "fee": fee_btc,
                "inputs": len(inputs),
                "outputs": len(outputs),
            }

        except Exception as e:
            logger.error(f"Error sending BTC transaction: {e}")
            return {"error": str(e)}

    def _create_raw_transaction_manual(self, inputs: list, outputs: dict) -> str:
        """Manually create a raw transaction (simplified)."""
        # This is a placeholder - in production, use a proper library
        return "0200000001" + "0" * 128 + "01" + "0" * 40 + "00000000"

    def _send_raw_transaction_manual(self, signed_tx: str) -> str:
        """Manually broadcast a raw transaction via blockchain.info."""
        try:
            import requests
            response = requests.post(
                "https://blockchain.info/pushtx",
                data={"tx": signed_tx},
                timeout=30
            )
            if response.status_code == 200:
                return response.text.strip()
            return None
        except:
            return None

    def _send_trx_transaction(self, from_address: str, to_address: str, amount: float, private_key: bytes) -> Dict[str, Any]:
        """
        Send a TRON transaction using direct TronGrid API with ecdsa signing.
        """
        try:
            import requests
            import json
            import hashlib
            import base58
            from datetime import datetime
            from ecdsa import SigningKey, SECP256k1
            from ecdsa.util import sigencode_der
            
            if not self.tron_provider:
                return {"error": "TRON provider not available"}

            # Step 1: Convert amount to SUN (1 TRX = 1,000,000 SUN)
            amount_sun = int(amount * 1_000_000)
            
            if amount_sun <= 0:
                return {"error": "Amount must be greater than 0"}

            # Step 2: Get TronGrid URL
            tron_api = self.tron_provider.http_url
            
            # Step 3: Check balance
            account_response = requests.post(
                f"{tron_api}/wallet/getaccount",
                json={"address": from_address},
                timeout=10
            )
            account_data = account_response.json()
            balance_sun = account_data.get('balance', 0)
            
            if balance_sun < amount_sun:
                return {"error": f"Insufficient balance. Have {balance_sun/1_000_000} TRX, need {amount} TRX"}

            # Step 4: Get latest block
            block_response = requests.post(
                f"{tron_api}/wallet/getnowblock",
                timeout=10
            )
            block_data = block_response.json()
            latest_block = block_data.get('block_header', {}).get('raw_data', {}).get('number', 0)

            # Step 5: Create transfer contract
            contract = {
                "type": "TransferContract",
                "parameter": {
                    "value": {
                        "owner_address": from_address,
                        "to_address": to_address,
                        "amount": amount_sun
                    },
                    "type_url": "type.googleapis.com/protocol.TransferContract"
                }
            }

            # Step 6: Build raw transaction
            raw_data = {
                "contract": [contract],
                "ref_block_bytes": hex(latest_block % 0x10000)[2:].zfill(4),
                "ref_block_hash": hex(latest_block)[2:].zfill(8),
                "expiration": int((datetime.utcnow().timestamp() + 60) * 1000),
                "timestamp": int(datetime.utcnow().timestamp() * 1000)
            }

            # Step 7: Create transaction JSON
            transaction = {
                "raw_data": raw_data,
                "visible": True
            }

            # Step 8: Sign the transaction using ecdsa
            try:
                # Convert raw_data to bytes for signing
                raw_data_bytes = json.dumps(raw_data, separators=(',', ':'), sort_keys=True).encode()
                
                # Create signing key from private key
                signing_key = SigningKey.from_string(private_key, curve=SECP256k1)
                
                # Sign the raw data
                signature = signing_key.sign_deterministic(
                    raw_data_bytes,
                    hashfunc=hashlib.sha256,
                    sigencode=sigencode_der
                )
                
                # Convert signature to hex
                signature_hex = signature.hex()
                
                # Add signature to transaction
                transaction['signature'] = [signature_hex]
                
                # Step 9: Broadcast the transaction
                broadcast_response = requests.post(
                    f"{tron_api}/wallet/broadcasttransaction",
                    json=transaction,
                    timeout=30
                )
                
                result = broadcast_response.json()
                
                if result.get('result') is True:
                    return {
                        "tx_hash": result.get('txid'),
                        "from": from_address,
                        "to": to_address,
                        "amount": amount,
                        "asset": "TRX",
                        "fee": 0,
                    }
                else:
                    return {"error": f"Broadcast failed: {result}"}
                    
            except Exception as e:
                return {"error": f"Signing failed: {str(e)}"}

        except Exception as e:
            logger.error(f"Error sending TRX transaction: {e}")
            return {"error": str(e)}

    def _send_trx_transaction_fallback(self, from_address: str, to_address: str, amount_sun: int, private_key: bytes) -> Dict[str, Any]:
        """
        Fallback method for sending TRX using direct TronGrid API calls.
        """
        try:
            import requests
            import hashlib
            import base58
            import json
            from tronpy.keys import PrivateKey
            from tronpy.providers import HTTPProvider

            # Step 1: Get TronGrid URL
            tron_api = self.tron_provider.http_url
            
            # Step 2: Get account info
            account_response = requests.post(
                f"{tron_api}/wallet/getaccount",
                json={"address": from_address},
                timeout=10
            )
            account_data = account_response.json()
            
            # Step 3: Get latest block
            block_response = requests.post(
                f"{tron_api}/wallet/getnowblock",
                timeout=10
            )
            block_data = block_response.json()
            latest_block = block_data.get('block_header', {}).get('raw_data', {}).get('number', 0)
            
            # Step 4: Get chain parameters for fee reference
            params_response = requests.post(
                f"{tron_api}/wallet/getchainparameters",
                timeout=10
            )
            params_data = params_response.json()
            
            # Step 5: Build the transaction
            # Create transfer contract
            contract = {
                "type": "TransferContract",
                "parameter": {
                    "value": {
                        "owner_address": from_address,
                        "to_address": to_address,
                        "amount": amount_sun
                    },
                    "type_url": "type.googleapis.com/protocol.TransferContract"
                }
            }
            
            # Step 6: Get the transaction builder
            tx_data = {
                "visible": True,
                "txID": None
            }
            
            # Create raw transaction
            raw_tx = {
                "raw_data": {
                    "contract": [contract],
                    "ref_block_bytes": hex(latest_block % 0x10000)[2:].zfill(4),
                    "ref_block_hash": hex(latest_block)[2:].zfill(8),
                    "expiration": int((datetime.utcnow().timestamp() + 60 * 60) * 1000),
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                },
                "visible": True
            }
            
            # Step 7: Sign the transaction using tronpy PrivateKey
            try:
                # Convert private key to hex string
                private_key_hex = private_key.hex()
                
                # Create PrivateKey from bytes
                priv_key = PrivateKey(private_key)
                
                # Create transaction using tronpy
                from tronpy import Tron
                tron = Tron(provider=HTTPProvider(api_key=self.tron_provider._api_key))
                
                # Use tronpy's transaction builder
                tx = (
                    tron.trx.transfer(from_address, to_address, amount_sun)
                    .build()
                    .sign(priv_key)
                )
                
                # Broadcast
                result = tx.broadcast()
                
                if result and result.get('result') is True:
                    return {
                        "tx_hash": result.get('txid'),
                        "from": from_address,
                        "to": to_address,
                        "amount": amount_sun / 1_000_000,
                        "asset": "TRX",
                        "fee": 0,
                    }
                else:
                    return {"error": f"Broadcast failed: {result}"}
                    
            except Exception as e:
                logger.error(f"TRON signing/broadcast failed: {e}")
                return {"error": f"TRON transaction failed: {str(e)}"}

        except Exception as e:
            logger.error(f"TRON fallback transaction failed: {e}")
            return {"error": f"TRON transaction failed: {str(e)}"}

    def _get_native_asset(self, blockchain: str) -> str:
        """Get native asset symbol for blockchain."""
        assets = {
            "ethereum": "ETH",
            "bitcoin": "BTC",
            "tron": "TRX"
        }
        return assets.get(blockchain, "UNKNOWN")

    def info(self) -> Dict[str, Any]:
        """Return service information."""
        return {
            "service": "Wallet Service",
            "version": "2.0 Enterprise",
            "providers": {
                "ethereum": self.eth_provider is not None,
                "bitcoin": self.btc_provider is not None,
                "tron": self.tron_provider is not None,
            }
        }


###############################################################################
# End of File
####################
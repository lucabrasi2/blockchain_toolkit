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
        Send a TRON transaction.
        """
        try:
            if not self.tron_provider:
                return {"error": "TRON provider not available"}

            # TRON transaction sending requires specific signing
            # For now, return a placeholder
            return {"error": "TRON transaction sending coming soon."}

        except Exception as e:
            logger.error(f"Error sending TRX transaction: {e}")
            return {"error": str(e)}

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
###############################################################################
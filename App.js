// ============================================================================
// Universal Blockchain Platform (UBP)
// Mobile Application
// ============================================================================

import React, {
  useCallback,
  useEffect,
  useState,
} from 'react';

import {
  ActivityIndicator,
  Alert,
  FlatList,
  Modal,
  Pressable,
  Share,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

import AsyncStorage from '@react-native-async-storage/async-storage';
import Clipboard from '@react-native-clipboard/clipboard';

// ============================================================================
// UBP Mobile API Configuration
// ============================================================================

const MOBILE_API_URL = 'http://172.20.189.103:5000/api/mobile';

// ============================================================================
// Storage Keys
// ============================================================================

const AUTH_TOKEN_KEY = 'ubp_auth_token';
const USER_KEY = 'ubp_user';

// ============================================================================
// Utility Functions
// ============================================================================

const parseResponse = async (response) => {
  try {
    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: 'Invalid server response',
    };
  }
};

/**
 * Centralized authenticated API request helper.
 */
const authenticatedFetch = async (path, options = {}) => {
  const token = await getAuthToken();

  if (!token) {
    const error = new Error('Authentication token is missing');
    error.code = 'AUTH_REQUIRED';
    throw error;
  }

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
    'Authorization': `Bearer ${token}`,
  };

  const response = await fetch(
    `${MOBILE_API_URL}${path}`,
    {
      ...options,
      headers,
    }
  );

  const data = await parseResponse(response);

  return { response, data };
};

const isUnauthorizedResponse = (response) => (
  response.status === 401
);

const handleUnauthorized = async (navigation, showAlert = true) => {
  await clearAuthentication();

  if (showAlert) {
    Alert.alert('Session Expired', 'Please sign in again.');
  }

  navigation.replace('Login');
};

// ============================================================================
// Authentication Storage
// ============================================================================

const getAuthToken = async () => {
  try {
    return await AsyncStorage.getItem(AUTH_TOKEN_KEY);
  } catch (error) {
    console.error(
      'Failed to retrieve authentication token:',
      error
    );

    return null;
  }
};

const storeAuthentication = async (
  token,
  user
) => {
  try {
    await AsyncStorage.multiSet([
      [AUTH_TOKEN_KEY, token],
      [USER_KEY, JSON.stringify(user)],
    ]);

    console.log(
      'Authentication credentials stored successfully'
    );
  } catch (error) {
    console.error(
      'Failed to store authentication:',
      error
    );

    throw error;
  }
};

const clearAuthentication = async () => {
  try {
    await AsyncStorage.multiRemove([
      AUTH_TOKEN_KEY,
      USER_KEY,
    ]);

    console.log(
      'Authentication credentials cleared'
    );
  } catch (error) {
    console.error(
      'Failed to clear authentication:',
      error
    );
  }
};

const getStoredUser = async () => {
  try {
    const user = await AsyncStorage.getItem(USER_KEY);

    if (!user) {
      return null;
    }

    return JSON.parse(user);
  } catch (error) {
    console.error(
      'Failed to retrieve stored user:',
      error
    );

    return null;
  }
};

// ============================================================================
// Clipboard
// ============================================================================

/**
 * Copy text to clipboard and show feedback.
 */
const copyToClipboard = (
  text,
  label = 'Address'
) => {
  Clipboard.setString(text);

  Alert.alert(
    '✅ Copied!',
    `${label} copied to clipboard.`
  );
};

// ============================================================================
// Login Screen
// ============================================================================

const LoginScreen = ({
  onLogin,
  onNavigateRegister,
}) => {
  const [
    username,
    setUsername,
  ] = useState('');

  const [
    password,
    setPassword,
  ] = useState('');

  const [
    loading,
    setLoading,
  ] = useState(false);

  const handleLogin = async () => {
    if (!username.trim()) {
      Alert.alert(
        'Validation Error',
        'Please enter your username.'
      );

      return;
    }

    if (!password) {
      Alert.alert(
        'Validation Error',
        'Please enter your password.'
      );

      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${MOBILE_API_URL}/auth/login`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: username.trim(),
            password,
          }),
        }
      );

      const data = await parseResponse(response);

      if (!response.ok || !data.success) {
        throw new Error(
          data.error || 'Login failed'
        );
      }

      if (!data.token) {
        throw new Error(
          'Authentication token was not returned by the server.'
        );
      }

      await storeAuthentication(
        data.token,
        data.user
      );

      onLogin(
        data.token,
        data.user
      );
    } catch (error) {
      console.error(
        'Login error:',
        error
      );

      Alert.alert(
        'Login Failed',
        error.message ||
          'Unable to sign in. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.screen}>
      <View style={styles.authContainer}>

        <Text style={styles.logo}>
          UBP
        </Text>

        <Text style={styles.title}>
          Universal Blockchain Platform
        </Text>

        <Text style={styles.subtitle}>
          Sign in to your wallet
        </Text>

        <TextInput
          style={styles.input}
          placeholder="Username"
          placeholderTextColor="#888"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
          autoCorrect={false}
        />

        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#888"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          autoCapitalize="none"
        />

        <TouchableOpacity
          style={styles.primaryButton}
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.primaryButtonText}>
              Sign In
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={onNavigateRegister}
          disabled={loading}
        >
          <Text style={styles.secondaryButtonText}>
            Create Account
          </Text>
        </TouchableOpacity>

      </View>
    </View>
  );
};

// ============================================================================
// Registration Screen
// ============================================================================

const RegisterScreen = ({
  onRegisterSuccess,
  onNavigateLogin,
}) => {
  const [
    username,
    setUsername,
  ] = useState('');

  const [
    email,
    setEmail,
  ] = useState('');

  const [
    password,
    setPassword,
  ] = useState('');

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState('');

  const [
    loading,
    setLoading,
  ] = useState(false);

  const handleRegister = async () => {
    if (!username.trim()) {
      Alert.alert(
        'Validation Error',
        'Please enter a username.'
      );

      return;
    }

    if (!email.trim()) {
      Alert.alert(
        'Validation Error',
        'Please enter your email address.'
      );

      return;
    }

    if (!password) {
      Alert.alert(
        'Validation Error',
        'Please enter a password.'
      );

      return;
    }

    if (password !== confirmPassword) {
      Alert.alert(
        'Validation Error',
        'Passwords do not match.'
      );

      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${MOBILE_API_URL}/auth/register`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: username.trim(),
            email: email.trim(),
            password,
          }),
        }
      );

      const data = await parseResponse(response);

      if (!response.ok || !data.success) {
        throw new Error(
          data.error || 'Registration failed'
        );
      }

      // ============================================================
      // FIX 1: Auto-login after successful registration
      // ============================================================
      const loginResponse = await fetch(
        `${MOBILE_API_URL}/auth/login`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: username.trim(),
            password,
          }),
        }
      );

      const loginData = await parseResponse(loginResponse);

      if (!loginResponse.ok || !loginData.success) {
        throw new Error('Auto-login failed. Please sign in manually.');
      }

      if (!loginData.token) {
        throw new Error('No authentication token received.');
      }

      await storeAuthentication(loginData.token, loginData.user);
      
      Alert.alert(
        '✅ Account Created',
        'Your account has been created and you are now signed in.',
        [
          {
            text: 'OK',
            onPress: () => {
              // Clear form fields
              setUsername('');
              setEmail('');
              setPassword('');
              setConfirmPassword('');
              onRegisterSuccess();
            },
          },
        ]
      );
    } catch (error) {
      console.error(
        'Registration error:',
        error
      );

      Alert.alert(
        'Registration Failed',
        error.message ||
          'Unable to create your account.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.screen}>
      <View style={styles.authContainer}>

        <Text style={styles.logo}>
          UBP
        </Text>

        <Text style={styles.title}>
          Create Account
        </Text>

        <TextInput
          style={styles.input}
          placeholder="Username"
          placeholderTextColor="#888"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
        />

        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor="#888"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />

        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#888"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        <TextInput
          style={styles.input}
          placeholder="Confirm Password"
          placeholderTextColor="#888"
          value={confirmPassword}
          onChangeText={setConfirmPassword}
          secureTextEntry
        />

        <TouchableOpacity
          style={styles.primaryButton}
          onPress={handleRegister}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.primaryButtonText}>
              Create Account
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={onNavigateLogin}
          disabled={loading}
        >
          <Text style={styles.secondaryButtonText}>
            Back to Sign In
          </Text>
        </TouchableOpacity>

      </View>
    </View>
  );
};

// ============================================================================
// Create Wallet Modal
// ============================================================================

const CreateWalletModal = ({
  visible,
  onClose,
  onCreated,
}) => {
  const [
    blockchain,
    setBlockchain,
  ] = useState('ethereum');

  const [
    label,
    setLabel,
  ] = useState('');

  const [
    loading,
    setLoading,
  ] = useState(false);

  const createWallet = async () => {
    if (!label.trim()) {
      Alert.alert(
        'Validation Error',
        'Please enter a wallet label.'
      );

      return;
    }

    setLoading(true);

    try {
      const { response, data } =
        await authenticatedFetch(
          '/wallets/create',
          {
            method: 'POST',
            body: JSON.stringify({
              blockchain: blockchain,
              label: label.trim(),
            }),
          }
        );

      if (isUnauthorizedResponse(response)) {
        await clearAuthentication();

        onClose();

        Alert.alert(
          'Session Expired',
          'Please sign in again.'
        );

        return;
      }

      if (data.success) {
        Alert.alert(
          'Wallet Created',
          'Your wallet was created successfully.'
        );

        setLabel('');
        onClose();

        if (onCreated) {
          onCreated(data.wallet);
        }
      } else {
        throw new Error(
          data.error || 'Unable to create wallet.'
        );
      }
    } catch (error) {
      console.error(
        'Create wallet error:',
        error
      );

      Alert.alert(
        'Wallet Creation Failed',
        error.message ||
          'Unable to create wallet.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>

        <View style={styles.modalContainer}>

          <Text style={styles.modalTitle}>
            Create Wallet
          </Text>

          <Text style={styles.fieldLabel}>
            Blockchain
          </Text>

          {/* ================================================================
              FIX 2: Added TRON button
              ============================================================ */}
          <View style={styles.blockchainRow}>

            <TouchableOpacity
              style={[
                styles.blockchainButton,
                blockchain === 'ethereum' &&
                  styles.blockchainButtonActive,
              ]}
              onPress={() =>
                setBlockchain('ethereum')
              }
            >
              <Text
                style={[
                  styles.blockchainButtonText,
                  blockchain === 'ethereum' &&
                    styles.blockchainButtonTextActive,
                ]}
              >
                🟣 Ethereum
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.blockchainButton,
                blockchain === 'bitcoin' &&
                  styles.blockchainButtonActive,
              ]}
              onPress={() =>
                setBlockchain('bitcoin')
              }
            >
              <Text
                style={[
                  styles.blockchainButtonText,
                  blockchain === 'bitcoin' &&
                    styles.blockchainButtonTextActive,
                ]}
              >
                🟠 Bitcoin
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.blockchainButton,
                blockchain === 'tron' &&
                  styles.blockchainButtonActive,
              ]}
              onPress={() =>
                setBlockchain('tron')
              }
            >
              <Text
                style={[
                  styles.blockchainButtonText,
                  blockchain === 'tron' &&
                    styles.blockchainButtonTextActive,
                ]}
              >
                🔴 TRON
              </Text>
            </TouchableOpacity>

          </View>

          <Text style={styles.fieldLabel}>
            Wallet Label
          </Text>

          <TextInput
            style={styles.input}
            placeholder="e.g. Main Wallet"
            placeholderTextColor="#888"
            value={label}
            onChangeText={setLabel}
          />

          <TouchableOpacity
            style={styles.primaryButton}
            onPress={createWallet}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.primaryButtonText}>
                Create Wallet
              </Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={onClose}
            disabled={loading}
          >
            <Text style={styles.secondaryButtonText}>
              Cancel
            </Text>
          </TouchableOpacity>

        </View>
      </View>
    </Modal>
  );
};

// ============================================================================
// Send Transaction Modal
// ============================================================================

const SendTransactionModal = ({
  visible,
  wallet,
  onClose,
  onSent,
}) => {
  const [
    toAddress,
    setToAddress,
  ] = useState('');

  const [
    amount,
    setAmount,
  ] = useState('');

  const [
    loading,
    setLoading,
  ] = useState(false);

  const handleSend = async () => {
    if (!wallet) {
      Alert.alert(
        'Error',
        'No wallet selected.'
      );

      return;
    }

    if (!toAddress.trim()) {
      Alert.alert(
        'Validation Error',
        'Please enter the destination address.'
      );

      return;
    }

    const amountNum = Number(amount);

    if (
      !amount ||
      Number.isNaN(amountNum) ||
      amountNum <= 0
    ) {
      Alert.alert(
        'Validation Error',
        'Please enter a valid amount.'
      );

      return;
    }

    setLoading(true);

    try {
      const { response, data } =
        await authenticatedFetch(
          `/wallets/${wallet.wallet_id}/send`,
          {
            method: 'POST',
            body: JSON.stringify({
              to_address: toAddress.trim(),
              amount: amountNum,
            }),
          }
        );

      if (isUnauthorizedResponse(response)) {
        await clearAuthentication();

        onClose();

        Alert.alert(
          'Session Expired',
          'Please sign in again.'
        );

        return;
      }

      if (data.success) {
        Alert.alert(
          'Transaction Submitted',
          data.message ||
            'Your transaction has been submitted.'
        );

        setToAddress('');
        setAmount('');

        onClose();

        if (onSent) {
          onSent(data);
        }
      } else {
        throw new Error(
          data.error ||
            'Transaction could not be submitted.'
        );
      }
    } catch (error) {
      console.error(
        'Send transaction error:',
        error
      );

      Alert.alert(
        'Transaction Failed',
        error.message ||
          'Unable to send transaction.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>

        <View style={styles.modalContainer}>

          <Text style={styles.modalTitle}>
            Send Transaction
          </Text>

          {wallet && (
            <View style={styles.selectedWalletBox}>
              <Text style={styles.selectedWalletLabel}>
                From
              </Text>

              <Text style={styles.selectedWalletValue}>
                {wallet.label ||
                  wallet.wallet_id}
              </Text>

              <Text
                style={styles.addressText}
                numberOfLines={1}
              >
                {wallet.address}
              </Text>
            </View>
          )}

          <Text style={styles.fieldLabel}>
            Destination Address
          </Text>

          <TextInput
            style={styles.input}
            placeholder="Enter destination address"
            placeholderTextColor="#888"
            value={toAddress}
            onChangeText={setToAddress}
            autoCapitalize="none"
            autoCorrect={false}
          />

          <Text style={styles.fieldLabel}>
            Amount
          </Text>

          <TextInput
            style={styles.input}
            placeholder="Enter amount"
            placeholderTextColor="#888"
            value={amount}
            onChangeText={setAmount}
            keyboardType="decimal-pad"
          />

          <TouchableOpacity
            style={styles.primaryButton}
            onPress={handleSend}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.primaryButtonText}>
                Send
              </Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={onClose}
            disabled={loading}
          >
            <Text style={styles.secondaryButtonText}>
              Cancel
            </Text>
          </TouchableOpacity>

        </View>
      </View>
    </Modal>
  );
};
// ============================================================================
// Wallet Card
// ============================================================================

const WalletCard = ({
  wallet,
  onSend,
  onReceive,
  onInspect,
}) => {
  if (!wallet) {
    return null;
  }

  const blockchain =
    wallet.blockchain ||
    wallet.network ||
    'Unknown';

  const address =
    wallet.address ||
    'Address unavailable';

  const balance =
    wallet.balance !== undefined &&
    wallet.balance !== null
      ? wallet.balance
      : '0';
const blockchainName =
  String(blockchain).toLowerCase();

const asset =
  wallet.asset ||
  wallet.symbol ||
  (
    blockchainName === 'bitcoin'
      ? 'BTC'
      : blockchainName === 'tron' ||
        blockchainName === 'trc20'
        ? 'USDT'
        : 'ETH'
  );
  return (
    <View style={styles.walletCard}>

      <View style={styles.walletHeader}>

        <View style={styles.walletHeaderLeft}>
          <Text style={styles.walletLabel}>
            {wallet.label ||
              'Unnamed Wallet'}
          </Text>

          <Text style={styles.walletBlockchain}>
            {blockchain.toUpperCase()}
          </Text>
        </View>

        <TouchableOpacity
          style={styles.inspectButton}
          onPress={() => onInspect(wallet)}
        >
          <Text style={styles.inspectButtonText}>
            Inspect
          </Text>
        </TouchableOpacity>

      </View>

      <Text style={styles.walletBalance}>
        {balance} {asset}
      </Text>

      <TouchableOpacity
        onPress={() =>
          copyToClipboard(
            address,
            'Wallet address'
          )
        }
      >
        <Text
          style={styles.walletAddress}
          numberOfLines={1}
          ellipsizeMode="middle"
        >
          {address}
        </Text>
      </TouchableOpacity>

      <View style={styles.walletActions}>

        <TouchableOpacity
          style={styles.walletActionButton}
          onPress={() => onSend(wallet)}
        >
          <Text style={styles.walletActionText}>
            Send
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.walletActionButton}
          onPress={() => onReceive(wallet)}
        >
          <Text style={styles.walletActionText}>
            Receive
          </Text>
        </TouchableOpacity>

      </View>

    </View>
  );
};

// ============================================================================
// Receive Wallet Modal
// ============================================================================

const ReceiveWalletModal = ({
  visible,
  wallet,
  onClose,
}) => {
  if (!wallet) {
    return null;
  }

  const address =
    wallet.address ||
    'Address unavailable';

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>

        <View style={styles.modalContainer}>

          <Text style={styles.modalTitle}>
            Receive
          </Text>

          <Text style={styles.receiveDescription}>
            Send funds to this wallet address.
          </Text>

          <View style={styles.receiveAddressBox}>

            <Text
              style={styles.receiveAddress}
              selectable
            >
              {address}
            </Text>

          </View>

          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() =>
              copyToClipboard(
                address,
                'Wallet address'
              )
            }
          >
            <Text style={styles.primaryButtonText}>
              Copy Address
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={async () => {
              try {
                await Share.share({
                  message: address,
                });
              } catch (error) {
                console.error(
                  'Share address error:',
                  error
                );
              }
            }}
          >
            <Text style={styles.secondaryButtonText}>
              Share Address
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={onClose}
          >
            <Text style={styles.secondaryButtonText}>
              Close
            </Text>
          </TouchableOpacity>

        </View>

      </View>
    </Modal>
  );
};

// ============================================================================
// Wallet Inspection Modal
// ============================================================================

const WalletInspectionModal = ({
  visible,
  wallet,
  onClose,
}) => {
  const [
    inspection,
    setInspection,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState(null);

  useEffect(() => {
    if (!visible || !wallet) {
      setInspection(null);
      setError(null);
      return;
    }

    let mounted = true;

    const loadInspection = async () => {
      setLoading(true);
      setError(null);

      try {
        const {
          response,
          data,
        } = await authenticatedFetch(
          `/wallets/${wallet.wallet_id}/inspect`
        );

        if (response.status === 401) {
          if (mounted) {
            setError(
              'Your session has expired.'
            );
          }

          return;
        }

        if (!response.ok || !data.success) {
          throw new Error(
            data.error ||
              'Unable to inspect wallet.'
          );
        }

        if (mounted) {
          setInspection(data.wallet);
        }
      } catch (err) {
        console.error(
          'Wallet inspection error:',
          err
        );

        if (mounted) {
          setError(
            err.message ||
              'Unable to inspect wallet.'
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    loadInspection();

    return () => {
      mounted = false;
    };
  }, [
    visible,
    wallet,
  ]);

  const renderToken = ({
    item,
  }) => (
    <View style={styles.tokenRow}>

      <View style={styles.tokenInfo}>
        <Text style={styles.tokenName}>
          {item.name ||
            item.symbol ||
            'Unknown Token'}
        </Text>

        <Text style={styles.tokenSymbol}>
          {item.symbol ||
            'TOKEN'}
        </Text>
      </View>

      <Text style={styles.tokenBalance}>
        {item.balance_formatted ??
          item.balance ??
          '0'}
      </Text>

    </View>
  );

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>

        <View style={styles.largeModalContainer}>

          <View style={styles.modalHeader}>

            <Text style={styles.modalTitle}>
              Wallet Inspection
            </Text>

            <TouchableOpacity
              onPress={onClose}
            >
              <Text style={styles.closeButton}>
                ✕
              </Text>
            </TouchableOpacity>

          </View>

          {loading && (
            <View style={styles.loadingContainer}>

              <ActivityIndicator
                size="large"
              />

              <Text style={styles.loadingText}>
                Loading wallet information...
              </Text>

            </View>
          )}

          {!loading && error && (
            <View style={styles.errorContainer}>

              <Text style={styles.errorText}>
                {error}
              </Text>

              <TouchableOpacity
                style={styles.secondaryButton}
                onPress={onClose}
              >
                <Text
                  style={
                    styles.secondaryButtonText
                  }
                >
                  Close
                </Text>
              </TouchableOpacity>

            </View>
          )}

          {!loading &&
            !error &&
            inspection && (
              <FlatList
                data={
                  inspection.token_balances ||
                  inspection.tokens ||
                  []
                }
                keyExtractor={(
                  item,
                  index
                ) =>
                  item.contract_address ||
                  item.symbol ||
                  `${index}`
                }
                renderItem={renderToken}
                ListHeaderComponent={() => (
                  <View>

                    <View
                      style={
                        styles.inspectionSection
                      }
                    >

                      <Text
                        style={
                          styles.sectionTitle
                        }
                      >
                        Wallet Information
                      </Text>

                      <View
                        style={
                          styles.infoRow
                        }
                      >
                        <Text
                          style={
                            styles.infoLabel
                          }
                        >
                          Address
                        </Text>

                        <TouchableOpacity
                          onPress={() =>
                            copyToClipboard(
                              inspection.address,
                              'Wallet address'
                            )
                          }
                        >
                          <Text
                            style={
                              styles.infoValue
                            }
                            numberOfLines={2}
                            ellipsizeMode="middle"
                          >
                            {inspection.address ||
                              'N/A'}
                          </Text>
                        </TouchableOpacity>
                      </View>

                      <View
                        style={
                          styles.infoRow
                        }
                      >
                        <Text
                          style={
                            styles.infoLabel
                          }
                        >
                          Blockchain
                        </Text>

                        <Text
                          style={
                            styles.infoValue
                          }
                        >
                          {inspection.blockchain ||
                            'N/A'}
                        </Text>
                      </View>

                      <View
                        style={
                          styles.infoRow
                        }
                      >
                        <Text
                          style={
                            styles.infoLabel
                          }
                        >
                          Network
                        </Text>

                        <Text
                          style={
                            styles.infoValue
                          }
                        >
                          {inspection.network ||
                            'mainnet'}
                        </Text>
                      </View>

                      <View
                        style={
                          styles.infoRow
                        }
                      >
                        <Text
                          style={
                            styles.infoLabel
                          }
                        >
                          Balance
                        </Text>

                        <Text
                          style={
                            styles.infoValue
                          }
                        >
                          {inspection.balance ??
                            '0'}{' '}
                          {inspection.asset ||
                            ''}
                        </Text>
                      </View>

                      <View
                        style={
                          styles.infoRow
                        }
                      >
                        <Text
                          style={
                            styles.infoLabel
                          }
                        >
                          Wallet Type
                        </Text>

                        <Text
                          style={
                            styles.infoValue
                          }
                        >
                          {inspection.classification ||
                            'EOA'}
                        </Text>
                      </View>

                      <View
                        style={
                          styles.infoRow
                        }
                      >
                        <Text
                          style={
                            styles.infoLabel
                          }
                        >
                          Contract
                        </Text>

                        <Text
                          style={
                            styles.infoValue
                          }
                        >
                          {inspection.is_contract
                            ? 'Yes'
                            : 'No'}
                        </Text>
                      </View>

                      {inspection.nonce !==
                        undefined && (
                        <View
                          style={
                            styles.infoRow
                          }
                        >
                          <Text
                            style={
                              styles.infoLabel
                            }
                          >
                            Nonce
                          </Text>

                          <Text
                            style={
                              styles.infoValue
                            }
                          >
                            {inspection.nonce}
                          </Text>
                        </View>
                      )}

                      {inspection.transaction_count !==
                        undefined && (
                        <View
                          style={
                            styles.infoRow
                          }
                        >
                          <Text
                            style={
                              styles.infoLabel
                            }
                          >
                            Transactions
                          </Text>

                          <Text
                            style={
                              styles.infoValue
                            }
                          >
                            {
                              inspection.transaction_count
                            }
                          </Text>
                        </View>
                      )}

                    </View>

                    <Text
                      style={
                        styles.sectionTitle
                      }
                    >
                      Token Holdings
                    </Text>

                    {( 
                      inspection.token_balances ||
                      inspection.tokens ||
                      []
                    ).length === 0 && (
                      <Text
                        style={
                          styles.emptyText
                        }
                      >
                        No token holdings found.
                      </Text>
                    )}

                  </View>
                )}
              />
            )}

        </View>
      </View>
    </Modal>
  );
};

// ============================================================================
// Transaction History Modal
// ============================================================================

const TransactionHistoryModal = ({
  visible,
  wallet,
  onClose,
}) => {
  const [
    transactions,
    setTransactions,
  ] = useState([]);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState(null);

  const loadTransactions = useCallback(
    async () => {
      if (!wallet) {
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const {
          response,
          data,
        } = await authenticatedFetch(
          `/wallets/${wallet.wallet_id}/transactions`
        );

        if (response.status === 401) {
          throw new Error(
            'Your session has expired.'
          );
        }

        if (!response.ok || !data.success) {
          throw new Error(
            data.error ||
              'Unable to load transaction history.'
          );
        }

        setTransactions(
          data.transactions || []
        );
      } catch (err) {
        console.error(
          'Transaction history error:',
          err
        );

        setError(
          err.message ||
            'Unable to load transactions.'
        );
      } finally {
        setLoading(false);
      }
    },
    [wallet]
  );

  useEffect(() => {
    if (visible) {
      loadTransactions();
    }
  }, [
    visible,
    loadTransactions,
  ]);

  const renderTransaction = ({
    item,
  }) => {
    const status =
      item.status ||
      item.state ||
      'unknown';

    const hash =
      item.tx_hash ||
      item.transaction_hash ||
      item.hash ||
      '';

    const amount =
      item.amount !== undefined
        ? item.amount
        : '';

    return (
      <View style={styles.transactionRow}>

        <View style={styles.transactionMain}>

          <Text
            style={styles.transactionHash}
            numberOfLines={1}
            ellipsizeMode="middle"
          >
            {hash || 'Transaction'}
          </Text>

          <Text
            style={styles.transactionMeta}
          >
            {item.timestamp ||
              item.created_at ||
              ''}
          </Text>

        </View>

        <View
          style={
            styles.transactionRight
          }
        >

          <Text
            style={
              styles.transactionAmount
            }
          >
            {amount}
          </Text>

          <Text
            style={[
              styles.transactionStatus,
              status === 'confirmed' &&
                styles.statusConfirmed,
              status === 'failed' &&
                styles.statusFailed,
            ]}
          >
            {status}
          </Text>

        </View>

      </View>
    );
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>

        <View style={styles.largeModalContainer}>

          <View style={styles.modalHeader}>

            <Text style={styles.modalTitle}>
              Transaction History
            </Text>

            <TouchableOpacity
              onPress={onClose}
            >
              <Text style={styles.closeButton}>
                ✕
              </Text>
            </TouchableOpacity>

          </View>

          {loading && (
            <View style={styles.loadingContainer}>

              <ActivityIndicator
                size="large"
              />

              <Text style={styles.loadingText}>
                Loading transactions...
              </Text>

            </View>
          )}

          {!loading && error && (
            <View style={styles.errorContainer}>

              <Text style={styles.errorText}>
                {error}
              </Text>

              <TouchableOpacity
                style={styles.secondaryButton}
                onPress={loadTransactions}
              >
                <Text
                  style={
                    styles.secondaryButtonText
                  }
                >
                  Retry
                </Text>
              </TouchableOpacity>

            </View>
          )}

          {!loading &&
            !error && (
              <FlatList
                data={transactions}
                keyExtractor={(
                  item,
                  index
                ) =>
                  item.tx_hash ||
                  item.transaction_hash ||
                  item.hash ||
                  `${index}`
                }
                renderItem={
                  renderTransaction
                }
                ListEmptyComponent={() => (
                  <View
                    style={
                      styles.emptyContainer
                    }
                  >
                    <Text
                      style={
                        styles.emptyText
                      }
                    >
                      No transactions found.
                    </Text>
                  </View>
                )}
              />
            )}

        </View>
      </View>
    </Modal>
  );
};

// ============================================================================
// Dashboard Screen
// ============================================================================

const DashboardScreen = ({
  navigation,
  user,
  onLogout,
}) => {
  const [
    wallets,
    setWallets,
  ] = useState([]);

  const [
    stats,
    setStats,
  ] = useState(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [
    createWalletVisible,
    setCreateWalletVisible,
  ] = useState(false);

  const [
    sendVisible,
    setSendVisible,
  ] = useState(false);

  const [
    receiveVisible,
    setReceiveVisible,
  ] = useState(false);

  const [
    inspectionVisible,
    setInspectionVisible,
  ] = useState(false);

  const [
    historyVisible,
    setHistoryVisible,
  ] = useState(false);

  const [
    selectedWallet,
    setSelectedWallet,
  ] = useState(null);

  const loadDashboard = useCallback(
    async () => {
      try {
        setLoading(true);

        const token =
          await getAuthToken();

        console.log(
          'STORED TOKEN EXISTS:',
          !!token
        );

        console.log(
          'STORED TOKEN LENGTH:',
          token
            ? token.length
            : 0
        );

        if (!token) {
          await clearAuthentication();

          navigation.replace(
            'Login'
          );

          return;
        }

        const {
          response: authResponse,
          data: authData,
        } = await authenticatedFetch(
          '/auth/me'
        );

        console.log(
          'AUTH ME STATUS:',
          authResponse.status
        );

        console.log(
          'AUTH ME RESPONSE:',
          authData
        );

        if (
          isUnauthorizedResponse(
            authResponse
          )
        ) {
          await handleUnauthorized(
            navigation
          );

          return;
        }

        if (!authResponse.ok) {
          throw new Error(
            'Unable to validate authentication session'
          );
        }

        if (
          !authData.success ||
          !authData.user
        ) {
          await clearAuthentication();

          navigation.replace(
            'Login'
          );

          return;
        }

        const {
          response: statsResponse,
          data: statsData,
        } = await authenticatedFetch(
          '/dashboard/stats'
        );

        if (
          isUnauthorizedResponse(
            statsResponse
          )
        ) {
          await handleUnauthorized(
            navigation
          );

          return;
        }

        if (statsResponse.ok) {
          setStats(
            statsData
          );
        }

        const {
          response: walletsResponse,
          data: walletsData,
        } = await authenticatedFetch(
          '/wallets'
        );

        if (
          isUnauthorizedResponse(
            walletsResponse
          )
        ) {
          await handleUnauthorized(
            navigation
          );

          return;
        }

        if (walletsResponse.ok) {
          setWallets(
            walletsData.wallets ||
              []
          );
        }
      } catch (error) {
        console.error(
          'Dashboard loading error:',
          error
        );

        if (
          error.code ===
          'AUTH_REQUIRED'
        ) {
          await clearAuthentication();

          navigation.replace(
            'Login'
          );

          return;
        }

        Alert.alert(
          'Dashboard Error',
          error.message ||
            'Unable to load dashboard.'
        );
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [navigation]
  );

  useEffect(() => {
    loadDashboard();
  }, [
    loadDashboard,
  ]);

  const handleRefresh =
    async () => {
      setRefreshing(true);
      await loadDashboard();
    };

  const handleWalletCreated =
    () => {
      loadDashboard();
    };

  const handleSend =
    (wallet) => {
      setSelectedWallet(
        wallet
      );

      setSendVisible(
        true
      );
    };

  const handleReceive =
    (wallet) => {
      setSelectedWallet(
        wallet
      );

      setReceiveVisible(
        true
      );
    };

  const handleInspect =
    (wallet) => {
      setSelectedWallet(
        wallet
      );

      setInspectionVisible(
        true
      );
    };

  const handleHistory =
    (wallet) => {
      setSelectedWallet(
        wallet
      );

      setHistoryVisible(
        true
      );
    };

  const handleLogout =
    async () => {
      try {
        await authenticatedFetch(
          '/auth/logout',
          {
            method: 'POST',
          }
        );
      } catch (error) {
        console.warn(
          'Logout request failed:',
          error
        );
      } finally {
        await clearAuthentication();
        onLogout();
      }
    };

  if (loading) {
    return (
      <View
        style={
          styles.loadingScreen
        }
      >
        <ActivityIndicator
          size="large"
        />

        <Text
          style={
            styles.loadingText
          }
        >
          Loading dashboard...
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.screen}>

      <View style={styles.dashboardHeader}>

        <View>
          <Text
            style={
              styles.dashboardGreeting
            }
          >
            Welcome
          </Text>

          <Text
            style={
              styles.dashboardUsername
            }
          >
            {user?.username ||
              'User'}
          </Text>
        </View>

        <TouchableOpacity
          onPress={handleLogout}
        >
          <Text
            style={
              styles.logoutText
            }
          >
            Logout
          </Text>
        </TouchableOpacity>

      </View>

      <FlatList
        data={wallets}
        keyExtractor={(
          item,
          index
        ) =>
          item.wallet_id ||
          item.id ||
          `${index}`
        }
        refreshing={
          refreshing
        }
        onRefresh={
          handleRefresh
        }
        ListHeaderComponent={() => (
          <View>

            <View
              style={
                styles.statsContainer
              }
            >

              <View
                style={
                  styles.statCard
                }
              >
                <Text
                  style={
                    styles.statLabel
                  }
                >
                  Wallets
                </Text>

                <Text
                  style={
                    styles.statValue
                  }
                >
                  {stats?.wallet_count ??
                    wallets.length}
                </Text>
              </View>

              <View
                style={
                  styles.statCard
                }
              >
                <Text
                  style={
                    styles.statLabel
                  }
                >
                  Transactions
                </Text>

                <Text
                  style={
                    styles.statValue
                  }
                >
                  {stats?.transaction_count ??
                    0}
                </Text>
              </View>

            </View>

            <TouchableOpacity
              style={
                styles.createWalletButton
              }
              onPress={() =>
                setCreateWalletVisible(
                  true
                )
              }
            >
              <Text
                style={
                  styles.primaryButtonText
                }
              >
                + Create Wallet
              </Text>
            </TouchableOpacity>

            <Text
              style={
                styles.sectionTitle
              }
            >
              Your Wallets
            </Text>

          </View>
        )}
        renderItem={({
          item,
        }) => (
          <View>

            <WalletCard
              wallet={item}
              onSend={
                handleSend
              }
              onReceive={
                handleReceive
              }
              onInspect={
                handleInspect
              }
            />

            <TouchableOpacity
              style={
                styles.historyButton
              }
              onPress={() =>
                handleHistory(item)
              }
            >
              <Text
                style={
                  styles.historyButtonText
                }
              >
                View Transaction History
              </Text>
            </TouchableOpacity>

          </View>
        )}
        ListEmptyComponent={() => (
          <View
            style={
              styles.emptyContainer
            }
          >
            <Text
              style={
                styles.emptyText
              }
            >
              You don't have any wallets yet.
            </Text>

            <Text
              style={
                styles.emptySubtext
              }
            >
              Create your first wallet to get started.
            </Text>
          </View>
        )}
      />

      <CreateWalletModal
        visible={
          createWalletVisible
        }
        onClose={() =>
          setCreateWalletVisible(
            false
          )
        }
        onCreated={
          handleWalletCreated
        }
      />

      <SendTransactionModal
        visible={
          sendVisible
        }
        wallet={
          selectedWallet
        }
        onClose={() =>
          setSendVisible(
            false
          )
        }
        onSent={
          handleWalletCreated
        }
      />

      <ReceiveWalletModal
        visible={
          receiveVisible
        }
        wallet={
          selectedWallet
        }
        onClose={() =>
          setReceiveVisible(
            false
          )
        }
      />

      <WalletInspectionModal
        visible={
          inspectionVisible
        }
        wallet={
          selectedWallet
        }
        onClose={() =>
          setInspectionVisible(
            false
          )
        }
      />

      <TransactionHistoryModal
        visible={
          historyVisible
        }
        wallet={
          selectedWallet
        }
        onClose={() =>
          setHistoryVisible(
            false
          )
        }
      />

    </View>
  );
};
// ============================================================================
// Main Application
// ============================================================================

const App = () => {
  const [
    screen,
    setScreen,
  ] = useState('loading');

  const [
    user,
    setUser,
  ] = useState(null);

  const [
    token,
    setToken,
  ] = useState(null);

  // --------------------------------------------------------------------------
  // Restore authentication state
  // --------------------------------------------------------------------------

  useEffect(() => {
    let mounted = true;

    const restoreAuthentication =
      async () => {
        try {
          const storedToken =
            await getAuthToken();
            console.log(
           'RESTORE STORED TOKEN:',
            storedToken
        );

          const storedUser =
            await getStoredUser();

          console.log(
            'RESTORE TOKEN EXISTS:',
            !!storedToken
          );

          console.log(
            'RESTORE TOKEN LENGTH:',
            storedToken
              ? storedToken.length
              : 0
          );

          if (!storedToken) {
            if (mounted) {
              setScreen('login');
            }

            return;
          }

          // ------------------------------------------------------------------
          // Validate the stored token with the backend before restoring the
          // authenticated application state.
          // ------------------------------------------------------------------

          const response =
            await fetch(
              `${MOBILE_API_URL}/auth/me`,
              {
                method: 'GET',
                headers: {
                  'Authorization':
                    `Bearer ${storedToken}`,
                  'Content-Type':
                    'application/json',
                },
              }
            );

          const data =
            await parseResponse(
              response
            );

          console.log(
            'RESTORE AUTH STATUS:',
            response.status
          );

          console.log(
            'RESTORE AUTH RESPONSE:',
            data
          );

          if (
            response.status === 401
          ) {
            await clearAuthentication();

            if (mounted) {
              setUser(null);
              setToken(null);
              setScreen('login');
            }

            return;
          }

          if (
            !response.ok ||
            !data.success ||
            !data.user
          ) {
            await clearAuthentication();

            if (mounted) {
              setUser(null);
              setToken(null);
              setScreen('login');
            }

            return;
          }

          if (mounted) {
            setToken(
              storedToken
            );

            setUser(
              data.user ||
                storedUser
            );

            setScreen(
              'dashboard'
            );
          }
        } catch (error) {
          console.error(
            'Authentication restore error:',
            error
          );

          /*
           * Do not keep a broken/stale authentication state.
           * If the API cannot validate the session, return to login.
           */
          await clearAuthentication();

          if (mounted) {
            setUser(null);
            setToken(null);
            setScreen('login');
          }
        }
      };

    restoreAuthentication();

    return () => {
      mounted = false;
    };
  }, []);

  // --------------------------------------------------------------------------
  // Login
  // --------------------------------------------------------------------------

  const handleLogin = (
    authenticatedToken,
    authenticatedUser
  ) => {
    setToken(
      authenticatedToken
    );

    setUser(
      authenticatedUser
    );

    setScreen(
      'dashboard'
    );
  };

  // --------------------------------------------------------------------------
  // Logout
  // --------------------------------------------------------------------------

  const handleLogout = async () => {
    await clearAuthentication();

    setToken(null);
    setUser(null);

    setScreen('login');
  };

  // ============================================================
  // FIX 3: Registration Success Handler - Proper session restore
  // ============================================================
  const handleRegistrationSuccess = () => {
    // The user is already logged in via auto-login, so go to dashboard
    // Reload the user state from storage
    const restoreAfterRegister = async () => {
      const storedToken = await getAuthToken();
      const storedUser = await getStoredUser();
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(storedUser);
        setScreen('dashboard');
      } else {
        setScreen('login');
      }
    };
    
    restoreAfterRegister();
  };

  // --------------------------------------------------------------------------
  // Navigation
  // --------------------------------------------------------------------------

  if (screen === 'loading') {
    return (
      <View
        style={
          styles.loadingScreen
        }
      >
        <Text
          style={
            styles.logo
          }
        >
          UBP
        </Text>

        <ActivityIndicator
          size="large"
        />

        <Text
          style={
            styles.loadingText
          }
        >
          Initializing UBP...
        </Text>
      </View>
    );
  }

  if (screen === 'login') {
    return (
      <LoginScreen
        onLogin={
          handleLogin
        }
        onNavigateRegister={() =>
          setScreen(
            'register'
          )
        }
      />
    );
  }

  if (screen === 'register') {
    return (
      <RegisterScreen
        onRegisterSuccess={
          handleRegistrationSuccess
        }
        onNavigateLogin={() =>
          setScreen(
            'login'
          )
        }
      />
    );
  }

  if (screen === 'dashboard') {
    return (
      <DashboardScreen
        navigation={{
          replace: (
            destination
          ) => {
            if (
              destination ===
              'Login'
            ) {
              handleLogout();
            }
          },
        }}
        user={user}
        token={token}
        onLogout={
          handleLogout
        }
      />
    );
  }

  // --------------------------------------------------------------------------
  // Defensive fallback
  // --------------------------------------------------------------------------

  return (
    <View
      style={
        styles.loadingScreen
      }
    >
      <Text
        style={
          styles.errorText
        }
      >
        Unable to initialize application.
      </Text>

      <TouchableOpacity
        style={
          styles.primaryButton
        }
        onPress={() =>
          setScreen('login')
        }
      >
        <Text
          style={
            styles.primaryButtonText
          }
        >
          Return to Login
        </Text>
      </TouchableOpacity>
    </View>
  );
};

// ============================================================================
// Styles
// ============================================================================

const styles = StyleSheet.create({

  // --------------------------------------------------------------------------
  // General
  // --------------------------------------------------------------------------

  screen: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },

  loadingScreen: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f7fa',
    padding: 20,
  },

  loadingText: {
    marginTop: 12,
    fontSize: 15,
    color: '#555',
  },

  logo: {
    fontSize: 42,
    fontWeight: '800',
    letterSpacing: 3,
    marginBottom: 8,
    color: '#1f2937',
  },

  title: {
    fontSize: 24,
    fontWeight: '700',
    textAlign: 'center',
    color: '#1f2937',
    marginBottom: 8,
  },

  subtitle: {
    fontSize: 15,
    textAlign: 'center',
    color: '#6b7280',
    marginBottom: 24,
  },

  // --------------------------------------------------------------------------
  // Authentication
  // --------------------------------------------------------------------------

  authContainer: {
    width: '100%',
    maxWidth: 480,
    alignSelf: 'center',
    paddingHorizontal: 24,
    paddingTop: 70,
  },

  input: {
    width: '100%',
    minHeight: 50,
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 10,
    backgroundColor: '#fff',
    paddingHorizontal: 15,
    fontSize: 15,
    color: '#111827',
    marginBottom: 14,
  },

  primaryButton: {
    minHeight: 50,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2563eb',
    paddingHorizontal: 20,
    marginTop: 8,
  },

  primaryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },

  secondaryButton: {
    minHeight: 50,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#2563eb',
    paddingHorizontal: 20,
    marginTop: 10,
  },

  secondaryButtonText: {
    color: '#2563eb',
    fontSize: 16,
    fontWeight: '700',
  },

  // --------------------------------------------------------------------------
  // Dashboard
  // --------------------------------------------------------------------------

  dashboardHeader: {
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 18,
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },

  dashboardGreeting: {
    fontSize: 14,
    color: '#6b7280',
  },

  dashboardUsername: {
    fontSize: 22,
    fontWeight: '700',
    color: '#111827',
    marginTop: 2,
  },

  logoutText: {
    color: '#dc2626',
    fontSize: 15,
    fontWeight: '600',
  },

  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingTop: 16,
    gap: 12,
  },

  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },

  statLabel: {
    fontSize: 13,
    color: '#6b7280',
    marginBottom: 5,
  },

  statValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
  },

  createWalletButton: {
    marginHorizontal: 16,
    marginTop: 16,
    minHeight: 50,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#2563eb',
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
    paddingHorizontal: 16,
    marginTop: 22,
    marginBottom: 10,
  },

  // --------------------------------------------------------------------------
  // Wallet
  // --------------------------------------------------------------------------

  walletCard: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginTop: 12,
    borderRadius: 14,
    padding: 18,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },

  walletHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },

  walletHeaderLeft: {
    flex: 1,
    paddingRight: 10,
  },

  walletLabel: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
  },

  walletBlockchain: {
    marginTop: 4,
    fontSize: 12,
    fontWeight: '600',
    color: '#6b7280',
  },

  walletBalance: {
    fontSize: 25,
    fontWeight: '700',
    color: '#111827',
    marginTop: 18,
  },

  walletAddress: {
    marginTop: 8,
    fontSize: 13,
    color: '#2563eb',
  },

  walletActions: {
    flexDirection: 'row',
    marginTop: 16,
    gap: 10,
  },

  walletActionButton: {
    flex: 1,
    minHeight: 44,
    borderRadius: 9,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#eff6ff',
    borderWidth: 1,
    borderColor: '#bfdbfe',
  },

  walletActionText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#2563eb',
  },

  inspectButton: {
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 8,
    backgroundColor: '#f3f4f6',
  },

  inspectButtonText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#374151',
  },

  historyButton: {
    marginHorizontal: 16,
    marginTop: 6,
    marginBottom: 4,
    paddingVertical: 10,
    alignItems: 'center',
  },

  historyButtonText: {
    color: '#2563eb',
    fontSize: 13,
    fontWeight: '600',
  },

  // --------------------------------------------------------------------------
  // Modals
  // --------------------------------------------------------------------------

  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.45)',
    justifyContent: 'flex-end',
  },

  modalContainer: {
    width: '100%',
    maxHeight: '90%',
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 22,
  },

  largeModalContainer: {
    width: '100%',
    height: '90%',
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
  },

  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },

  modalTitle: {
    fontSize: 21,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 18,
  },

  closeButton: {
    fontSize: 22,
    color: '#6b7280',
    padding: 5,
  },

  fieldLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 6,
  },

  blockchainRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 16,
  },

  blockchainButton: {
    flex: 1,
    minHeight: 44,
    borderRadius: 9,
    borderWidth: 1,
    borderColor: '#d1d5db',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
  },

  blockchainButtonActive: {
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
  },

  blockchainButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6b7280',
  },

  blockchainButtonTextActive: {
    color: '#2563eb',
  },

  selectedWalletBox: {
    backgroundColor: '#f9fafb',
    borderRadius: 10,
    padding: 13,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },

  selectedWalletLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 3,
  },

  selectedWalletValue: {
    fontSize: 15,
    fontWeight: '700',
    color: '#111827',
  },

  addressText: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
  },

  receiveDescription: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 16,
  },

  receiveAddressBox: {
    backgroundColor: '#f3f4f6',
    borderRadius: 10,
    padding: 16,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },

  receiveAddress: {
    fontSize: 14,
    lineHeight: 21,
    color: '#111827',
  },

  // --------------------------------------------------------------------------
  // Inspection
  // --------------------------------------------------------------------------

  inspectionSection: {
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    padding: 14,
    marginBottom: 18,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },

  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingVertical: 9,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },

  infoLabel: {
    flex: 0.4,
    fontSize: 13,
    color: '#6b7280',
  },

  infoValue: {
    flex: 0.6,
    fontSize: 13,
    fontWeight: '600',
    color: '#111827',
    textAlign: 'right',
  },

  tokenRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 13,
    paddingHorizontal: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },

  tokenInfo: {
    flex: 1,
  },

  tokenName: {
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
  },

  tokenSymbol: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 2,
  },

  tokenBalance: {
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
  },

  // --------------------------------------------------------------------------
  // Transactions
  // --------------------------------------------------------------------------

  transactionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },

  transactionMain: {
    flex: 1,
    paddingRight: 10,
  },

  transactionHash: {
    fontSize: 13,
    fontWeight: '600',
    color: '#2563eb',
  },

  transactionMeta: {
    fontSize: 11,
    color: '#6b7280',
    marginTop: 4,
  },

  transactionRight: {
    alignItems: 'flex-end',
  },

  transactionAmount: {
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
  },

  transactionStatus: {
    fontSize: 11,
    color: '#6b7280',
    marginTop: 4,
    textTransform: 'capitalize',
  },

  statusConfirmed: {
    color: '#16a34a',
  },

  statusFailed: {
    color: '#dc2626',
  },

  // --------------------------------------------------------------------------
  // States
  // --------------------------------------------------------------------------

  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },

  errorContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },

  errorText: {
    fontSize: 14,
    color: '#dc2626',
    textAlign: 'center',
    marginBottom: 14,
  },

  emptyContainer: {
    padding: 30,
    alignItems: 'center',
    justifyContent: 'center',
  },

  emptyText: {
    fontSize: 15,
    color: '#6b7280',
    textAlign: 'center',
  },

  emptySubtext: {
    fontSize: 13,
    color: '#9ca3af',
    textAlign: 'center',
    marginTop: 6,
  },

});

// ============================================================================
// Export
// ============================================================================

export default App;
import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  TextInput,
  ScrollView,
  ActivityIndicator,
  Alert,
  Modal,
  Pressable,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// ============================================================================
// UBP Mobile API Configuration
// ============================================================================

const API_URL = 'http://localhost:5000';

const MOBILE_API_URL = `${API_URL}/api/mobile`;

const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  IS_LOGGED_IN: 'isLoggedIn',
};


// ============================================================================
// API Helpers
// ============================================================================

/**
 * Parse a JSON response safely.
 */
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
 * Store authentication information locally.
 */
const storeAuthentication = async (token, user) => {
  if (!token) {
    throw new Error('Authentication token was not returned by the server');
  }

  await AsyncStorage.setItem(STORAGE_KEYS.TOKEN, token);

  if (user) {
    await AsyncStorage.setItem(
      STORAGE_KEYS.USER,
      JSON.stringify(user)
    );
  }

  await AsyncStorage.setItem(
    STORAGE_KEYS.IS_LOGGED_IN,
    'true'
  );
};


/**
 * Clear authentication information.
 */
const clearAuthentication = async () => {
  await AsyncStorage.multiRemove([
    STORAGE_KEYS.TOKEN,
    STORAGE_KEYS.USER,
    STORAGE_KEYS.IS_LOGGED_IN,
  ]);
};


/**
 * Retrieve the stored authentication token.
 */
const getAuthToken = async () => {
  return await AsyncStorage.getItem(STORAGE_KEYS.TOKEN);
};


/**
 * Retrieve the stored user.
 */
const getStoredUser = async () => {
  const user = await AsyncStorage.getItem(STORAGE_KEYS.USER);

  if (!user) {
    return null;
  }

  try {
    return JSON.parse(user);
  } catch (error) {
    console.error('Unable to parse stored user:', error);
    return null;
  }
};


// ============================================================================
// Login Screen
// ============================================================================

const LoginScreen = ({ navigation }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);


  const handleLogin = async () => {
    if (!username.trim() || !password) {
      Alert.alert(
        'Error',
        'Please enter your username and password.'
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

      if (response.ok && data.success && data.token) {
        await storeAuthentication(
          data.token,
          data.user
        );

        navigation.replace('Dashboard');
        return;
      }

      Alert.alert(
        'Login Failed',
        data.error || 'Unable to sign in.'
      );

    } catch (error) {
      console.error('Mobile login error:', error);

      Alert.alert(
        'Network Error',
        'Unable to connect to the UBP server. Please check that the server is running.'
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <View style={styles.container}>
      <Text style={styles.title}>🌐 UBP</Text>

      <Text style={styles.subtitle}>
        Sign in to your account
      </Text>

      <View style={styles.form}>

        <TextInput
          style={styles.input}
          placeholder="Username"
          placeholderTextColor="#6a7a8e"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
          autoCorrect={false}
          editable={!loading}
        />

        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#6a7a8e"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          editable={!loading}
        />

        <TouchableOpacity
          style={styles.button}
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>
              Sign In
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => navigation.navigate('Register')}
          disabled={loading}
        >
          <Text style={styles.link}>
            Don't have an account? Register
          </Text>
        </TouchableOpacity>

      </View>
    </View>
  );
};


// ============================================================================
// Register Screen
// ============================================================================

const RegisterScreen = ({ navigation }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);


  const handleRegister = async () => {
    if (
      !username.trim() ||
      !email.trim() ||
      !password ||
      !confirmPassword
    ) {
      Alert.alert(
        'Error',
        'Please fill in all fields.'
      );
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert(
        'Error',
        'Passwords do not match.'
      );
      return;
    }

    if (password.length < 8) {
      Alert.alert(
        'Error',
        'Password must be at least 8 characters.'
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

      if (response.ok && data.success && data.token) {
        await storeAuthentication(
          data.token,
          data.user
        );

        navigation.replace('Dashboard');
        return;
      }

      Alert.alert(
        'Registration Failed',
        data.error || 'Unable to create your account.'
      );

    } catch (error) {
      console.error(
        'Mobile registration error:',
        error
      );

      Alert.alert(
        'Network Error',
        'Unable to connect to the UBP server. Please try again.'
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <View style={styles.container}>
      <Text style={styles.title}>🌐 UBP</Text>

      <Text style={styles.subtitle}>
        Create your account
      </Text>

      <View style={styles.form}>

        <TextInput
          style={styles.input}
          placeholder="Username"
          placeholderTextColor="#6a7a8e"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
          autoCorrect={false}
          editable={!loading}
        />

        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor="#6a7a8e"
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="email-address"
          editable={!loading}
        />

        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#6a7a8e"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          editable={!loading}
        />

        <TextInput
          style={styles.input}
          placeholder="Confirm Password"
          placeholderTextColor="#6a7a8e"
          value={confirmPassword}
          onChangeText={setConfirmPassword}
          secureTextEntry
          editable={!loading}
        />

        <TouchableOpacity
          style={styles.button}
          onPress={handleRegister}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>
              Create Account
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => navigation.navigate('Login')}
          disabled={loading}
        >
          <Text style={styles.link}>
            Already have an account? Sign In
          </Text>
        </TouchableOpacity>

      </View>
    </View>
  );
};


// ============================================================================
// Send Transaction Modal
// ============================================================================

const SendTransactionModal = ({ visible, onClose, onSuccess, wallet, token }) => {
  const [toAddress, setToAddress] = useState('');
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [asset, setAsset] = useState('ETH');

  useEffect(() => {
    if (wallet) {
      const assetMap = {
        'ethereum': 'ETH',
        'bitcoin': 'BTC',
        'tron': 'TRX',
      };
      setAsset(assetMap[wallet.blockchain] || 'ETH');
    }
  }, [wallet]);

  const handleSend = async () => {
    if (!toAddress.trim()) {
      Alert.alert('Error', 'Please enter a recipient address.');
      return;
    }

    const amountNum = parseFloat(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      Alert.alert('Error', 'Please enter a valid amount.');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${MOBILE_API_URL}/wallets/${wallet.wallet_id}/send`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            to_address: toAddress.trim(),
            amount: amountNum,
          }),
        }
      );

      const data = await parseResponse(response);

      if (data.success) {
        Alert.alert(
          '✅ Transaction Sent',
          `Transaction sent successfully!\n\nTx Hash: ${data.transaction.tx_hash.slice(0, 16)}...\nAmount: ${data.transaction.amount} ${data.transaction.asset}\nStatus: ${data.transaction.status}`
        );
        setToAddress('');
        setAmount('');
        onSuccess();
        onClose();
      } else {
        Alert.alert('Error', data.error || 'Failed to send transaction.');
      }
    } catch (error) {
      console.error('Send transaction error:', error);
      Alert.alert('Error', 'Unable to send transaction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!wallet) return null;

  const displayAddress = wallet.address.slice(0, 16) + '...';

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>📤 Send {asset}</Text>
            <TouchableOpacity onPress={onClose} style={styles.modalClose}>
              <Text style={styles.modalCloseText}>✕</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.modalBody}>
            <View style={styles.sendFromInfo}>
              <Text style={styles.sendFromLabel}>From:</Text>
              <Text style={styles.sendFromAddress}>{displayAddress}</Text>
              <Text style={styles.sendFromBlockchain}>{wallet.blockchain.toUpperCase()} • {wallet.label}</Text>
            </View>

            <Text style={styles.modalLabel}>Recipient Address</Text>
            <TextInput
              style={styles.modalInput}
              placeholder="0x..."
              placeholderTextColor="#6a7a8e"
              value={toAddress}
              onChangeText={setToAddress}
              editable={!loading}
              autoCapitalize="none"
            />

            <Text style={styles.modalLabel}>Amount ({asset})</Text>
            <TextInput
              style={styles.modalInput}
              placeholder="0.001"
              placeholderTextColor="#6a7a8e"
              value={amount}
              onChangeText={setAmount}
              editable={!loading}
              keyboardType="decimal-pad"
            />

            <TouchableOpacity
              style={[styles.modalButton, loading && styles.modalButtonDisabled]}
              onPress={handleSend}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="white" size="small" />
              ) : (
                <Text style={styles.modalButtonText}>Send {asset}</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};


// ============================================================================
// Wallet Creation Modal
// ============================================================================

const CreateWalletModal = ({ visible, onClose, onSuccess, token }) => {
  const [blockchain, setBlockchain] = useState('ethereum');
  const [label, setLabel] = useState('');
  const [loading, setLoading] = useState(false);

  const blockchainOptions = [
    { value: 'ethereum', label: '🟣 Ethereum', color: '#6c5ce7' },
    { value: 'bitcoin', label: '🟠 Bitcoin', color: '#f7931a' },
    { value: 'tron', label: '🔴 TRON', color: '#ef4444' },
  ];

  const handleCreate = async () => {
    if (!label.trim()) {
      Alert.alert('Error', 'Please enter a wallet label.');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${MOBILE_API_URL}/wallets/create`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            blockchain: blockchain,
            label: label.trim(),
          }),
        }
      );

      const data = await parseResponse(response);

      if (data.success) {
        Alert.alert(
          '✅ Wallet Created',
          `${blockchain.charAt(0).toUpperCase() + blockchain.slice(1)} wallet created successfully!\n\nAddress: ${data.wallet.address.slice(0, 16)}...`
        );
        setLabel('');
        onSuccess();
        onClose();
      } else {
        Alert.alert('Error', data.error || 'Failed to create wallet.');
      }
    } catch (error) {
      console.error('Create wallet error:', error);
      Alert.alert('Error', 'Unable to create wallet. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>➕ Create Wallet</Text>
            <TouchableOpacity onPress={onClose} style={styles.modalClose}>
              <Text style={styles.modalCloseText}>✕</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.modalBody}>
            <Text style={styles.modalLabel}>Select Blockchain</Text>
            <View style={styles.blockchainOptions}>
              {blockchainOptions.map((option) => (
                <TouchableOpacity
                  key={option.value}
                  style={[
                    styles.blockchainOption,
                    blockchain === option.value && {
                      borderColor: option.color,
                      backgroundColor: `${option.color}15`,
                    },
                  ]}
                  onPress={() => setBlockchain(option.value)}
                >
                  <Text style={styles.blockchainOptionText}>
                    {option.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <Text style={styles.modalLabel}>Wallet Label</Text>
            <TextInput
              style={styles.modalInput}
              placeholder="e.g., My ETH Wallet"
              placeholderTextColor="#6a7a8e"
              value={label}
              onChangeText={setLabel}
              editable={!loading}
            />

            <TouchableOpacity
              style={[styles.modalButton, loading && styles.modalButtonDisabled]}
              onPress={handleCreate}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="white" size="small" />
              ) : (
                <Text style={styles.modalButtonText}>Create Wallet</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};


// ============================================================================
// Dashboard Screen
// ============================================================================

const DashboardScreen = ({ navigation }) => {
  const [stats, setStats] = useState({
    total_wallets: 0,
    total_transactions: 0,
    by_blockchain: {
      ethereum: { wallets: 0, transactions: 0 },
      bitcoin: { wallets: 0, transactions: 0 },
      tron: { wallets: 0, transactions: 0 },
    },
    recent_activity: [],
  });

  const [wallets, setWallets] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [sendModalVisible, setSendModalVisible] = useState(false);
  const [selectedWallet, setSelectedWallet] = useState(null);
  const [token, setToken] = useState(null);


  useEffect(() => {
    loadDashboard();
  }, []);


  const loadDashboard = async () => {
    try {
      const authToken = await getAuthToken();

      if (!authToken) {
        await clearAuthentication();
        navigation.replace('Login');
        return;
      }

      setToken(authToken);

      // ------------------------------------------------------------
      // Validate the mobile authentication token first.
      // ------------------------------------------------------------

      const authResponse = await fetch(
        `${MOBILE_API_URL}/auth/me`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (authResponse.status === 401) {
        await clearAuthentication();
        Alert.alert(
          'Session Expired',
          'Please sign in again.'
        );
        navigation.replace('Login');
        return;
      }

      if (!authResponse.ok) {
        throw new Error('Unable to validate authentication session');
      }

      const authData = await parseResponse(authResponse);

      if (!authData.success || !authData.user) {
        await clearAuthentication();
        navigation.replace('Login');
        return;
      }

      setUser(authData.user);

      // ------------------------------------------------------------
      // Fetch dashboard statistics from the mobile endpoint.
      // ------------------------------------------------------------

      const response = await fetch(
        `${MOBILE_API_URL}/dashboard/stats`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await parseResponse(response);

        if (data.success && data.data) {
          setStats({
            total_wallets: data.data.total_wallets ?? 0,
            total_transactions: data.data.total_transactions ?? 0,
            by_blockchain: data.data.by_blockchain || {
              ethereum: { wallets: 0, transactions: 0 },
              bitcoin: { wallets: 0, transactions: 0 },
              tron: { wallets: 0, transactions: 0 },
            },
            recent_activity: data.data.recent_activity || [],
          });
        }
      } else if (response.status === 401) {
        await clearAuthentication();
        Alert.alert(
          'Session Expired',
          'Please sign in again.'
        );
        navigation.replace('Login');
        return;
      }

      // ------------------------------------------------------------
      // Fetch wallets list
      // ------------------------------------------------------------

      const walletsResponse = await fetch(
        `${MOBILE_API_URL}/wallets`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (walletsResponse.ok) {
        const data = await parseResponse(walletsResponse);
        if (data.success) {
          setWallets(data.wallets || []);
        }
      }

    } catch (error) {
      console.error('Dashboard loading error:', error);

      setStats({
        total_wallets: 0,
        total_transactions: 0,
        by_blockchain: {
          ethereum: { wallets: 0, transactions: 0 },
          bitcoin: { wallets: 0, transactions: 0 },
          tron: { wallets: 0, transactions: 0 },
        },
        recent_activity: [],
      });

    } finally {
      setLoading(false);
    }
  };


  const refreshDashboard = async () => {
    setLoading(true);
    await loadDashboard();
    setLoading(false);
  };


  const handleLogout = async () => {
    try {
      const authToken = await getAuthToken();
      if (authToken) {
        try {
          await fetch(
            `${MOBILE_API_URL}/auth/logout`,
            {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json',
              },
            }
          );
        } catch (e) {
          // Ignore logout endpoint errors
        }
      }
      await clearAuthentication();
    } catch (error) {
      console.error('Logout storage error:', error);
    }

    navigation.replace('Login');
  };


  const openSendModal = (wallet) => {
    setSelectedWallet(wallet);
    setSendModalVisible(true);
  };


  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator
          size="large"
          color="#6c5ce7"
        />
      </View>
    );
  }


  return (
    <SafeAreaView style={styles.safe}>

      <View style={styles.dashboardHeader}>

        <View>
          <Text style={styles.title}>
            📊 Dashboard
          </Text>

          {user?.username ? (
            <Text style={styles.dashboardUser}>
              Welcome, {user.username}
            </Text>
          ) : null}
        </View>

        <View style={styles.headerActions}>
          <TouchableOpacity
            onPress={refreshDashboard}
            style={styles.refreshButton}
          >
            <Text style={styles.refreshButtonText}>🔄</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={handleLogout}
          >
            <Text style={styles.logoutLink}>🚪</Text>
          </TouchableOpacity>
        </View>

      </View>


      <ScrollView style={styles.container}>

        <View style={styles.statsGrid}>

          <View
            style={[
              styles.statCard,
              {
                borderColor: '#6c5ce7',
              },
            ]}
          >
            <Text style={styles.statValue}>
              {stats.total_wallets}
            </Text>

            <Text style={styles.statLabel}>
              Total Wallets
            </Text>
          </View>

          <View
            style={[
              styles.statCard,
              {
                borderColor: '#00b894',
              },
            ]}
          >
            <Text style={styles.statValue}>
              {stats.total_transactions}
            </Text>

            <Text style={styles.statLabel}>
              Transactions
            </Text>
          </View>

          <View
            style={[
              styles.statCard,
              {
                borderColor: '#6c5ce7',
              },
            ]}
          >
            <Text style={styles.statValue}>
              {stats.by_blockchain?.ethereum?.wallets || 0}
            </Text>

            <Text style={styles.statLabel}>
              🟣 ETH Wallets
            </Text>
          </View>

          <View
            style={[
              styles.statCard,
              {
                borderColor: '#f7931a',
              },
            ]}
          >
            <Text style={styles.statValue}>
              {stats.by_blockchain?.bitcoin?.wallets || 0}
            </Text>

            <Text style={styles.statLabel}>
              🟠 BTC Wallets
            </Text>
          </View>

          <View
            style={[
              styles.statCard,
              {
                borderColor: '#ef4444',
              },
            ]}
          >
            <Text style={styles.statValue}>
              {stats.by_blockchain?.tron?.wallets || 0}
            </Text>

            <Text style={styles.statLabel}>
              🔴 TRX Wallets
            </Text>
          </View>

        </View>

        {/* Create Wallet Button */}
        <TouchableOpacity
          style={styles.createWalletButton}
          onPress={() => setCreateModalVisible(true)}
        >
          <Text style={styles.createWalletButtonText}>➕ Create New Wallet</Text>
        </TouchableOpacity>

        {/* Wallet List */}
        {wallets.length > 0 && (
          <View style={styles.walletSection}>
            <Text style={styles.sectionTitle}>My Wallets</Text>
            {wallets.map((wallet) => {
              const assetMap = {
                'ethereum': 'ETH',
                'bitcoin': 'BTC',
                'tron': 'TRX',
              };
              const colorMap = {
                'ethereum': '#6c5ce7',
                'bitcoin': '#f7931a',
                'tron': '#ef4444',
              };
              return (
                <View key={wallet.id} style={styles.walletItem}>
                  <View style={styles.walletInfo}>
                    <Text style={styles.walletLabel}>
                      {wallet.label || 'Unnamed Wallet'}
                    </Text>
                    <Text style={styles.walletAddress}>
                      {wallet.address.slice(0, 16)}...
                    </Text>
                    <Text style={[styles.walletBlockchain, { color: colorMap[wallet.blockchain] || '#6a7a8e' }]}>
                      {wallet.blockchain.toUpperCase()} • {wallet.network}
                    </Text>
                  </View>
                  <View style={styles.walletActions}>
                    <TouchableOpacity
                      style={[styles.walletAction, styles.sendButton]}
                      onPress={() => openSendModal(wallet)}
                    >
                      <Text style={styles.walletActionText}>📤 Send</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={styles.walletAction}
                      onPress={() => {
                        Alert.alert(
                          wallet.label || 'Wallet',
                          `Address: ${wallet.address}\nBlockchain: ${wallet.blockchain}\nNetwork: ${wallet.network}\nAsset: ${assetMap[wallet.blockchain] || 'Unknown'}`
                        );
                      }}
                    >
                      <Text style={styles.walletActionText}>👁️</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              );
            })}
          </View>
        )}

        {/* Recent Activity Section */}
        {stats.recent_activity && stats.recent_activity.length > 0 && (
          <View style={styles.recentActivitySection}>
            <Text style={styles.sectionTitle}>Recent Activity</Text>

            {stats.recent_activity.slice(0, 5).map((item, index) => (
              <View key={index} style={styles.activityItem}>
                <View style={styles.activityIcon}>
                  <Text>
                    {item.type === 'wallet_inspection' ? '👛' : '📤'}
                  </Text>
                </View>
                <View style={styles.activityContent}>
                  <Text style={styles.activityText}>
                    {item.type === 'wallet_inspection'
                      ? `Inspected ${item.blockchain} wallet`
                      : `${item.blockchain} transaction ${item.amount ? `(${item.amount} ${item.asset})` : ''}`
                    }
                  </Text>
                  <Text style={styles.activityAddress}>
                    {item.address ? `${item.address.slice(0, 10)}...` : ''}
                  </Text>
                </View>
                <Text style={styles.activityTime}>
                  {item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}
                </Text>
              </View>
            ))}
          </View>
        )}

      </ScrollView>

      {/* Create Wallet Modal */}
      <CreateWalletModal
        visible={createModalVisible}
        onClose={() => setCreateModalVisible(false)}
        onSuccess={refreshDashboard}
        token={token}
      />

      {/* Send Transaction Modal */}
      <SendTransactionModal
        visible={sendModalVisible}
        onClose={() => {
          setSendModalVisible(false);
          setSelectedWallet(null);
        }}
        onSuccess={refreshDashboard}
        wallet={selectedWallet}
        token={token}
      />

    </SafeAreaView>
  );
};


// ============================================================================
// App Navigation
// ============================================================================

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(null);
  const [currentScreen, setCurrentScreen] = useState('Login');


  useEffect(() => {
    checkLogin();
  }, []);


  const checkLogin = async () => {
    try {
      const token = await getAuthToken();

      if (!token) {
        await clearAuthentication();

        setIsLoggedIn(false);
        setCurrentScreen('Login');
        return;
      }


      // ------------------------------------------------------------
      // Verify that the stored token is still valid.
      // ------------------------------------------------------------

      const response = await fetch(
        `${MOBILE_API_URL}/auth/me`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );


      if (!response.ok) {
        await clearAuthentication();

        setIsLoggedIn(false);
        setCurrentScreen('Login');
        return;
      }


      const data = await parseResponse(response);


      if (
        !data.success ||
        !data.user
      ) {
        await clearAuthentication();

        setIsLoggedIn(false);
        setCurrentScreen('Login');
        return;
      }


      // Refresh stored user information.
      await AsyncStorage.setItem(
        STORAGE_KEYS.USER,
        JSON.stringify(data.user)
      );

      await AsyncStorage.setItem(
        STORAGE_KEYS.IS_LOGGED_IN,
        'true'
      );


      setIsLoggedIn(true);
      setCurrentScreen('Dashboard');

    } catch (error) {
      console.error(
        'Authentication check error:',
        error
      );

      // If the server cannot be reached, do not assume
      // the user is logged out permanently.
      //
      // For startup, however, we need a deterministic screen.
      // The user can sign in again if necessary.
      setIsLoggedIn(false);
      setCurrentScreen('Login');
    }
  };


  if (isLoggedIn === null) {
    return (
      <View style={styles.center}>
        <ActivityIndicator
          size="large"
          color="#6c5ce7"
        />
      </View>
    );
  }


  const renderScreen = () => {
    switch (currentScreen) {

      case 'Login':
        return (
          <LoginScreen
            navigation={{
              navigate: setCurrentScreen,
              replace: setCurrentScreen,
            }}
          />
        );


      case 'Register':
        return (
          <RegisterScreen
            navigation={{
              navigate: setCurrentScreen,
              replace: setCurrentScreen,
            }}
          />
        );


      case 'Dashboard':
        return (
          <DashboardScreen
            navigation={{
              navigate: setCurrentScreen,
              replace: setCurrentScreen,
            }}
          />
        );


      default:
        return (
          <LoginScreen
            navigation={{
              navigate: setCurrentScreen,
              replace: setCurrentScreen,
            }}
          />
        );
    }
  };


  return (
    <SafeAreaView style={styles.safe}>

      <StatusBar
        barStyle="light-content"
        backgroundColor="#0a0e17"
      />

      {renderScreen()}

    </SafeAreaView>
  );
};


// ============================================================================
// Styles
// ============================================================================

const styles = StyleSheet.create({

  safe: {
    flex: 1,
    backgroundColor: '#0a0e17',
  },

  container: {
    flex: 1,
    backgroundColor: '#0a0e17',
    padding: 20,
  },

  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#0a0e17',
  },

  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#e0e6ed',
    textAlign: 'center',
    marginBottom: 4,
  },

  subtitle: {
    color: '#6a7a8e',
    textAlign: 'center',
    marginBottom: 30,
    fontSize: 14,
  },

  form: {
    gap: 12,
  },

  input: {
    backgroundColor: '#141b2b',
    padding: 14,
    borderRadius: 10,
    color: '#e0e6ed',
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#1e2a3e',
  },

  button: {
    backgroundColor: '#6c5ce7',
    padding: 16,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 4,
  },

  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },

  link: {
    color: '#6c5ce7',
    textAlign: 'center',
    marginTop: 12,
    fontSize: 14,
  },

  dashboardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 10,
  },

  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },

  refreshButton: {
    padding: 4,
  },

  refreshButtonText: {
    fontSize: 20,
  },

  dashboardUser: {
    color: '#8a9aae',
    fontSize: 13,
    marginTop: 2,
  },

  logoutLink: {
    fontSize: 24,
    color: '#ef4444',
  },

  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 16,
  },

  statCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#141b2b',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
  },

  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#e0e6ed',
  },

  statLabel: {
    color: '#8a9aae',
    fontSize: 12,
    marginTop: 4,
  },

  createWalletButton: {
    backgroundColor: '#6c5ce7',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },

  createWalletButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },

  walletSection: {
    marginBottom: 16,
  },

  sectionTitle: {
    color: '#e0e6ed',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },

  walletItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#141b2b',
    padding: 14,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#1e2a3e',
    marginBottom: 8,
  },

  walletInfo: {
    flex: 1,
  },

  walletLabel: {
    color: '#e0e6ed',
    fontSize: 14,
    fontWeight: '500',
  },

  walletAddress: {
    color: '#6a7a8e',
    fontSize: 12,
    fontFamily: 'monospace',
    marginTop: 1,
  },

  walletBlockchain: {
    fontSize: 11,
    marginTop: 1,
  },

  walletActions: {
    flexDirection: 'row',
    gap: 8,
  },

  walletAction: {
    padding: 6,
  },

  sendButton: {
    backgroundColor: '#6c5ce7',
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },

  walletActionText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#e0e6ed',
  },

  recentActivitySection: {
    marginTop: 4,
    backgroundColor: '#141b2b',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#1e2a3e',
    marginBottom: 16,
  },

  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1f2e',
  },

  activityIcon: {
    width: 30,
    alignItems: 'center',
  },

  activityContent: {
    flex: 1,
    marginLeft: 8,
  },

  activityText: {
    color: '#e0e6ed',
    fontSize: 13,
  },

  activityAddress: {
    color: '#6a7a8e',
    fontSize: 11,
    marginTop: 1,
  },

  activityTime: {
    color: '#4a5a6e',
    fontSize: 10,
    marginLeft: 8,
  },

  // Modal Styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },

  modalContent: {
    backgroundColor: '#141b2b',
    borderRadius: 16,
    width: '90%',
    maxWidth: 400,
    borderWidth: 1,
    borderColor: '#1e2a3e',
    overflow: 'hidden',
  },

  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1e2a3e',
  },

  modalTitle: {
    color: '#e0e6ed',
    fontSize: 18,
    fontWeight: '600',
  },

  modalClose: {
    padding: 4,
  },

  modalCloseText: {
    color: '#6a7a8e',
    fontSize: 20,
  },

  modalBody: {
    padding: 16,
  },

  modalLabel: {
    color: '#8a9aae',
    fontSize: 14,
    marginBottom: 8,
    marginTop: 8,
  },

  modalInput: {
    backgroundColor: '#0d1422',
    padding: 12,
    borderRadius: 8,
    color: '#e0e6ed',
    fontSize: 14,
    borderWidth: 1,
    borderColor: '#1e2a3e',
    marginBottom: 16,
  },

  blockchainOptions: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },

  blockchainOption: {
    flex: 1,
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#1e2a3e',
    alignItems: 'center',
  },

  blockchainOptionText: {
    color: '#e0e6ed',
    fontSize: 12,
    fontWeight: '500',
  },

  modalButton: {
    backgroundColor: '#6c5ce7',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 4,
  },

  modalButtonDisabled: {
    opacity: 0.6,
  },

  modalButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },

  // Send Transaction specific
  sendFromInfo: {
    backgroundColor: '#0d1422',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#1e2a3e',
  },

  sendFromLabel: {
    color: '#6a7a8e',
    fontSize: 12,
  },

  sendFromAddress: {
    color: '#e0e6ed',
    fontSize: 14,
    fontFamily: 'monospace',
    marginTop: 2,
  },

  sendFromBlockchain: {
    color: '#6c5ce7',
    fontSize: 12,
    marginTop: 2,
  },

});


export default App;
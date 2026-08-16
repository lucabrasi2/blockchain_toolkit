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
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API Base URL - We'll update this later
const API_URL = 'http://localhost:5000';

// ============ Login Screen ============
const LoginScreen = ({ navigation }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        await AsyncStorage.setItem('user', JSON.stringify({ username }));
        await AsyncStorage.setItem('isLoggedIn', 'true');
        navigation.replace('Dashboard');
      } else {
        Alert.alert('Error', data.error || 'Login failed');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please check your connection.');
    }
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🌐 UBP</Text>
      <Text style={styles.subtitle}>Sign in to your account</Text>

      <View style={styles.form}>
        <TextInput
          style={styles.input}
          placeholder="Username"
          placeholderTextColor="#6a7a8e"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#6a7a8e"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>Sign In</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.navigate('Register')}>
          <Text style={styles.link}>Don't have an account? Register</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

// ============ Register Screen ============
const RegisterScreen = ({ navigation }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!username || !email || !password || !confirmPassword) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (password.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `username=${encodeURIComponent(username)}&email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}&confirm_password=${encodeURIComponent(confirmPassword)}`,
      });

      const data = await response.json();

      if (response.ok) {
        Alert.alert('Success', 'Registration successful! Please login.');
        navigation.navigate('Login');
      } else {
        Alert.alert('Error', data.error || 'Registration failed');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please try again.');
    }
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🌐 UBP</Text>
      <Text style={styles.subtitle}>Create your account</Text>

      <View style={styles.form}>
        <TextInput
          style={styles.input}
          placeholder="Username"
          placeholderTextColor="#6a7a8e"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
        />
        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor="#6a7a8e"
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#6a7a8e"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />
        <TextInput
          style={styles.input}
          placeholder="Confirm Password"
          placeholderTextColor="#6a7a8e"
          value={confirmPassword}
          onChangeText={setConfirmPassword}
          secureTextEntry
        />

        <TouchableOpacity style={styles.button} onPress={handleRegister} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>Create Account</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.navigate('Login')}>
          <Text style={styles.link}>Already have an account? Sign In</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

// ============ Dashboard Screen ============
const DashboardScreen = ({ navigation }) => {
  const [stats, setStats] = useState({ total_inspections: 0, ethereum: 0, bitcoin: 0, tron: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadDashboard(); }, []);

  const loadDashboard = async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      const response = await fetch(`${API_URL}/api/dashboard/stats`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });
      const data = await response.json();
      setStats(data);
    } catch (error) { console.error(error); }
    setLoading(false);
  };

  const handleLogout = async () => {
    await AsyncStorage.removeItem('user');
    await AsyncStorage.removeItem('isLoggedIn');
    navigation.replace('Login');
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6c5ce7" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.dashboardHeader}>
        <Text style={styles.title}>📊 Dashboard</Text>
        <TouchableOpacity onPress={handleLogout}>
          <Text style={styles.logoutLink}>🚪</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.container}>
        <View style={styles.statsGrid}>
          <View style={[styles.statCard, { borderColor: '#6c5ce7' }]}>
            <Text style={styles.statValue}>{stats.total_inspections}</Text>
            <Text style={styles.statLabel}>Total</Text>
          </View>
          <View style={[styles.statCard, { borderColor: '#6c5ce7' }]}>
            <Text style={styles.statValue}>{stats.ethereum}</Text>
            <Text style={styles.statLabel}>🟣 ETH</Text>
          </View>
          <View style={[styles.statCard, { borderColor: '#f7931a' }]}>
            <Text style={styles.statValue}>{stats.bitcoin}</Text>
            <Text style={styles.statLabel}>🟠 BTC</Text>
          </View>
          <View style={[styles.statCard, { borderColor: '#ef4444' }]}>
            <Text style={styles.statValue}>{stats.tron}</Text>
            <Text style={styles.statLabel}>🔴 TRX</Text>
          </View>
        </View>

        <View style={styles.quickActions}>
          <TouchableOpacity style={[styles.actionBtn, { backgroundColor: '#6c5ce7' }]} onPress={() => Alert.alert('Coming Soon', 'Ethereum features in development')}>
            <Text style={styles.actionText}>🟣 Ethereum</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.actionBtn, { backgroundColor: '#f7931a' }]} onPress={() => Alert.alert('Coming Soon', 'Bitcoin features in development')}>
            <Text style={styles.actionText}>🟠 Bitcoin</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.actionBtn, { backgroundColor: '#ef4444' }]} onPress={() => Alert.alert('Coming Soon', 'TRON features in development')}>
            <Text style={styles.actionText}>🔴 TRON</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

// ============ App Navigation ============
const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(null);
  const [currentScreen, setCurrentScreen] = useState('Login');

  useEffect(() => { checkLogin(); }, []);

  const checkLogin = async () => {
    const loggedIn = await AsyncStorage.getItem('isLoggedIn');
    setIsLoggedIn(loggedIn === 'true');
    setCurrentScreen(loggedIn === 'true' ? 'Dashboard' : 'Login');
  };

  if (isLoggedIn === null) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6c5ce7" />
      </View>
    );
  }

  const renderScreen = () => {
    switch (currentScreen) {
      case 'Login': return <LoginScreen navigation={{ navigate: setCurrentScreen, replace: setCurrentScreen }} />;
      case 'Register': return <RegisterScreen navigation={{ navigate: setCurrentScreen }} />;
      case 'Dashboard': return <DashboardScreen navigation={{ navigate: setCurrentScreen, replace: setCurrentScreen }} />;
      default: return <LoginScreen navigation={{ navigate: setCurrentScreen, replace: setCurrentScreen }} />;
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="light-content" backgroundColor="#0a0e17" />
      {renderScreen()}
    </SafeAreaView>
  );
};

// ============ Styles ============
const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#0a0e17' },
  container: { flex: 1, backgroundColor: '#0a0e17', padding: 20 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0a0e17' },
  title: { fontSize: 32, fontWeight: 'bold', color: '#e0e6ed', textAlign: 'center', marginBottom: 4 },
  subtitle: { color: '#6a7a8e', textAlign: 'center', marginBottom: 30, fontSize: 14 },
  form: { gap: 12 },
  input: { backgroundColor: '#141b2b', padding: 14, borderRadius: 10, color: '#e0e6ed', fontSize: 16, borderWidth: 1, borderColor: '#1e2a3e' },
  button: { backgroundColor: '#6c5ce7', padding: 16, borderRadius: 10, alignItems: 'center', marginTop: 4 },
  buttonText: { color: 'white', fontSize: 18, fontWeight: '600' },
  link: { color: '#6c5ce7', textAlign: 'center', marginTop: 12, fontSize: 14 },
  dashboardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 20, paddingTop: 10, paddingBottom: 10 },
  logoutLink: { fontSize: 24, color: '#ef4444' },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 16 },
  statCard: { flex: 1, minWidth: '45%', backgroundColor: '#141b2b', padding: 16, borderRadius: 12, borderWidth: 1, alignItems: 'center' },
  statValue: { fontSize: 28, fontWeight: 'bold', color: '#e0e6ed' },
  statLabel: { color: '#8a9aae', fontSize: 12, marginTop: 4 },
  quickActions: { flexDirection: 'row', justifyContent: 'space-between', gap: 8, marginBottom: 16 },
  actionBtn: { flex: 1, paddingVertical: 12, borderRadius: 10, alignItems: 'center' },
  actionText: { color: 'white', fontWeight: '600', fontSize: 14 },
});

export default App;

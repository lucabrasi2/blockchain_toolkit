/**
 * =============================================================================
 * Universal Blockchain Platform (UBP)
 *
 * Module
 * ------
 * mobile/api/client.js
 *
 * Purpose
 * -------
 * Centralized mobile API client.
 *
 * Responsibilities
 * ----------------
 * - Provide one HTTP interface for the mobile application
 * - Attach authentication tokens automatically
 * - Normalize UBP API responses
 * - Handle authentication failures consistently
 * - Handle network and server errors consistently
 *
 * Architectural Intent
 * --------------------
 * Screens must not contain duplicated fetch(), token handling, or response
 * parsing logic. All communication with the UBP mobile API goes through this
 * module.
 * =============================================================================
 */

import AsyncStorage from '@react-native-async-storage/async-storage';


/**
 * =============================================================================
 * Configuration
 * =============================================================================
 *
 * Android emulator:
 *     http://10.0.2.2:5000/api/mobile
 *
 * iOS simulator:
 *     http://127.0.0.1:5000/api/mobile
 *
 * Physical device:
 *     http://YOUR_COMPUTER_IP:5000/api/mobile
 *
 * Do not use localhost on a physical mobile device.
 */

export const API_URL = 'http://10.0.2.2:5000/api/mobile';


/**
 * =============================================================================
 * Storage Keys
 * =============================================================================
 */

export const AUTH_TOKEN_KEY = 'token';

export const USER_KEY = 'user';


/**
 * =============================================================================
 * API Error
 * =============================================================================
 */

export class APIError extends Error {
  constructor(
    message,
    status = null,
    data = null,
  ) {
    super(message);

    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}


/**
 * =============================================================================
 * Authentication Storage
 * =============================================================================
 */

export const getAuthToken = async () => {
  return AsyncStorage.getItem(
    AUTH_TOKEN_KEY,
  );
};


export const setAuthToken = async (
  token,
) => {
  if (!token) {
    await AsyncStorage.removeItem(
      AUTH_TOKEN_KEY,
    );

    return;
  }

  await AsyncStorage.setItem(
    AUTH_TOKEN_KEY,
    token,
  );
};


export const clearAuthSession = async () => {
  await AsyncStorage.multiRemove([
    AUTH_TOKEN_KEY,
    USER_KEY,
  ]);
};


/**
 * =============================================================================
 * Request Helper
 * =============================================================================
 */

const request = async (
  endpoint,
  options = {},
) => {
  const {
    method = 'GET',
    body = null,
    headers = {},
    authenticated = true,
  } = options;


  /**
   * ---------------------------------------------------------------------------
   * Authentication
   * ---------------------------------------------------------------------------
   */

  const token = authenticated
    ? await getAuthToken()
    : null;


  /**
   * ---------------------------------------------------------------------------
   * Headers
   * ---------------------------------------------------------------------------
   */

  const requestHeaders = {
    Accept: 'application/json',
    ...headers,
  };


  if (body !== null) {
    requestHeaders['Content-Type'] =
      'application/json';
  }


  if (token) {
    requestHeaders.Authorization =
      `Bearer ${token}`;
  }


  /**
   * ---------------------------------------------------------------------------
   * Request Body
   * ---------------------------------------------------------------------------
   */

  let requestBody = null;

  if (body !== null) {
    requestBody = JSON.stringify(
      body,
    );
  }


  /**
   * ---------------------------------------------------------------------------
   * HTTP Request
   * ---------------------------------------------------------------------------
   */

  let response;

  try {
    response = await fetch(
      `${API_URL}${endpoint}`,
      {
        method,
        headers: requestHeaders,
        body: requestBody,
      },
    );
  } catch (error) {
    throw new APIError(
      'Unable to connect to the UBP server. Please check your network connection.',
      null,
      null,
    );
  }


  /**
   * ---------------------------------------------------------------------------
   * Response Parsing
   * ---------------------------------------------------------------------------
   */

  let data = null;

  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }


  /**
   * ---------------------------------------------------------------------------
   * Authentication Failure
   * ---------------------------------------------------------------------------
   */

  if (response.status === 401) {
    await clearAuthSession();

    throw new APIError(
      data?.error ||
        'Invalid or expired access token',
      401,
      data,
    );
  }


  /**
   * ---------------------------------------------------------------------------
   * HTTP Error
   * ---------------------------------------------------------------------------
   */

  if (!response.ok) {
    throw new APIError(
      data?.error ||
        `Request failed with status ${response.status}`,
      response.status,
      data,
    );
  }


  /**
   * ---------------------------------------------------------------------------
   * UBP Response Contract
   * ---------------------------------------------------------------------------
   *
   * Successful responses normally use:
   *
   * {
   *     "success": true,
   *     "data": {...}
   * }
   *
   * Some existing endpoints may return additional top-level fields.
   * Therefore the complete response is returned unchanged.
   */

  if (
    data &&
    data.success === false
  ) {
    throw new APIError(
      data.error ||
        'UBP request failed',
      response.status,
      data,
    );
  }


  return data;
};


/**
 * =============================================================================
 * Public API Methods
 * =============================================================================
 */

export const api = {
  get: (
    endpoint,
    options = {},
  ) =>
    request(
      endpoint,
      {
        ...options,
        method: 'GET',
      },
    ),


  post: (
    endpoint,
    body = null,
    options = {},
  ) =>
    request(
      endpoint,
      {
        ...options,
        method: 'POST',
        body,
      },
    ),


  put: (
    endpoint,
    body = null,
    options = {},
  ) =>
    request(
      endpoint,
      {
        ...options,
        method: 'PUT',
        body,
      },
    ),


  delete: (
    endpoint,
    options = {},
  ) =>
    request(
      endpoint,
      {
        ...options,
        method: 'DELETE',
      },
    ),
};


/**
 * =============================================================================
 * Public Exports
 * =============================================================================
 */

export default api;


/**
 * =============================================================================
 * End of File
 * =============================================================================
 */

package com.voicedictation.util

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import timber.log.Timber

/**
 * Manages app configuration using EncryptedSharedPreferences.
 *
 * Security:
 * - API keys stored encrypted using Android Keystore
 * - Encryption tied to device and app signature
 * - Cannot be decrypted on different device
 */
class ConfigManager(context: Context) {

    companion object {
        private const val PREFS_NAME = "encrypted_prefs"
        private const val KEY_GROQ_API_KEY = "groq_api_key"
        private const val KEY_VOLUME_GAIN = "volume_gain"
        private const val KEY_SILENCE_TIMEOUT = "silence_timeout"

        private const val DEFAULT_VOLUME_GAIN = 1.0f
        private const val DEFAULT_SILENCE_TIMEOUT = 60000L // 60 seconds
    }

    private val sharedPreferences: SharedPreferences

    init {
        try {
            // Create or retrieve master key for encryption
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()

            // Create encrypted shared preferences
            sharedPreferences = EncryptedSharedPreferences.create(
                context,
                PREFS_NAME,
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )

            Timber.d("ConfigManager initialized with encrypted storage")
        } catch (e: Exception) {
            Timber.e(e, "Failed to initialize encrypted preferences")
            throw e
        }
    }

    /**
     * Get Groq API key
     */
    fun getGroqApiKey(): String {
        return sharedPreferences.getString(KEY_GROQ_API_KEY, "") ?: ""
    }

    /**
     * Set Groq API key (encrypted)
     */
    fun setGroqApiKey(apiKey: String) {
        sharedPreferences.edit()
            .putString(KEY_GROQ_API_KEY, apiKey)
            .apply()
        Timber.d("Groq API key saved")
    }

    /**
     * Get volume gain multiplier
     */
    fun getVolumeGain(): Float {
        return sharedPreferences.getFloat(KEY_VOLUME_GAIN, DEFAULT_VOLUME_GAIN)
    }

    /**
     * Set volume gain multiplier
     */
    fun setVolumeGain(gain: Float) {
        sharedPreferences.edit()
            .putFloat(KEY_VOLUME_GAIN, gain)
            .apply()
        Timber.d("Volume gain set to $gain")
    }

    /**
     * Get silence timeout in milliseconds
     */
    fun getSilenceTimeout(): Long {
        return sharedPreferences.getLong(KEY_SILENCE_TIMEOUT, DEFAULT_SILENCE_TIMEOUT)
    }

    /**
     * Set silence timeout in milliseconds
     */
    fun setSilenceTimeout(timeout: Long) {
        sharedPreferences.edit()
            .putLong(KEY_SILENCE_TIMEOUT, timeout)
            .apply()
        Timber.d("Silence timeout set to $timeout ms")
    }

    /**
     * Check if API key is configured
     */
    fun isConfigured(): Boolean {
        return getGroqApiKey().isNotEmpty()
    }

    /**
     * Clear all configuration (for testing/debugging)
     */
    fun clear() {
        sharedPreferences.edit().clear().apply()
        Timber.w("Configuration cleared")
    }

    /**
     * Get all configuration as map (for debugging, API key masked)
     */
    fun getDebugInfo(): Map<String, String> {
        val apiKey = getGroqApiKey()
        return mapOf(
            "api_key_configured" to if (apiKey.isEmpty()) "No" else "Yes (${apiKey.take(8)}...)",
            "volume_gain" to getVolumeGain().toString(),
            "silence_timeout" to "${getSilenceTimeout()}ms"
        )
    }
}

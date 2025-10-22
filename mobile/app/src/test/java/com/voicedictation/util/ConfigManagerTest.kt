package com.voicedictation.util

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Unit tests for ConfigManager
 * Uses Robolectric for Android context
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [28])
class ConfigManagerTest {

    private lateinit var context: Context
    private lateinit var configManager: ConfigManager

    @Before
    fun setup() {
        context = ApplicationProvider.getApplicationContext()
        configManager = ConfigManager(context)
        configManager.clear() // Start with clean state
    }

    @Test
    fun `isConfigured returns false when no API key set`() {
        assertFalse(configManager.isConfigured())
    }

    @Test
    fun `isConfigured returns true after setting API key`() {
        configManager.setGroqApiKey("test_key_123")
        assertTrue(configManager.isConfigured())
    }

    @Test
    fun `API key is persisted`() {
        val testKey = "test_api_key_456"
        configManager.setGroqApiKey(testKey)

        // Create new instance to verify persistence
        val newConfigManager = ConfigManager(context)
        assertEquals(testKey, newConfigManager.getGroqApiKey())
    }

    @Test
    fun `volume gain defaults to 1_0`() {
        assertEquals(1.0f, configManager.getVolumeGain(), 0.01f)
    }

    @Test
    fun `volume gain is persisted`() {
        configManager.setVolumeGain(2.5f)

        val newConfigManager = ConfigManager(context)
        assertEquals(2.5f, newConfigManager.getVolumeGain(), 0.01f)
    }

    @Test
    fun `silence timeout defaults to 60000ms`() {
        assertEquals(60000L, configManager.getSilenceTimeout())
    }

    @Test
    fun `silence timeout is persisted`() {
        configManager.setSilenceTimeout(30000L)

        val newConfigManager = ConfigManager(context)
        assertEquals(30000L, newConfigManager.getSilenceTimeout())
    }

    @Test
    fun `clear removes all configuration`() {
        configManager.setGroqApiKey("test_key")
        configManager.setVolumeGain(3.0f)
        configManager.setSilenceTimeout(45000L)

        configManager.clear()

        assertFalse(configManager.isConfigured())
        assertEquals(1.0f, configManager.getVolumeGain(), 0.01f)
        assertEquals(60000L, configManager.getSilenceTimeout())
    }

    @Test
    fun `debug info masks API key`() {
        configManager.setGroqApiKey("secret_key_very_long_1234567890")

        val debugInfo = configManager.getDebugInfo()
        val apiKeyInfo = debugInfo["api_key_configured"] ?: ""

        assertTrue(apiKeyInfo.contains("Yes"))
        assertFalse(apiKeyInfo.contains("secret_key_very_long"))
        assertTrue(apiKeyInfo.contains("...")) // Masked
    }
}

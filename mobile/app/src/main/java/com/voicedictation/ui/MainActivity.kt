package com.voicedictation.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.android.material.textfield.TextInputEditText
import com.voicedictation.R
import com.voicedictation.service.AudioRecorder
import com.voicedictation.service.VoiceAccessibilityService
import com.voicedictation.util.ConfigManager
import com.voicedictation.util.TextProcessor
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import timber.log.Timber
import kotlin.math.abs

/**
 * Main Settings Activity
 *
 * Features:
 * - Accessibility service status and enable button
 * - API key configuration
 * - Test API connection
 * - Test microphone (5 second recording)
 * - Save configuration
 */
class MainActivity : AppCompatActivity() {

    companion object {
        private const val REQUEST_MICROPHONE_PERMISSION = 1001
        private const val MICROPHONE_TEST_DURATION_MS = 5000L
    }

    private lateinit var configManager: ConfigManager
    private val activityScope = CoroutineScope(Dispatchers.Main + Job())

    // UI components
    private lateinit var serviceStatusText: TextView
    private lateinit var openAccessibilitySettingsButton: Button
    private lateinit var apiKeyInput: TextInputEditText
    private lateinit var testApiButton: Button
    private lateinit var testMicrophoneButton: Button
    private lateinit var audioTestResult: TextView
    private lateinit var saveButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        Timber.plant(Timber.DebugTree())

        configManager = ConfigManager(this)

        initViews()
        loadConfiguration()
        updateServiceStatus()
        setupListeners()

        // Request microphone permission if not granted
        if (!hasMicrophonePermission()) {
            requestMicrophonePermission()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        activityScope.cancel()
    }

    override fun onResume() {
        super.onResume()
        updateServiceStatus()
    }

    private fun initViews() {
        serviceStatusText = findViewById(R.id.service_status_text)
        openAccessibilitySettingsButton = findViewById(R.id.open_accessibility_settings_button)
        apiKeyInput = findViewById(R.id.api_key_input)
        testApiButton = findViewById(R.id.test_api_button)
        testMicrophoneButton = findViewById(R.id.test_microphone_button)
        audioTestResult = findViewById(R.id.audio_test_result)
        saveButton = findViewById(R.id.save_button)
    }

    private fun loadConfiguration() {
        apiKeyInput.setText(configManager.getGroqApiKey())
    }

    private fun setupListeners() {
        openAccessibilitySettingsButton.setOnClickListener {
            openAccessibilitySettings()
        }

        testApiButton.setOnClickListener {
            testApiConnection()
        }

        testMicrophoneButton.setOnClickListener {
            testMicrophone()
        }

        saveButton.setOnClickListener {
            saveConfiguration()
        }
    }

    /**
     * Update accessibility service status display
     */
    private fun updateServiceStatus() {
        val isEnabled = VoiceAccessibilityService.isServiceRunning()
        if (isEnabled) {
            serviceStatusText.text = "Enabled ✓"
            serviceStatusText.setTextColor(ContextCompat.getColor(this, R.color.green))
            openAccessibilitySettingsButton.text = "Open Settings"
        } else {
            serviceStatusText.text = "Not enabled"
            serviceStatusText.setTextColor(ContextCompat.getColor(this, R.color.red))
            openAccessibilitySettingsButton.text = "Enable Service"
        }
    }

    /**
     * Open accessibility settings to enable service
     */
    private fun openAccessibilitySettings() {
        try {
            val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            startActivity(intent)
            Toast.makeText(this, "Enable Voice Dictation service", Toast.LENGTH_LONG).show()
        } catch (e: Exception) {
            Timber.e(e, "Failed to open accessibility settings")
            Toast.makeText(this, "Failed to open settings", Toast.LENGTH_SHORT).show()
        }
    }

    /**
     * Test API connection with saved key
     */
    private fun testApiConnection() {
        val apiKey = apiKeyInput.text?.toString()?.trim() ?: ""
        if (apiKey.isEmpty()) {
            Toast.makeText(this, "Please enter API key first", Toast.LENGTH_SHORT).show()
            return
        }

        // Temporarily save API key for testing
        configManager.setGroqApiKey(apiKey)

        testApiButton.isEnabled = false
        testApiButton.text = "Testing..."

        activityScope.launch {
            try {
                val textProcessor = TextProcessor(configManager)
                val result = textProcessor.testPipeline()

                if (result.isSuccess) {
                    Toast.makeText(this@MainActivity, "API connection successful!", Toast.LENGTH_SHORT).show()
                } else {
                    val error = result.exceptionOrNull()?.message ?: "Unknown error"
                    Toast.makeText(this@MainActivity, "API test failed: $error", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                Timber.e(e, "API test error")
                Toast.makeText(this@MainActivity, "API test error: ${e.message}", Toast.LENGTH_LONG).show()
            } finally {
                testApiButton.isEnabled = true
                testApiButton.text = getString(R.string.test_transcription)
            }
        }
    }

    /**
     * Test microphone - record 5 seconds and show audio levels
     */
    private fun testMicrophone() {
        if (!hasMicrophonePermission()) {
            requestMicrophonePermission()
            return
        }

        testMicrophoneButton.isEnabled = false
        testMicrophoneButton.text = "Recording..."
        audioTestResult.visibility = View.VISIBLE
        audioTestResult.text = "Recording for 5 seconds..."

        activityScope.launch {
            try {
                val audioRecorder = AudioRecorder()

                // Start recording
                withContext(Dispatchers.IO) {
                    audioRecorder.startRecording()
                }

                // Wait 5 seconds
                delay(MICROPHONE_TEST_DURATION_MS)

                // Stop recording
                val audioData = withContext(Dispatchers.IO) {
                    audioRecorder.stopRecording()
                }

                // Analyze audio levels
                val analysis = analyzeAudio(audioData)
                audioTestResult.text = """
                    Test complete!
                    Audio size: ${audioData.size} bytes
                    Average level: ${analysis.avgLevel}
                    Peak level: ${analysis.peakLevel}
                    ${if (analysis.avgLevel < 500) "⚠️ Low audio level - speak louder or move closer to mic" else "✓ Audio levels good"}
                """.trimIndent()

                Toast.makeText(this@MainActivity, "Microphone test complete", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                Timber.e(e, "Microphone test failed")
                audioTestResult.text = "Test failed: ${e.message}"
                Toast.makeText(this@MainActivity, "Microphone test failed", Toast.LENGTH_SHORT).show()
            } finally {
                testMicrophoneButton.isEnabled = true
                testMicrophoneButton.text = getString(R.string.test_microphone)
            }
        }
    }

    /**
     * Analyze audio data to get levels
     */
    private suspend fun analyzeAudio(audioData: ByteArray): AudioAnalysis = withContext(Dispatchers.Default) {
        // Skip WAV header (44 bytes)
        val pcmData = audioData.drop(44)

        var sum = 0L
        var peak = 0

        // Process as 16-bit samples (little-endian)
        for (i in pcmData.indices step 2) {
            if (i + 1 < pcmData.size) {
                val sample = ((pcmData[i + 1].toInt() shl 8) or (pcmData[i].toInt() and 0xFF)).toShort()
                val level = abs(sample.toInt())
                sum += level
                if (level > peak) peak = level
            }
        }

        val numSamples = pcmData.size / 2
        val avgLevel = if (numSamples > 0) (sum / numSamples).toInt() else 0

        AudioAnalysis(avgLevel, peak)
    }

    /**
     * Save configuration
     */
    private fun saveConfiguration() {
        val apiKey = apiKeyInput.text?.toString()?.trim() ?: ""

        if (apiKey.isEmpty()) {
            Toast.makeText(this, "Please enter API key", Toast.LENGTH_SHORT).show()
            return
        }

        configManager.setGroqApiKey(apiKey)
        Toast.makeText(this, "Configuration saved", Toast.LENGTH_SHORT).show()

        Timber.d("Configuration saved: ${configManager.getDebugInfo()}")
    }

    /**
     * Check microphone permission
     */
    private fun hasMicrophonePermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.RECORD_AUDIO
        ) == PackageManager.PERMISSION_GRANTED
    }

    /**
     * Request microphone permission
     */
    private fun requestMicrophonePermission() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(Manifest.permission.RECORD_AUDIO),
            REQUEST_MICROPHONE_PERMISSION
        )
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            REQUEST_MICROPHONE_PERMISSION -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this, "Microphone permission granted", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "Microphone permission required for voice dictation", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private data class AudioAnalysis(val avgLevel: Int, val peakLevel: Int)
}

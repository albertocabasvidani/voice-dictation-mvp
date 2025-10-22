package com.voicedictation.service

import android.accessibilityservice.AccessibilityService
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Build
import android.view.KeyEvent
import android.view.accessibility.AccessibilityEvent
import androidx.core.app.NotificationCompat
import com.voicedictation.R
import com.voicedictation.util.ConfigManager
import com.voicedictation.util.TextProcessor
import kotlinx.coroutines.*
import timber.log.Timber

/**
 * Accessibility service that handles voice dictation triggered by volume key gesture.
 *
 * Workflow:
 * 1. User presses Volume Up + Volume Down simultaneously
 * 2. Service starts audio recording
 * 3. User releases keys to stop recording
 * 4. Audio is transcribed via Groq Whisper
 * 5. Text is processed via Groq LLM
 * 6. Result is copied to clipboard and auto-pasted
 */
class VoiceAccessibilityService : AccessibilityService() {

    private lateinit var audioRecorder: AudioRecorder
    private lateinit var textProcessor: TextProcessor
    private lateinit var configManager: ConfigManager
    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    // Gesture detection state
    private var volumeUpPressed = false
    private var volumeDownPressed = false
    private var isRecording = false
    private var recordingJob: Job? = null

    companion object {
        private const val NOTIFICATION_ID = 1
        private const val CHANNEL_ID = "voice_dictation_channel"
        private const val CHANNEL_NAME = "Voice Dictation Service"

        // Singleton instance for checking service state
        @Volatile
        private var instance: VoiceAccessibilityService? = null

        fun isServiceRunning(): Boolean = instance != null
    }

    override fun onCreate() {
        super.onCreate()
        Timber.plant(Timber.DebugTree())
        Timber.d("VoiceAccessibilityService created")

        instance = this

        // Initialize components
        configManager = ConfigManager(this)
        audioRecorder = AudioRecorder()
        textProcessor = TextProcessor(configManager)

        // Start foreground service
        startForeground(NOTIFICATION_ID, createNotification("Service running"))
    }

    override fun onDestroy() {
        super.onDestroy()
        Timber.d("VoiceAccessibilityService destroyed")

        instance = null

        // Cleanup
        recordingJob?.cancel()
        serviceScope.cancel()
        audioRecorder.release()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // We handle key events in onKeyEvent instead
    }

    override fun onInterrupt() {
        Timber.w("Service interrupted")
        stopRecording()
    }

    override fun onKeyEvent(event: KeyEvent): Boolean {
        // Intercept volume key combinations for gesture trigger
        when (event.keyCode) {
            KeyEvent.KEYCODE_VOLUME_UP -> {
                handleVolumeKey(isUp = true, isPressed = event.action == KeyEvent.ACTION_DOWN)
                return true // Consume event to prevent volume change
            }
            KeyEvent.KEYCODE_VOLUME_DOWN -> {
                handleVolumeKey(isUp = false, isPressed = event.action == KeyEvent.ACTION_DOWN)
                return true // Consume event to prevent volume change
            }
        }
        return super.onKeyEvent(event)
    }

    /**
     * Handle volume key press/release for gesture detection.
     * Gesture: Volume Up + Volume Down pressed simultaneously starts recording
     */
    private fun handleVolumeKey(isUp: Boolean, isPressed: Boolean) {
        if (isUp) {
            volumeUpPressed = isPressed
        } else {
            volumeDownPressed = isPressed
        }

        // Check if both volume keys are pressed (gesture detected)
        val bothPressed = volumeUpPressed && volumeDownPressed

        if (bothPressed && !isRecording) {
            // Start recording when both keys pressed
            Timber.d("Gesture detected: Starting recording")
            startRecording()
        } else if (!bothPressed && isRecording) {
            // Stop recording when either key released
            Timber.d("Gesture released: Stopping recording")
            stopRecording()
        }
    }

    /**
     * Start audio recording
     */
    private fun startRecording() {
        if (isRecording) {
            Timber.w("Already recording, ignoring")
            return
        }

        // Check API key configured
        if (configManager.getGroqApiKey().isEmpty()) {
            Timber.e("No API key configured")
            showToast(getString(R.string.error_no_api_key))
            return
        }

        isRecording = true
        updateNotification("Recording...")

        // Start recording in background
        recordingJob = serviceScope.launch {
            try {
                audioRecorder.startRecording()
                Timber.d("Recording started")
            } catch (e: Exception) {
                Timber.e(e, "Failed to start recording")
                showToast(getString(R.string.error_microphone_permission))
                isRecording = false
                updateNotification("Service running")
            }
        }
    }

    /**
     * Stop recording and process audio
     */
    private fun stopRecording() {
        if (!isRecording) {
            Timber.w("Not recording, ignoring")
            return
        }

        isRecording = false
        recordingJob?.cancel()
        updateNotification("Processing...")

        serviceScope.launch {
            try {
                // Stop recording and get audio data
                val audioData = audioRecorder.stopRecording()

                if (audioData.isEmpty()) {
                    Timber.w("No audio data recorded")
                    updateNotification("Service running")
                    return@launch
                }

                Timber.d("Audio recorded: ${audioData.size} bytes")

                // Process audio through pipeline
                updateNotification("Transcribing...")
                val result = textProcessor.processAudio(audioData)

                if (result.isSuccess) {
                    val text = result.getOrNull() ?: ""
                    Timber.d("Processing complete: $text")

                    // Copy to clipboard
                    copyToClipboard(text)

                    // Auto-paste
                    performGlobalAction(GLOBAL_ACTION_PASTE)

                    updateNotification("Done!")

                    // Reset notification after 2 seconds
                    delay(2000)
                    updateNotification("Service running")
                } else {
                    val error = result.exceptionOrNull()
                    Timber.e(error, "Processing failed")
                    showToast(getString(R.string.error_processing_failed))
                    updateNotification("Error")
                    delay(2000)
                    updateNotification("Service running")
                }
            } catch (e: Exception) {
                Timber.e(e, "Error in stopRecording")
                showToast(getString(R.string.error_processing_failed))
                updateNotification("Service running")
            }
        }
    }

    /**
     * Copy text to system clipboard
     */
    private fun copyToClipboard(text: String) {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = ClipData.newPlainText("Voice Dictation", text)
        clipboard.setPrimaryClip(clip)
        Timber.d("Copied to clipboard: $text")
    }

    /**
     * Show toast message (must be called from main thread)
     */
    private fun showToast(message: String) {
        serviceScope.launch(Dispatchers.Main) {
            android.widget.Toast.makeText(this@VoiceAccessibilityService, message, android.widget.Toast.LENGTH_SHORT).show()
        }
    }

    /**
     * Create notification channel (required for Android O+)
     */
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Voice dictation service status"
                setShowBadge(false)
            }

            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    /**
     * Create notification for foreground service
     */
    private fun createNotification(text: String): Notification {
        createNotificationChannel()

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.app_name))
            .setContentText(text)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()
    }

    /**
     * Update foreground notification
     */
    private fun updateNotification(text: String) {
        val notification = createNotification(text)
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIFICATION_ID, notification)
    }
}

package com.voicedictation.service

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import timber.log.Timber
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.abs

/**
 * Audio recorder with silence detection and WAV encoding.
 *
 * Features:
 * - 16kHz sample rate, mono, 16-bit PCM
 * - Continuous recording with silence detection
 * - Auto-stop after 60 seconds of silence
 * - WAV file format output
 */
class AudioRecorder {

    companion object {
        private const val SAMPLE_RATE = 16000
        private const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        private const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
        private const val BUFFER_SIZE_MULTIPLIER = 2
        private const val SILENCE_THRESHOLD = 300
        private const val SILENCE_TIMEOUT_MS = 60000L // 60 seconds
    }

    private var audioRecord: AudioRecord? = null
    private var recordingThread: Thread? = null
    private val audioBuffer = ByteArrayOutputStream()
    private var isRecording = false
    private var lastAudioTime = 0L

    /**
     * Start audio recording
     */
    @Synchronized
    fun startRecording() {
        if (isRecording) {
            Timber.w("Already recording")
            return
        }

        // Calculate buffer size
        val minBufferSize = AudioRecord.getMinBufferSize(
            SAMPLE_RATE,
            CHANNEL_CONFIG,
            AUDIO_FORMAT
        )

        if (minBufferSize == AudioRecord.ERROR || minBufferSize == AudioRecord.ERROR_BAD_VALUE) {
            throw IllegalStateException("Invalid audio configuration")
        }

        val bufferSize = minBufferSize * BUFFER_SIZE_MULTIPLIER

        // Create AudioRecord instance
        audioRecord = AudioRecord(
            MediaRecorder.AudioSource.MIC,
            SAMPLE_RATE,
            CHANNEL_CONFIG,
            AUDIO_FORMAT,
            bufferSize
        )

        if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
            throw IllegalStateException("AudioRecord not initialized")
        }

        // Reset state
        audioBuffer.reset()
        isRecording = true
        lastAudioTime = System.currentTimeMillis()

        // Start recording
        audioRecord?.startRecording()
        Timber.d("AudioRecord started")

        // Start recording thread
        recordingThread = Thread {
            recordAudio(bufferSize)
        }.apply {
            priority = Thread.MAX_PRIORITY
            start()
        }
    }

    /**
     * Stop recording and return audio data as WAV bytes
     */
    @Synchronized
    fun stopRecording(): ByteArray {
        if (!isRecording) {
            Timber.w("Not recording")
            return ByteArray(0)
        }

        isRecording = false

        // Wait for recording thread to finish
        recordingThread?.join(1000)
        recordingThread = null

        // Stop AudioRecord
        audioRecord?.apply {
            stop()
            release()
        }
        audioRecord = null

        // Get raw PCM data
        val pcmData = audioBuffer.toByteArray()
        Timber.d("Recorded ${pcmData.size} bytes of PCM data")

        // Encode as WAV
        return encodeWav(pcmData)
    }

    /**
     * Release resources
     */
    fun release() {
        stopRecording()
    }

    /**
     * Get silence duration in milliseconds
     */
    fun getSilenceDuration(): Long {
        return if (isRecording) {
            System.currentTimeMillis() - lastAudioTime
        } else {
            0L
        }
    }

    /**
     * Recording loop - reads audio data and detects silence
     */
    private fun recordAudio(bufferSize: Int) {
        val buffer = ShortArray(bufferSize / 2) // 16-bit samples

        Timber.d("Recording thread started")

        while (isRecording) {
            // Read audio data
            val readSize = audioRecord?.read(buffer, 0, buffer.size) ?: 0

            if (readSize > 0) {
                // Calculate audio level (RMS)
                val audioLevel = calculateAudioLevel(buffer, readSize)

                // Check for silence
                if (audioLevel > SILENCE_THRESHOLD) {
                    lastAudioTime = System.currentTimeMillis()
                }

                // Check silence timeout
                if (getSilenceDuration() > SILENCE_TIMEOUT_MS) {
                    Timber.d("Silence timeout reached, stopping recording")
                    isRecording = false
                    break
                }

                // Write to buffer (convert shorts to bytes)
                val bytes = shortArrayToByteArray(buffer, readSize)
                audioBuffer.write(bytes, 0, bytes.size)
            } else if (readSize < 0) {
                Timber.e("AudioRecord read error: $readSize")
                break
            }
        }

        Timber.d("Recording thread finished")
    }

    /**
     * Calculate audio level (RMS) from sample buffer
     */
    private fun calculateAudioLevel(buffer: ShortArray, size: Int): Int {
        var sum = 0L
        for (i in 0 until size) {
            sum += abs(buffer[i].toInt())
        }
        return (sum / size).toInt()
    }

    /**
     * Convert short array to byte array (little-endian)
     */
    private fun shortArrayToByteArray(shorts: ShortArray, size: Int): ByteArray {
        val bytes = ByteArray(size * 2)
        val buffer = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
        for (i in 0 until size) {
            buffer.putShort(shorts[i])
        }
        return bytes
    }

    /**
     * Encode PCM data as WAV file format
     */
    private fun encodeWav(pcmData: ByteArray): ByteArray {
        val channels = 1 // mono
        val bitsPerSample = 16
        val byteRate = SAMPLE_RATE * channels * bitsPerSample / 8
        val blockAlign = channels * bitsPerSample / 8

        val wavSize = 44 + pcmData.size
        val buffer = ByteBuffer.allocate(wavSize).order(ByteOrder.LITTLE_ENDIAN)

        // RIFF header
        buffer.put("RIFF".toByteArray())
        buffer.putInt(wavSize - 8)
        buffer.put("WAVE".toByteArray())

        // fmt chunk
        buffer.put("fmt ".toByteArray())
        buffer.putInt(16) // chunk size
        buffer.putShort(1.toShort()) // audio format (PCM)
        buffer.putShort(channels.toShort())
        buffer.putInt(SAMPLE_RATE)
        buffer.putInt(byteRate)
        buffer.putShort(blockAlign.toShort())
        buffer.putShort(bitsPerSample.toShort())

        // data chunk
        buffer.put("data".toByteArray())
        buffer.putInt(pcmData.size)
        buffer.put(pcmData)

        return buffer.array()
    }
}

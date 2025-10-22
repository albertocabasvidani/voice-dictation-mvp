package com.voicedictation.util

import com.voicedictation.provider.GroqLLMClient
import com.voicedictation.provider.GroqWhisperClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import timber.log.Timber

/**
 * Orchestrates the audio processing pipeline:
 * Audio bytes → Groq Whisper (transcription) → Groq LLM (formatting) → Formatted text
 *
 * This is the main coordinator between audio recording and text output.
 */
class TextProcessor(private val configManager: ConfigManager) {

    /**
     * Process audio data through the complete pipeline
     *
     * @param audioData WAV audio bytes
     * @return Result with formatted text or error
     */
    suspend fun processAudio(audioData: ByteArray): Result<String> = withContext(Dispatchers.IO) {
        try {
            val apiKey = configManager.getGroqApiKey()
            if (apiKey.isEmpty()) {
                return@withContext Result.failure(Exception("No API key configured"))
            }

            Timber.d("Starting audio processing pipeline")
            val totalStartTime = System.currentTimeMillis()

            // Step 1: Transcribe audio
            val whisperClient = GroqWhisperClient(apiKey)
            val transcriptionResult = whisperClient.transcribe(audioData)

            if (transcriptionResult.isFailure) {
                Timber.e("Transcription failed: ${transcriptionResult.exceptionOrNull()}")
                return@withContext Result.failure(
                    transcriptionResult.exceptionOrNull() ?: Exception("Transcription failed")
                )
            }

            val rawText = transcriptionResult.getOrNull() ?: ""
            Timber.d("Transcription result: $rawText")

            if (rawText.isBlank()) {
                Timber.w("Empty transcription")
                return@withContext Result.success("")
            }

            // Step 2: Format with LLM
            val llmClient = GroqLLMClient(apiKey)
            val formattedResult = llmClient.process(rawText)

            if (formattedResult.isFailure) {
                Timber.w("LLM processing failed, using raw transcription")
                // Fallback to raw transcription if LLM fails
                return@withContext Result.success(rawText)
            }

            val formattedText = formattedResult.getOrNull() ?: rawText
            Timber.d("Formatted result: $formattedText")

            val totalLatency = System.currentTimeMillis() - totalStartTime
            Timber.d("Pipeline complete in ${totalLatency}ms")

            Result.success(formattedText)
        } catch (e: Exception) {
            Timber.e(e, "Pipeline error")
            Result.failure(e)
        }
    }

    /**
     * Test the complete pipeline with minimal audio
     *
     * @return Result with success/failure status
     */
    suspend fun testPipeline(): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val apiKey = configManager.getGroqApiKey()
            if (apiKey.isEmpty()) {
                return@withContext Result.failure(Exception("No API key configured"))
            }

            // Test transcription
            val whisperClient = GroqWhisperClient(apiKey)
            val transcriptionTest = whisperClient.testConnection()

            if (transcriptionTest.isFailure) {
                return@withContext Result.failure(Exception("Transcription test failed"))
            }

            // Test LLM
            val llmClient = GroqLLMClient(apiKey)
            val llmTest = llmClient.testConnection()

            if (llmTest.isFailure) {
                return@withContext Result.failure(Exception("LLM test failed"))
            }

            Result.success(true)
        } catch (e: Exception) {
            Timber.e(e, "Pipeline test failed")
            Result.failure(e)
        }
    }
}

package com.voicedictation.provider

import com.google.gson.annotations.SerializedName
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Header
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import timber.log.Timber
import java.io.File
import java.util.concurrent.TimeUnit

/**
 * Groq Whisper API client for audio transcription.
 *
 * API: https://api.groq.com/openai/v1/audio/transcriptions
 * Model: whisper-large-v3
 * Speed: <1s latency (typical)
 * Cost: Free tier available
 */
class GroqWhisperClient(private val apiKey: String) {

    companion object {
        private const val BASE_URL = "https://api.groq.com/"
        private const val MODEL = "whisper-large-v3"
        private const val TIMEOUT_SECONDS = 30L
    }

    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .writeTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        })
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    private val api = retrofit.create(GroqWhisperApi::class.java)

    /**
     * Transcribe audio bytes to text
     */
    suspend fun transcribe(audioData: ByteArray): Result<String> = withContext(Dispatchers.IO) {
        try {
            Timber.d("Transcribing ${audioData.size} bytes with Groq Whisper")
            val startTime = System.currentTimeMillis()

            // Create temporary file for multipart upload
            val tempFile = File.createTempFile("audio", ".wav")
            try {
                tempFile.writeBytes(audioData)

                // Create multipart request
                val requestBody = tempFile.asRequestBody("audio/wav".toMediaType())
                val audioPart = MultipartBody.Part.createFormData("file", "audio.wav", requestBody)
                val modelPart = MultipartBody.Part.createFormData("model", MODEL)

                // Make API call
                val response = api.transcribe(
                    authorization = "Bearer $apiKey",
                    file = audioPart,
                    model = modelPart
                )

                val latency = System.currentTimeMillis() - startTime

                if (response.isSuccessful) {
                    val text = response.body()?.text ?: ""
                    Timber.d("Transcription success (${latency}ms): $text")
                    Result.success(text)
                } else {
                    val error = "Groq API error: ${response.code()} - ${response.errorBody()?.string()}"
                    Timber.e(error)
                    Result.failure(Exception(error))
                }
            } finally {
                // Cleanup temp file
                tempFile.delete()
            }
        } catch (e: Exception) {
            Timber.e(e, "Transcription failed")
            Result.failure(e)
        }
    }

    /**
     * Test API key validity
     */
    suspend fun testConnection(): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            // Create minimal test audio (1 second of silence)
            val testAudio = createTestAudio()
            val result = transcribe(testAudio)
            Result.success(result.isSuccess)
        } catch (e: Exception) {
            Timber.e(e, "Connection test failed")
            Result.failure(e)
        }
    }

    /**
     * Create minimal test audio (WAV format, 1 second of silence)
     */
    private fun createTestAudio(): ByteArray {
        val sampleRate = 16000
        val duration = 1 // seconds
        val dataSize = sampleRate * duration * 2 // 16-bit = 2 bytes per sample

        val wavSize = 44 + dataSize
        val buffer = ByteArray(wavSize)

        // WAV header (44 bytes)
        var offset = 0

        // RIFF header
        "RIFF".toByteArray().copyInto(buffer, offset); offset += 4
        writeInt(buffer, offset, wavSize - 8); offset += 4
        "WAVE".toByteArray().copyInto(buffer, offset); offset += 4

        // fmt chunk
        "fmt ".toByteArray().copyInto(buffer, offset); offset += 4
        writeInt(buffer, offset, 16); offset += 4 // chunk size
        writeShort(buffer, offset, 1); offset += 2 // audio format (PCM)
        writeShort(buffer, offset, 1); offset += 2 // channels (mono)
        writeInt(buffer, offset, sampleRate); offset += 4
        writeInt(buffer, offset, sampleRate * 2); offset += 4 // byte rate
        writeShort(buffer, offset, 2); offset += 2 // block align
        writeShort(buffer, offset, 16); offset += 2 // bits per sample

        // data chunk
        "data".toByteArray().copyInto(buffer, offset); offset += 4
        writeInt(buffer, offset, dataSize); offset += 4

        // Audio data (silence = zeros)
        // Already initialized to 0

        return buffer
    }

    private fun writeInt(buffer: ByteArray, offset: Int, value: Int) {
        buffer[offset] = (value and 0xFF).toByte()
        buffer[offset + 1] = ((value shr 8) and 0xFF).toByte()
        buffer[offset + 2] = ((value shr 16) and 0xFF).toByte()
        buffer[offset + 3] = ((value shr 24) and 0xFF).toByte()
    }

    private fun writeShort(buffer: ByteArray, offset: Int, value: Int) {
        buffer[offset] = (value and 0xFF).toByte()
        buffer[offset + 1] = ((value shr 8) and 0xFF).toByte()
    }
}

/**
 * Groq Whisper API interface
 */
private interface GroqWhisperApi {
    @Multipart
    @POST("openai/v1/audio/transcriptions")
    suspend fun transcribe(
        @Header("Authorization") authorization: String,
        @Part file: MultipartBody.Part,
        @Part model: MultipartBody.Part
    ): Response<TranscriptionResponse>
}

/**
 * API response model
 */
private data class TranscriptionResponse(
    @SerializedName("text") val text: String
)

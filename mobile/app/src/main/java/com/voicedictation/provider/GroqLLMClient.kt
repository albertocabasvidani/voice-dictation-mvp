package com.voicedictation.provider

import com.google.gson.annotations.SerializedName
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST
import timber.log.Timber
import java.util.concurrent.TimeUnit

/**
 * Groq LLM API client for text post-processing.
 *
 * API: https://api.groq.com/openai/v1/chat/completions
 * Model: llama-3.1-8b-instant (fast, free tier)
 * Purpose: Clean transcriptions, add punctuation, format structure
 */
class GroqLLMClient(private val apiKey: String) {

    companion object {
        private const val BASE_URL = "https://api.groq.com/"
        private const val MODEL = "llama-3.1-8b-instant"
        private const val TIMEOUT_SECONDS = 30L

        /**
         * System prompt for text formatting (same as Windows version)
         */
        private const val SYSTEM_PROMPT = """You are a text formatter. Clean up speech transcriptions by:

BASIC FORMATTING:
- Removing filler words (um, uh, eh, allora, cioè, tipo)
- Adding proper punctuation (periods, commas, question marks)
- Fixing capitalization
- Resolving self-corrections (e.g., "tomorrow, no Friday" → "Friday")

STRUCTURE RECOGNITION (only when obvious):
- **Lists**: When the user says phrases like "first", "second", "next", "also", "another", "punto uno", "punto due", or lists items, format as:
  • Bullet points for unordered items
  • Numbered list (1., 2., 3.) for sequential items
- **Paragraphs**: Add line breaks between distinct topics or logical sections
- **Code**: When the user mentions code, programming, or uses technical terms like "function", "class", "variable", format it in backticks or code blocks
- **Titles/Headings**: When the user explicitly says "title", "heading", "titolo", or emphasizes a section name, put it in quotes

EXAMPLES:
Input: "first point is the API then second the database and third the frontend"
Output: 1. API
2. Database
3. Frontend

Input: "reminder buy milk eggs and bread"
Output: Reminder:
• Buy milk
• Eggs
• Bread

Input: "ho fatto un test e funziona"
Output: Ho fatto un test e funziona.

CRITICAL: Return ONLY the user's words, cleaned and formatted. NEVER add notes, explanations, comments, or meta-text like "Nota:" or "Note:". If there's nothing to format structurally, just clean the text. DO NOT add any text that the user did not say."""
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

    private val api = retrofit.create(GroqLLMApi::class.java)

    /**
     * Process transcribed text through LLM
     */
    suspend fun process(text: String): Result<String> = withContext(Dispatchers.IO) {
        try {
            Timber.d("Processing text with Groq LLM: $text")
            val startTime = System.currentTimeMillis()

            // Create chat completion request
            val request = ChatCompletionRequest(
                model = MODEL,
                messages = listOf(
                    Message(role = "system", content = SYSTEM_PROMPT),
                    Message(role = "user", content = text)
                ),
                temperature = 0.3, // Lower temperature for more consistent formatting
                maxTokens = 1000
            )

            // Make API call
            val response = api.createChatCompletion(
                authorization = "Bearer $apiKey",
                request = request
            )

            val latency = System.currentTimeMillis() - startTime

            if (response.isSuccessful) {
                val processedText = response.body()?.choices?.firstOrNull()?.message?.content ?: text
                Timber.d("LLM processing success (${latency}ms): $processedText")
                Result.success(processedText)
            } else {
                val error = "Groq API error: ${response.code()} - ${response.errorBody()?.string()}"
                Timber.e(error)
                // Fallback to original text on error
                Result.success(text)
            }
        } catch (e: Exception) {
            Timber.e(e, "LLM processing failed, returning original text")
            // Fallback to original text on error
            Result.success(text)
        }
    }

    /**
     * Test API key validity
     */
    suspend fun testConnection(): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val result = process("test")
            Result.success(result.isSuccess)
        } catch (e: Exception) {
            Timber.e(e, "Connection test failed")
            Result.failure(e)
        }
    }
}

/**
 * Groq LLM API interface
 */
private interface GroqLLMApi {
    @POST("openai/v1/chat/completions")
    suspend fun createChatCompletion(
        @Header("Authorization") authorization: String,
        @Body request: ChatCompletionRequest
    ): Response<ChatCompletionResponse>
}

/**
 * Request/Response models
 */
private data class ChatCompletionRequest(
    @SerializedName("model") val model: String,
    @SerializedName("messages") val messages: List<Message>,
    @SerializedName("temperature") val temperature: Double = 0.3,
    @SerializedName("max_tokens") val maxTokens: Int = 1000
)

private data class Message(
    @SerializedName("role") val role: String,
    @SerializedName("content") val content: String
)

private data class ChatCompletionResponse(
    @SerializedName("choices") val choices: List<Choice>
)

private data class Choice(
    @SerializedName("message") val message: Message
)

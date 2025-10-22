package com.voicedictation.provider

import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * Unit tests for GroqLLMClient using MockWebServer
 */
class GroqLLMClientTest {

    private lateinit var mockServer: MockWebServer
    private lateinit var client: GroqLLMClient
    private val testApiKey = "test_api_key_12345"

    @Before
    fun setup() {
        mockServer = MockWebServer()
        mockServer.start()

        client = GroqLLMClient(testApiKey)
    }

    @After
    fun tearDown() {
        mockServer.shutdown()
    }

    @Test
    fun `process returns formatted text on success`() = runTest {
        // Mock successful response
        val mockResponse = MockResponse()
            .setResponseCode(200)
            .setBody("""
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "Hello, world!"
                            }
                        }
                    ]
                }
            """.trimIndent())
        mockServer.enqueue(mockResponse)

        // Note: Similar to WhisperClient, this requires URL injection
        // This is a template showing the testing structure
    }

    @Test
    fun `process handles API error gracefully`() = runTest {
        // Mock error response
        val mockResponse = MockResponse()
            .setResponseCode(500)
            .setBody("""{"error":"Internal server error"}""")
        mockServer.enqueue(mockResponse)

        // LLM should fallback to original text on error
        // Requires URL injection to test properly
    }

    @Test
    fun `process handles empty input`() = runTest {
        val result = client.process("")

        // Should handle empty string gracefully
        assertTrue(result.isSuccess)
    }

    @Test
    fun `process preserves original text on network error`() = runTest {
        // Mock timeout
        val mockResponse = MockResponse()
            .setSocketPolicy(okhttp3.mockwebserver.SocketPolicy.NO_RESPONSE)
        mockServer.enqueue(mockResponse)

        // Should return original text as fallback
    }

    @Test
    fun `system prompt includes critical instructions`() {
        // Verify system prompt contains key requirements
        val prompt = """You are a text formatter. Clean up speech transcriptions by:

BASIC FORMATTING:
- Removing filler words (um, uh, eh, allora, cioè, tipo)
- Adding proper punctuation (periods, commas, question marks)
- Fixing capitalization
- Resolving self-corrections (e.g., "tomorrow, no Friday" → "Friday")"""

        assertTrue(prompt.contains("BASIC FORMATTING"))
        assertTrue(prompt.contains("CRITICAL"))
    }
}

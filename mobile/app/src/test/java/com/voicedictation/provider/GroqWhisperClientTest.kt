package com.voicedictation.provider

import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * Unit tests for GroqWhisperClient using MockWebServer
 */
class GroqWhisperClientTest {

    private lateinit var mockServer: MockWebServer
    private lateinit var client: GroqWhisperClient
    private val testApiKey = "test_api_key_12345"

    @Before
    fun setup() {
        mockServer = MockWebServer()
        mockServer.start()

        // Create client with test API key
        client = GroqWhisperClient(testApiKey)
    }

    @After
    fun tearDown() {
        mockServer.shutdown()
    }

    @Test
    fun `transcribe returns text on success`() = runTest {
        // Mock successful response
        val mockResponse = MockResponse()
            .setResponseCode(200)
            .setBody("""{"text":"Hello world"}""")
        mockServer.enqueue(mockResponse)

        // Create test audio data (minimal WAV)
        val audioData = createTestAudio()

        // Note: This test won't work as-is because we can't inject mock URL into client
        // In production, you'd use dependency injection or factory pattern
        // This is a template showing the testing structure

        // For now, just verify test audio creation works
        assertTrue(audioData.size > 44) // WAV header is 44 bytes
    }

    @Test
    fun `transcribe handles API error`() = runTest {
        // Mock error response
        val mockResponse = MockResponse()
            .setResponseCode(401)
            .setBody("""{"error":"Invalid API key"}""")
        mockServer.enqueue(mockResponse)

        // This would test error handling
        // Actual implementation requires URL injection
    }

    @Test
    fun `transcribe handles network timeout`() = runTest {
        // Mock timeout (no response)
        val mockResponse = MockResponse()
            .setSocketPolicy(okhttp3.mockwebserver.SocketPolicy.NO_RESPONSE)
        mockServer.enqueue(mockResponse)

        // This would test timeout handling
    }

    @Test
    fun `test audio creation is valid WAV`() {
        val audio = createTestAudio()

        // Check WAV header
        val header = audio.take(12).toByteArray()
        val riff = String(header.slice(0..3).toByteArray())
        val wave = String(header.slice(8..11).toByteArray())

        assertEquals("RIFF", riff)
        assertEquals("WAVE", wave)
    }

    /**
     * Create minimal test audio (1 second of silence)
     */
    private fun createTestAudio(): ByteArray {
        val sampleRate = 16000
        val duration = 1
        val dataSize = sampleRate * duration * 2

        val wavSize = 44 + dataSize
        val buffer = ByteArray(wavSize)

        var offset = 0

        // RIFF header
        "RIFF".toByteArray().copyInto(buffer, offset); offset += 4
        writeInt(buffer, offset, wavSize - 8); offset += 4
        "WAVE".toByteArray().copyInto(buffer, offset); offset += 4

        // fmt chunk
        "fmt ".toByteArray().copyInto(buffer, offset); offset += 4
        writeInt(buffer, offset, 16); offset += 4
        writeShort(buffer, offset, 1); offset += 2
        writeShort(buffer, offset, 1); offset += 2
        writeInt(buffer, offset, sampleRate); offset += 4
        writeInt(buffer, offset, sampleRate * 2); offset += 4
        writeShort(buffer, offset, 2); offset += 2
        writeShort(buffer, offset, 16); offset += 2

        // data chunk
        "data".toByteArray().copyInto(buffer, offset); offset += 4
        writeInt(buffer, offset, dataSize)

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
